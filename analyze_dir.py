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


def need_judge_text(file):
    head, tail = os.path.split(file)
    _, extension = os.path.splitext(tail)

    include_extensions = ['.py', '.html', '.js', '.css', '.conf', '.txt', '.sh', '.pas', '.sql', '.sqc',
                          '.h', '.cpp', '.ini', '.H', '.txt', '.sql', '.CPP', '.rb']

    if extension in include_extensions:
        return True

    return False


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class FileAttr():
    def __init__(self, suffix, files):
        self.suffix = suffix
        self.files = files
        self.file_numbers = len(files)
        self.mimes = {}
        self.newlines = {}
        self.encodings = {}
        self.size = 0
        self.lines = 0
        self.tab_or_space = {}
        self.need_judge = False

    def __str__(self):
        if self.need_judge:
            return '{} {} newline: {} encoding: {} size: {} lines: {} tab_or_space: {}'.format(self.suffix,
                                                                                               self.file_numbers,
                                                                                               self.newlines,
                                                                                               self.encodings,
                                                                                               sizeof_fmt(self.size),
                                                                                               self.lines,
                                                                                               self.tab_or_space)
        else:
            return '{} {}'.format(self.suffix, self.file_numbers)

    def __lt__(self, other):
        return self.file_numbers < other.file_numbers


if __name__ == '__main__':
    (options, args) = parser.parse_args()

    extension_dict = {}

    if options.suffix:
        filter_suffixs = options.suffix.split(',')

    if options.ignore_directory:
        ignore_directorys = options.ignore_directory.split(',')

        # exclude absolute directories
        for idx, directory in enumerate(ignore_directorys):
            ignore_directorys[idx] = os.path.abspath(os.path.join(options.directory, directory))


    def judge_ignore_directorys(judge_dir):
        for dir in ignore_directorys:
            if judge_dir.startswith(dir):
                return True
        return False


    for root, dirs, files in os.walk(options.directory):
        for file in files:
            file = os.path.join(root, file)
            _, file_extension = os.path.splitext(file)

            # exclude directory
            if options.ignore_directory:
                abspath = os.path.abspath(root)
                if judge_ignore_directorys(abspath):
                    continue

            # only include file
            if options.suffix:
                if file_extension not in filter_suffixs:
                    continue

            # like {.html: [A.html, B.html], .py: [A.py, B.py]}
            extension_dict.setdefault(file_extension, []).append(os.path.abspath(file))

    file_attrs = []

    # put in list, and reverse sort by file's num
    for key, value in extension_dict.items():
        file_attrs.append(FileAttr(key, value))
    file_attrs.sort(reverse=True)

    for file_attr in file_attrs:
        for file in file_attr.files:

            need_judge = need_judge_text(file)

            # encoding
            encoding = None

            file_attr.need_judge = need_judge

            if need_judge:
                with open(file, 'rb') as f:
                    encoding = chardet.detect(f.read())['encoding']
                    file_attr.encodings[encoding] = file_attr.encodings.get(encoding, 0) + 1
            else:
                file_attr.encodings['?'] = file_attr.encodings.get('?', 0) + 1

            # newline
            if need_judge:
                with open(file, 'rb') as f:
                    line = f.readline()


                    def get_new_line(line):
                        new_line_characters = [b'\r\n', b'\r', b'\n', b'']
                        for c in new_line_characters:
                            if line.endswith(c):
                                return c.decode()
                        return None


                    c = get_new_line(line)
                    if c != None:
                        file_attr.newlines[c] = file_attr.newlines.get(c, 0) + 1
                    else:
                        file_attr.newlines['?'] = file_attr.newlines.get('?', 0) + 1

            else:
                file_attr.newlines['?'] = file_attr.newlines.get('?', 0) + 1

            # size
            file_attr.size = file_attr.size + os.path.getsize(file)

            # line
            if need_judge:
                file_attr.lines = file_attr.lines + sum(1 for line in open(file, 'rb'))

            # tab or space
            if need_judge:
                with open(file, 'rb') as f:
                    if f.read(500).find(b'\t') != -1:
                        file_attr.tab_or_space['\t'] = file_attr.tab_or_space.get('\t', 0) + 1
                    else:
                        file_attr.tab_or_space[r'space'] = file_attr.tab_or_space.get(r'space', 0) + 1

            if options.verbose:
                print('{} encoding:{}'.format(file, encoding))

        print(file_attr)
