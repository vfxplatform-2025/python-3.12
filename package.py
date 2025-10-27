name = "python"
version = "3.12.10"

description = "Python for VFX Platform"

build_requires = [
    "gcc-11.5.0",
    "cmake-3.26.5",
]

requires = [
    "zlib-1.2.13",
    "openssl-3.0.16",   # VFX 플랫폼 통일 OpenSSL
    "xz-5.4.5",
    "bzip2-1.0.8",
    "libffi-3.4.4",
    "minizip_ng-4.0.10",
        "sqlite-3.44.0",
    "python_lib-3.12.10"
]

tools = [
    "python",
    "python3",
    "pip",
    "pip3"
]

build_command = "python {root}/rezbuild.py {install}"

def commands():
    env.PYTHON_VERSION = "3.12.10"
    env.PYTHON_MAJOR_VERSION = "3"
    env.PYTHON_MINOR_VERSION = "12"
    env.PATH.set("{root}/bin:{env.PATH}")
    env.LD_LIBRARY_PATH.prepend("{root}/lib")
    env.PIP_TARGET.set("{}/site-packages".format(env.REZ_PYTHON_LIB_ROOT))
    env.PYTHONUSERBASE.set("{}".format(env.REZ_PYTHON_LIB_ROOT))
    # env.PYTHONHOME.set("{root}")
    env.CMAKE_PREFIX_PATH.append("{root}")
