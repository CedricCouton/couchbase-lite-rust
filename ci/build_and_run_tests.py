#!/usr/bin/env python3
# For simplify migration between different CI

import os, time, sys
from pathlib import Path
from subprocess import check_call
from multiprocessing import cpu_count

def show_timing(function):
    def _wrapper(*args, **kwargs):
        start = time.time()
        ret = function(*args, **kwargs)
        elapsed = (time.time() - start)
        print("%s elapsed time: %f" % (function.__name__, elapsed))
        return ret
    return _wrapper

def mkdir_if_not_exists(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_src_root_path(my_path: str) -> str:
    my_path = os.path.dirname(os.path.realpath(my_path))
    return my_path

@show_timing
def build_and_test_cpp_part(src_root: str):
    cmake_build_dir = os.path.join(src_root, "build-cmake")
    cmake_src_dir = os.path.join(src_root, "couchbase-lite-core-sys",
                                 "couchbase-lite-core")
    mkdir_if_not_exists(cmake_build_dir)
    print("Current path: %s" % os.environ["PATH"])
    check_call(["cmake", "-DCMAKE_BUILD_TYPE=RelWithDebInfo", cmake_src_dir],
               cwd = cmake_build_dir)
    check_call(["ls"], cwd = cmake_build_dir)
    check_call(["cmake", "--build", ".", "--", "-j%d" % (cpu_count() + 1)],
               cwd = cmake_build_dir)

@show_timing
def build_and_test_rust_part(src_root: str):
    print("running tests in debug mode")
    check_call(["cargo", "test", "--all", "-vv"], cwd = src_root)
    print("running tests in release mode")
    check_call(["cargo", "test", "--all", "--release", "-vv"], cwd = src_root)

@show_timing
def main():
    ci_dir = Path(get_src_root_path(sys.argv[0]))
    src_root = ci_dir.parent
    build_and_test_cpp_part(src_root)
    build_and_test_rust_part(src_root)

if __name__ == "__main__":
    main()
