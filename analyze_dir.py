"""analyze directory"""
import os
import argparse
import chardet
import colorama
from termcolor import colored

PARSER = argparse.ArgumentParser()

SUBPARSER = PARSER.add_subparsers(help='commands', dest='command')

ANALYZE_PARSER = SUBPARSER.add_parser('analyze', help='analyze directory')

ANALYZE_PARSER.add_argument('directory',
                            nargs=1, help='which directory to be traversed')

ANALYZE_PARSER.add_argument('-s', '--suffix', action='store', dest='suffix',
                            default=None, help=
                            """which suffix to be traversed. type in '.html,.css'""")

ANALYZE_PARSER.add_argument('-i', '--ignore_directory', action='store', dest='ignore_directory',
                            default=None, help="""ignore director. type in 'dir1,dir1/dir2'""")

CONVERT_PARSER = SUBPARSER.add_parser('convert', help='convert file in directory')

CONVERT_PARSER.add_argument('directory',
                            nargs=1, help='which directory to be traversed')

CONVERT_PARSER.add_argument('-s', '--suffix', action='store', dest='suffix',
                            default=None, help=
                            """which suffix to be traversed. type in '.html,.css'""")

CONVERT_PARSER.add_argument('-i', '--ignore_directory', action='store', dest='ignore_directory',
                            default=None, help="""ignore director. type in 'dir1,dir1/dir2'""")

CONVERT_PARSER.add_argument('-f', '--from', action='store', dest='convert_from',
                            default='gb2312', help="""like 'gb2312','utf-8' default is gb2312""")

CONVERT_PARSER.add_argument('-t', '--to', action='store', dest='convert_to',
                            default='utf-8', help="""like 'gb2312','utf-8' default is utf-8""")


# TODO make -i like .gitignore
# only directory ok
# all directory and files
# Relative directory and files



class FileAttr():
    """(文件后缀,所有文件,各种属性统计)的集合"""

    def __init__(self, suffix, files):
        """后缀,文件列表"""
        self.suffix = suffix
        self.files = files
        self.file_numbers = len(self.files)
        self.newlines = {}
        self.encodings = {}
        self.size = 0
        self.lines = 0
        self.tab_or_space = {}
        self.need_judge = True if self.need_judge_text(self.suffix) else False
        self.need_convert = True if self.need_convert_text(self.suffix) else False

    def __str__(self):
        if self.need_judge:
            rtn_str = '{} {} newline: {} encoding: {} size: \
{} lines: {} tab_or_space: {}'.format(self.suffix,
                                      self.file_numbers,
                                      self.newlines,
                                      self.encodings,
                                      self.sizeof_fmt(self.size),
                                      self.lines,
                                      self.tab_or_space)
        else:
            rtn_str = '{} {}'.format(self.suffix, self.file_numbers)

        return rtn_str

    def __lt__(self, other):
        return self.file_numbers < other.file_numbers

    @staticmethod
    def need_judge_text(extension):
        """根据后缀名判断文件是否需要检查"""

        include_extensions = ['.py', '.html', '.js', '.css', '.conf',
                              '.txt', '.sh', '.pas', '.sql', '.sqc',
                              '.h', '.cpp', '.ini', '.H', '.txt',
                              '.sql', '.CPP', '.rb', '.c']

        if extension in include_extensions:
            return True

        return False

    @staticmethod
    def need_convert_text(extension):
        """根据后缀名判断文件是否需要转换"""
        return FileAttr.need_judge_text(extension)

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        """格式化文件大小字符串"""
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    @staticmethod
    def get_new_line(line):
        """获取换行符,line为bytes类型

        -> string 换行符

        """
        new_line_characters = [b'\r\n', b'\r', b'\n', b'']
        for character in new_line_characters:
            if line.endswith(character):
                return character.decode()

        return None

    @staticmethod
    def is_encoding_equal(from_encoding, bytes_encoding):
        """
        常见场景:
        1.utf-8,utf-bom -> gb2312
        2.gb2312 -> utf-8
        对于第一种情况判断时from_encoding为utf-8,utf-bom也算上
        """
        if from_encoding.lower() == 'utf-8':
            if bytes_encoding.lower() == 'utf-8' or \
                            bytes_encoding.lower() == 'utf-8-sig':
                return True

        if from_encoding.lower() == bytes_encoding.lower():
            return True

        return False

    def inspect_file(self):
        """检查所有文件属性
        1.encoding 2.newline 3.size 4.line 5.tab or space
        """
        if self.need_judge:
            for file in self.files:
                self.__inspect_encoding(file)
                self.__inspect_newline(file)
                self.__inspect_size(file)
                self.__inspect_line(file)
                self.__inspect_tab_or_space(file)

    def convert_encoding(self, from_encoding, to_encoding):
        """转换文件编码"""
        if not self.need_convert:
            return

        for file in self.files:
            write_bytes = None
            with open(file, 'rb') as file_handle:
                read_bytes = file_handle.read()
                bytes_encoding = chardet.detect(read_bytes)['encoding']

                if not bytes_encoding:
                    continue

                if self.is_encoding_equal(from_encoding, bytes_encoding):
                    try:
                        write_bytes = (read_bytes.decode(bytes_encoding)).encode(to_encoding)
                    except (UnicodeDecodeError, UnicodeEncodeError) as err:
                        print(colored('{file} convert from {from_encoding} to {to_encoding},err={err}'.format(
                            file=file, from_encoding=bytes_encoding, to_encoding=to_encoding, err=err), 'red'))
                        continue

            if write_bytes:
                with open(file, 'wb') as file_handle:
                    file_handle.write(write_bytes)
                    print(colored('{file} convert from {from_encoding} to {to_encoding}'.format(
                        file=file, from_encoding=bytes_encoding, to_encoding=to_encoding), 'green'))

    def __inspect_encoding(self, file):
        """检查文件编码,并将统计数据写入当前实例"""
        with open(file, 'rb') as file_handle:
            encoding = chardet.detect(file_handle.read())['encoding']
            self.encodings[encoding] = self.encodings.get(encoding, 0) + 1

    def __inspect_newline(self, file):
        """检查文件换行符,并将统计数据写入当前实例"""
        with open(file, 'rb') as file_handle:
            line = file_handle.readline()
            newline_character = self.get_new_line(line)
            if newline_character:
                self.newlines[newline_character] = self.newlines.get(newline_character, 0) + 1

    def __inspect_size(self, file):
        """检查文件大小,并将统计数据写入当前实例"""
        self.size = self.size + os.path.getsize(file)

    def __inspect_line(self, file):
        """检查文件行数,并将统计数据写入当前实例"""
        self.lines = self.lines + sum(1 for line in open(file, 'rb'))

    def __inspect_tab_or_space(self, file):
        """检查文件是空格还是跳格,并将统计数据写入当前实例"""
        with open(file, 'rb') as file_handle:
            if file_handle.read(1000).find(b'\t') != -1:
                self.tab_or_space['\t'] = self.tab_or_space.get('\t', 0) + 1
            else:
                self.tab_or_space['space'] = self.tab_or_space.get(
                    'space', 0) + 1


