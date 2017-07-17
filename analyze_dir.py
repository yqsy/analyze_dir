"""analyze directory"""
from optparse import OptionParser
import os
import mimetypes
import chardet

from binary_or_text.binary_or_text import istextfile

parser = OptionParser()

parser.add_option('-d', '--dir', dest='directory', default='.',
                  help='which directory to be traversed')

parser.add_option('-s', '--suffix', dest='suffix', default=None,
                  help="""which suffix to be traversed. type in '.html,.css'""")

# TODO make it like .gitignore
# only directory ok
# all directory and files
# Relative directory and files
parser.add_option('-i', '--ignore_directory', dest='ignore_directory', default=None,
                  help="""ignore director. type in 'dir1,dir1/dir2'""")

parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                  help='verbose')


class FileAttr():
    def __init__(self, suffix, files):
        self.suffix = suffix
        self.files = files
        self.file_numbers = len(files)
        self.newlines = {}
        self.encodings = {}
        self.size = 0
        self.lines = 0
        self.tab_or_space = {}
        self.need_judge = True if self.need_judge_text(self.suffix) else False

    def __str__(self):
        if self.need_judge:
            return '{} {} newline: {} encoding: {} size: \
{} lines: {} tab_or_space: {}'.format(self.suffix,
                                      self.file_numbers,
                                      self.newlines,
                                      self.encodings,
                                      self.sizeof_fmt(self.size),
                                      self.lines,
                                      self.tab_or_space)
        else:
            return '{} {}'.format(self.suffix, self.file_numbers)

    def __lt__(self, other):
        return self.file_numbers < other.file_numbers

    @staticmethod
    def need_judge_text(extension):
        """根据后缀名判断文件是否需要检查"""

        include_extensions = ['.py', '.html', '.js', '.css', '.conf',
                              '.txt', '.sh', '.pas', '.sql', '.sqc',
                              '.h', '.cpp', '.ini', '.H', '.txt',
                              '.sql', '.CPP', '.rb']

        if extension in include_extensions:
            return True

        return False

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
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
        for c in new_line_characters:
            if line.endswith(c):
                return c.decode()
            return None

    def inspect_file(self):
        """检查所有文件属性
        1.encoding 2.newline 3.size 4.line 5.tab or space
        """
        for file in self.files:
            if self.need_judge:
                self.inspect_encoding(file)
                self.insepect_newline(file)
                self.insepect_size(file)
                self.inspect_line(file)
                self.inspect_tab_or_space(file)

    def inspect_encoding(self, file):
        """检查文件编码,并将统计数据写入当前实例"""
        with open(file, 'rb') as file_handle:
            encoding = chardet.detect(file_handle.read())['encoding']
            self.encodings[encoding] = self.encodings.get(encoding, 0) + 1

    def insepect_newline(self, file):
        """检查文件换行符,并将统计数据写入当前实例"""
        with open(file, 'rb') as file_handle:
            line = file_handle.readline()
            c = self.get_new_line(line)
            if c:
                self.newlines[c] = self.newlines.get(c, 0) + 1

    def insepect_size(self, file):
        """检查文件大小,并将统计数据写入当前实例"""
        self.size = self.size + os.path.getsize(file)

    def inspect_line(self, file):
        """检查文件行数,并将统计数据写入当前实例"""
        self.lines = self.lines + sum(1 for line in open(file, 'rb'))

    def inspect_tab_or_space(self, file):
        """检查文件是空格还是跳格,并将统计数据写入当前实例"""
        with open(file, 'rb') as file_handle:
            if file_handle.read(1000).find(b'\t') != -1:
                self.tab_or_space['\t'] = self.tab_or_space.get('\t', 0) + 1
            else:
                self.tab_or_space['space'] = self.tab_or_space.get('space', 0) + 1


def get_filter_suffixs():
    """后缀白名单,在此白名单之内才会被处理"""
    return options.suffix.split(',') if options.suffix else []


def get_ignore_directorys():
    """文件目录黑名单,在此黑名单之内的目录不被处理"""
    if options.ignore_directory:
        ignore_directorys = options.ignore_directory.split(',')

        # exclude absolute directories
        for idx, directory in enumerate(ignore_directorys):
            ignore_directorys[idx] = os.path.abspath(
                os.path.join(options.directory, directory))

        return ignore_directorys

    return []


def judge_ignore_directorys(ignore_directorys, judge_dir):
    """判断文件是否处在文件目录黑名单之内"""
    for dir in ignore_directorys:
        if judge_dir.startswith(dir):
            return True
    return False


def get_extension_dict(ignore_directorys, filter_suffixs):
    """遍历目录获得所有全量文件名
    
    -> {后缀 : 全量文件名列表}
    
    过滤方式:
    1.黑名单文件夹 2.白名单文件后缀
    """
    extension_dict = {}

    for root, dirs, files in os.walk(options.directory):
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
    """把 {后缀 : 全量文件名列表} 放到FileAttr list里,以文件数量进行排序
    
    -> [FileAttr]
    
    """
    file_attrs = []
    for key, value in extension_dict.items():
        file_attrs.append(FileAttr(key, value))
    file_attrs.sort(reverse=True)

    return file_attrs


if __name__ == '__main__':
    (options, args) = parser.parse_args()

    filter_suffixs = get_filter_suffixs()

    ignore_directorys = get_ignore_directorys()

    extension_dict = get_extension_dict(ignore_directorys, filter_suffixs)

    file_attrs = get_file_attrs(extension_dict)

    for file_attr in file_attrs:
        file_attr.inspect_file()
        print(file_attr)
