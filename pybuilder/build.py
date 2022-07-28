import os
import sys
import argparse

from yaml import load
from sysconfig import get_python_version

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def safe_exec(cmd):
    # print("Executing [%s] ..." % cmd)
    if 0 != os.system(cmd):
        sys.exit(-1)


def yaml_load(conf_file):
    """
    load config
    """
    with open(conf_file, "r") as fd:
        try:
            obj = load(fd, Loader=Loader)
        except Exception as e:
            print("Load yaml failed: %s" % e)
            sys.exit(-1)

    return obj


class PyBuilder(object):
    def __init__(self, conf):
        self.conf = conf
        self._format_config(conf)

        self._py_version = get_python_version()
        self._py_include = '/usr/include/python%s' % self._py_version
        self._compile_files = []

    def _format_config(self, conf):
        self.src_dir = conf['compile']['src_dir'].rstrip('/')
        self.output_dir = conf['compile']['output_dir'].rstrip('/')
        _exe_files = conf['compile'].get('exe_files') or []
        _exclude_files = conf['compile'].get('exclude_files') or []
        self.exe_files = [i.format(src_dir=self.output_dir) for i in _exe_files]
        self.exclude_files = [i.format(src_dir=self.output_dir) for i in _exclude_files]

    def _print(self):
        print('-------------------------------- PyBuilder ----------------------------------')
        print('src_dir         : %s' % self.src_dir)
        print('output_dir      : %s' % self.output_dir)
        print('python.version  : %s' % self._py_version)
        print('python.include  : %s' % self._py_include)
        print('-------------------------------- compiling ----------------------------------')

    @classmethod
    def need_compile(cls, file_name):
        if file_name.endswith('.py') and file_name != '__init__.py':
            return True
        return False

    def compile_exe(self, pys_file):
        """
        if this source file is executable, it shall be compiled to exe
        cython -D -2 --directive always_allow_keywords=true --embed main.py
        gcc -c -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o main.o main.c
        gcc -I/usr/include/python2.7 -o main main.o -lpython2.7
        """
        base_name, _ = os.path.splitext(pys_file)
        safe_exec("cython -D -%s --directive always_allow_keywords=true --embed %s" % (self._py_version[0], pys_file))
        safe_exec("gcc -c -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I%s -o %s.o %s.c" % (
            self._py_include, base_name, base_name))
        safe_exec("gcc -I%s -o %s %s.o -lpython%s" % (self._py_include, base_name, base_name, self._py_version))
        safe_exec("rm -f {base_name}.c {base_name}.o {base_name}.py".format(base_name=base_name))
        safe_exec("strip -s %s" % base_name)

    def compile_lib(self, pys_file):
        """
        cython -D -2 --directive always_allow_keywords=true main.py
        gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o main.so main.c
        """
        base_name, _ = os.path.splitext(pys_file)
        safe_exec("cython -D -%s --directive always_allow_keywords=true %s" % (self._py_version[0], pys_file))
        safe_exec("gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I%s -o %s.so %s.c" % (
            self._py_include, base_name, base_name))
        safe_exec("rm -f {base_name}.c {base_name}.py".format(base_name=base_name))
        safe_exec("strip -s %s.so" % base_name)

    def _compile_file(self):
        self._print()
        _count = len(self._compile_files)

        def _format_print(i, f):
            print('[{}%] compile: {}...'.format(int(float(i + 1) * 100 / _count),
                                                f.replace(self.output_dir, '{output_dir}')))
        for index, f_path in enumerate(self._compile_files):
            _format_print(index, f_path)
            if f_path in self.exe_files:
                self.compile_exe(f_path)
            else:
                self.compile_lib(f_path)
        print('-------------------------------- compiled ----------------------------------')

    @classmethod
    def skip_file(cls, file_name):
        _skip_name = ['_pycache_', '.git', '.gitignore']
        _skip_suffix = ['.pyc']
        if file_name in _skip_name:
            return True
        for _suffix in _skip_suffix:
            if file_name.endswith(_suffix):
                return True

        return False

    def _async_file(self, pys_dir):
        files = os.listdir(pys_dir)
        for f_name in files:
            if self.skip_file(f_name):
                continue

            f_path = os.path.join(pys_dir, f_name)
            new_path = f_path.replace(self.src_dir, self.output_dir)
            if os.path.isdir(f_path):
                safe_exec("mkdir -p %s" % new_path)
                self._async_file(f_path)
            elif os.path.isfile(f_path):
                safe_exec("cp -rf %s %s" % (f_path, new_path))
                if self.need_compile(f_name) and new_path not in self.exclude_files:
                    self._compile_files.append(new_path)

    def compile(self):
        safe_exec("mkdir -p %s" % self.output_dir)
        self._async_file(self.src_dir)
        self._compile_file()

    def build_package(self):
        """
        make deb
        """
        # cmd = "dpkg -b %s %s-%s.deb > /dev/null" % (deb_home, pkg_name, pkg_version)
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--using-config', action='store_true',
                        dest='using_config', help='whether to use a configuration file')
    parser.add_argument('-f', '--config-file', action='store', default='',
                        dest='config', help='config file path for compile')
    parser.add_argument('-s', '--src-dir', action='store', default='',
                        dest='src_dir', help='src file dir')
    parser.add_argument('-o', '--output-dir', action='store', default='',
                        dest='output_dir', help='output file dir')
    parser.add_argument('-e', '--exe-files', dest='exe_files',
                        help='the executable file list, separate by comma.')
    parser.add_argument('-x', '--exclude-files', dest='exclude_files',
                        help='the exclude file list, separate by comma.')

    args = parser.parse_args()
    if args.using_config:
        if not args.config:
            parser.error('config required')
        conf = yaml_load(args.config)
    else:
        if not args.src_dir:
            parser.error('src_dir required')
        if not args.output_dir:
            parser.error('output_dir required')

        _compile_config = {
            'src_dir': args.src_dir,
            'output_dir': args.output_dir
        }
        if args.exe_files:
            _compile_config['exe_files'] = args.exe_files.split(',')
        if args.exclude_files:
            _compile_config['exclude_files'] = args.exclude_files.split(',')

        conf = {'compile': _compile_config}

    builder = PyBuilder(conf)
    builder.compile()
    sys.exit(0)


if __name__ == '__main__':
    main()
