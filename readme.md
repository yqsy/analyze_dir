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
analyze_dir) D:\reference\project\analyze_dir>python analyze_dir.py analyze -i .git D:/reference/refer/ssbc
.py 59 newline: {'\r\n': 46} encoding: {'utf-8': 7, 'ascii': 39, None: 13} size: 73.1KiB lines: 2375 tab_or_space: {'space': 59}
.html 12 newline: {'\r\n': 12} encoding: {'utf-8': 8, 'ascii': 4} size: 21.0KiB lines: 601 tab_or_space: {'space': 12}
.js 6 newline: {'\r\n': 6} encoding: {'utf-8': 1, 'ascii': 5} size: 208.8KiB lines: 2469 tab_or_space: {'space': 6}
.css 5 newline: {'\r\n': 5} encoding: {'ascii': 5} size: 302.2KiB lines: 7093 tab_or_space: {'space': 5}
.png 4
 3
.conf 2 newline: {'\r\n': 2} encoding: {'ascii': 2} size: 1.8KiB lines: 95 tab_or_space: {'\t': 1, 'space': 1}
.sh 2 newline: {'\r\n': 2} encoding: {'ascii': 2} size: 307.0B lines: 6 tab_or_space: {'space': 2}
.txt 2 newline: {'\r\n': 2} encoding: {'utf-8': 1, 'ascii': 1} size: 6.5KiB lines: 473 tab_or_space: {'space': 2}
.map 2
.eot 1
.woff 1
.dat 1
.svg 1
.woff2 1
.jpg 1
.ico 1
.ttf 1
.md 1
```

```
$ python analyze_dir.py convert -i .git,.idea .
C:\work\source\my\analyze_dir\1.txt C:\work\source\my\analyze_dir\1.txt convert from gb2312 to utf-8
```
