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

## TODO
* utf-8中文字节判定为二进制字节,istextfile函数判定为binary

## 关键细节

### 判断text还是binary
读取文件前500个字节,二进制字节 < 30%则为文本
