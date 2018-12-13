"""
Using Cython to protect a Python codebase and convert *.py to binary
Make sure there are __init__.py file under each folder
"""

import sys
import os
import shutil
import time
import fnmatch


SUICIDE = True

try:
    from distutils.core import setup
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
except:
    print("You don't seem to have Cython installed. Please install it first")
    sys.exit(1)

start_time = time.time()
cur_dir = os.path.abspath(os.path.dirname(__file__))
setup_file = os.path.split(__file__)[1]
build_dir = os.path.join(cur_dir, 'build')
build_tmp_dir = os.path.join(build_dir, "temp")
# define exclude dirs
exclude_dirs = ['.git', '__pycache__', 'test', 'logs', 'venv', '.idea']
# defile exclude files
exclude_files = ['*.md', '.gitignore', '.python-version', 'requirements.txt', '*.pyc', '*.c']
ext_modules = []

if os.path.isdir(build_dir):
    print('You have build directory in your current directory. Please check and remove it first.')
    sys.exit(1)

# get all build files
for path, dirs, files in os.walk(cur_dir, topdown=True):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    # touch a new file when __init__.py not exists
    for _dir in dirs:
        init_file = os.path.join(path, _dir, '__init__.py')
        if not os.path.isfile(init_file):
            print('WARNING: create new empty [{}] file.'.format(init_file))
            with open(init_file, 'a') as f:
                pass
    # create target folder
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    # make empty dirs
    for dir_name in dirs:
        dir = os.path.join(path, dir_name)
        target_dir = dir.replace(cur_dir, build_dir)
        os.mkdir(target_dir)
    for file_name in files:
        file = os.path.join(path, file_name)
        if os.path.splitext(file)[1] == '.py':
            if file_name not in exclude_files:
                #  copy __init__.py resolve package cannot be imported
                if file_name == '__init__.py':
                    shutil.copy(file, path.replace(cur_dir, build_dir))
                if file_name != setup_file:
                    ext_modules.append(file)
            else:
                shutil.copy(file, path.replace(cur_dir, build_dir))
        else:
            _exclude = False
            for pattern in exclude_files:
                if fnmatch.fnmatch(file_name, pattern):
                    _exclude = True
            if not _exclude:
                shutil.copy(file, path.replace(cur_dir, build_dir))

try:
    setup(
            ext_modules=cythonize(
                ext_modules,
                compiler_directives=dict(
                    always_allow_keywords=True,
                    c_string_encoding='utf-8',
                    language_level=3
                )
            ),
            cmdclass=dict(
                build_ext=build_ext
            ),
            script_args=["build_ext", "-b", build_dir, "-t", build_tmp_dir]
        )
except Exception as e:
    print('ERROR: {}'.format(e))
    sys.exit(1)
else:
    shutil.rmtree(build_tmp_dir)
    # remove *.c temp files
    for path, dirs, files in os.walk(cur_dir):
        dirs[:] = [_dir for _dir in dirs if _dir not in exclude_dirs]
        for file in files:
            if file.endswith('.c'):
                os.unlink(os.path.join(path, file))
    # suicide mode: delete all file except build folder
    if SUICIDE:
        print("\nWARNING: Delete all files except in build folder")
        for path, dirs, files in os.walk(cur_dir):
            dirs[:] = [_dir for _dir in dirs if _dir not in [os.path.split(build_dir)[-1]]]
            for folder in dirs:
                folder = os.path.join(path, folder)
                shutil.rmtree(folder)
            for file in files:
                os.unlink(os.path.join(path, file))

    print("\nCompile finished!  cost time: {}s".format(time.time() - start_time))

