# analyze_dir

## 分析指定目录内的文件内容

* text or binary
* new line (LRLF/LF/LR)
* encoding (utf8-bom/utf-8/gb2312/...)
* use tab or space
* line number
* size

## 转换

* new line convert
* encoding convert
* tab space convert
* add new line to text file
* remove white line

```
$ python analyze_dir.py -d C:/work/source/FIXServer -i .git,qhbin,lib
.sqc 54 {'no_mime': 54} newline: {'\n': 54} encoding: {'ascii': 10, 'GB2312': 39, 'ISO-8859-1': 5} size: 348.7KiB lines: 10688 tab_or_space: {'space': 53, '\\t': 1}
.h 36 {'text/plain': 36} newline: {'\n': 36} encoding: {'ascii': 5, 'GB2312': 31} size: 263.5KiB lines: 7389 tab_or_space: {'space': 13, '\\t': 23}
.cpp 26 {'text/plain': 26} newline: {'\n': 26} encoding: {'ascii': 5, 'GB2312': 21} size: 295.9KiB lines: 11184 tab_or_space: {'space': 14, '\\t': 12}
.sh 13 {'application/x-sh': 13} newline: {'\n': 8, 'l': 5} encoding: {'ascii': 13} size: 816.0B lines: 59 tab_or_space: {'space': 13}
.sql 6 {'no_mime': 6} newline: {'\n': 6} encoding: {'ascii': 6} size: 4.7KiB lines: 206 tab_or_space: {'space': 5, '\\t': 1}
 4 {'text/plain': 2, 'no_mime': 2} newline: {'?': 2, '\n': 2} encoding: {'ascii': 2, '?': 2} size: 2.8KiB lines: 6 tab_or_space: {'space': 2}
```