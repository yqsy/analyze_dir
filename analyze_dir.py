from optparse import OptionParser
import os
import mimetypes

from binary_or_text.binary_or_text import istextfile

parser = OptionParser()

parser.add_option('-d', '--dir', dest='directory', default='.',
                  help='which directory to be traversed')

parser.add_option('-s', '--suffix', dest='suffix', default=None,
                  help="""which suffix to be traversed. type in '.html;.css'""")

# TODO make it like .gitignore
# only directory ok
# all directory and files
# Relative directory and files
parser.add_option('-i', '--ignore_directory', dest='ignore_directory', default=None,
                  help="""""""ignore director. type in 'dir1;dir1/dir2'""")


class FileAttr():
    def __init__(self, suffix, files):
        self.suffix = suffix
        self.files = files
        self.file_numbers = len(files)

    def __str__(self):
        return '{} {}'.format(self.suffix, self.file_numbers)

    def __lt__(self, other):
        return self.file_numbers < other.file_numbers


if __name__ == '__main__':
    (options, args) = parser.parse_args()

    extension_dict = {}

    if options.suffix:
        filter_suffixs = options.suffix.split(';')

    if options.ignore_directory:
        ignore_directorys = options.ignore_directory.split(';')

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
                if judge_ignore_directorys(root):
                    continue

            # only include file
            if options.suffix:
                if file_extension not in filter_suffixs:
                    continue

            # like {.html: [A.html, B.html], .py: [A.py, B.py]}
            extension_dict.setdefault(file_extension, []).append(file)

    file_attrs = []

    # put in list, and reverse sort by file's num
    for key, value in extension_dict.items():
        file_attrs.append(FileAttr(key, value))
    file_attrs.sort(reverse=True)

    for file_attr in file_attrs:
        print(file_attr)

        for file in file_attr.files:
            mine = mimetypes.guess_type(file)

            if not mine[0]:
                print('[no mine]', file)
            else:
                print('[', mine[0], ']', file)

