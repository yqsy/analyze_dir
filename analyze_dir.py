from optparse import OptionParser
import os
import mimetypes

parser = OptionParser()

parser.add_option('-d', '--dir', dest='directory', default='.',
                  help='which directory to be traversed')


class FileAttr():

    def __init__(self, suffix, files):
        self.suffix = suffix
        self.files = files
        self.len = len(files)

    def __str__(self):
        return '{} {}'.format(self.suffix, self.len)

    def __lt__(self, other):
        return self.len < other.len

if __name__ == '__main__':
    (options, args) = parser.parse_args()

    extension_dict = {}

    for root, dirs, files in os.walk(options.directory):
        for file in files:
            file = os.path.join(root, file)
            _, file_extension = os.path.splitext(file)

            extension_dict.setdefault(file_extension, []).append(file)

    file_attrs = []

    for key,value in extension_dict.items():
        file_attrs.append(FileAttr(key, value))

    file_attrs.sort(reverse=True)

    for file_attr in file_attrs:
        print(file_attr)

        for file in file_attr.files:
            mime = mimetypes.guess_type(file)
            print(file, mime)

