
## 使用Cython编译整个python项目

ref: https://pushiqiang.blog.csdn.net/article/details/124734320

**Usage**
```
$ python build.py -h
usage: build.py [-h] [-c] [-f CONFIG] [-s SRC_DIR] [-o OUTPUT_DIR]
                [-e EXE_FILES] [-x EXCLUDE_FILES]

optional arguments:
  -h, --help            show this help message and exit
  -c, --using-config    whether to use a configuration file
  -f CONFIG, --config-file CONFIG
                        config file path for compile
  -s SRC_DIR, --src-dir SRC_DIR
                        src file dir
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        output file dir
  -e EXE_FILES, --exe-files EXE_FILES
                        the executable file list, separate by comma.
  -x EXCLUDE_FILES, --exclude-files EXCLUDE_FILES
                        the exclude file list, separate by comma.
```


**Example**
```
# build.yaml
compile:
  src_dir: '/home/test/src'
  output_dir: '/home/test/output'
  exe_files:
    - '{src_dir}/runserver.py'
  exclude_files:
    - '{src_dir}/uwsgi.py'

使用配置文件
python build.py -c -f ./build.yaml

或者
python build.py -s /home/test/src -o /home/test/output -e {src_dir}/runserver.py -x {src_dir}/uwsgi.py
```