def get_filter_suffixs():
    """后缀白名单,在此白名单之内才会被处理"""
    return OPTIONS.suffix.split(',') if OPTIONS.suffix else []


def get_ignore_directorys():
    """文件目录黑名单,在此黑名单之内的目录不被处理"""
    if OPTIONS.ignore_directory:
        ignore_directorys = OPTIONS.ignore_directory.split(',')

        # exclude absolute directories
        for idx, directory in enumerate(ignore_directorys):
            ignore_directorys[idx] = os.path.abspath(
                os.path.join(OPTIONS.directory, directory))

        return ignore_directorys

    return []


def judge_ignore_directorys(ignore_directorys, judge_dir):
    """判断文件是否处在文件目录黑名单之内"""
    for directory in ignore_directorys:
        if judge_dir.startswith(directory):
            return True
    return False


def get_extension_dict(directory, ignore_directorys, filter_suffixs):
    """遍历目录获得所有全量文件名

    -> {后缀 : 文件列表}

    过滤方式:
    1.黑名单文件夹 2.白名单文件后缀
    """
    extension_dict = {}

    for root, _, files in os.walk(directory):
        for file in files:
            file = os.path.join(root, file)
            _, file_extension = os.path.splitext(file)

            # exclude directory
            if ignore_directorys:
                abspath = os.path.abspath(root)
                if judge_ignore_directorys(ignore_directorys, abspath):
                    continue

            # only include file
            if filter_suffixs:
                if file_extension not in filter_suffixs:
                    continue

            # like {.html: [A.html, B.html], .py: [A.py, B.py]}
            extension_dict.setdefault(
                file_extension, []).append(os.path.abspath(file))
    return extension_dict


def get_file_attrs(extension_dict):
    """把 {后缀 : 文件列表} 放到FileAttr list里,以文件数量进行排序

    -> [FileAttr]

    """
    file_attrs = []
    for key, value in extension_dict.items():
        file_attrs.append(FileAttr(key, value))
    file_attrs.sort(reverse=True)

    return file_attrs


def setup_directory():
    """传进来的positional arguments为列表,但是需要字符串,
    所以在这个函数强制替换得到OPTIONS.directory
    """
    OPTIONS.directory = OPTIONS.directory[0]


if __name__ == '__main__':
    OPTIONS = PARSER.parse_args()

    # 打印不出颜色才执行这句
    # reference https://github.com/spyder-ide/spyder/issues/1917
    colorama.init(strip=False)

    if not OPTIONS.command:
        PARSER.print_help()
        exit(0)

    if OPTIONS.command == 'analyze':
        # 分析文件目录信息
        setup_directory()

        IGNORE_DIRECTORYS = get_ignore_directorys()
        FILTER_SUFFIXS = get_filter_suffixs()
        EXTENSION_DICT = get_extension_dict(OPTIONS.directory, IGNORE_DIRECTORYS, FILTER_SUFFIXS)

        FILE_ATTRS = get_file_attrs(EXTENSION_DICT)

        for file_attr in FILE_ATTRS:
            file_attr.inspect_file()
            print(file_attr)

    if OPTIONS.command == 'convert':
        # 转换文件编码
        setup_directory()

        IGNORE_DIRECTORYS = get_ignore_directorys()
        FILTER_SUFFIXS = get_filter_suffixs()
        EXTENSION_DICT = get_extension_dict(OPTIONS.directory, IGNORE_DIRECTORYS, FILTER_SUFFIXS)

        FILE_ATTRS = get_file_attrs(EXTENSION_DICT)

        for file_attr in FILE_ATTRS:
            file_attr.convert_encoding(OPTIONS.convert_from, OPTIONS.convert_to)
