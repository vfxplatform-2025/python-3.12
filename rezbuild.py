# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess

def run_cmd(cmd, cwd=None):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, cwd=cwd, check=True)

def clean_build_dir(path):
    """build_path 내부만 삭제하되, build.rxt 마커는 보존합니다."""
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return
    print(f"🧹 Cleaning build dir (preserve *.rxt): {path}")
    for entry in os.listdir(path):
        p = os.path.join(path, entry)
        if entry.endswith(".rxt"):
            print(f"🔒 Preserving marker: {p}")
            continue
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            os.remove(p)

def clean_install_dir(path):
    """install_path 전체를 삭제합니다."""
    if os.path.isdir(path):
        print(f"🧹 Removing install dir: {path}")
        shutil.rmtree(path, ignore_errors=True)

def copy_license(src_root, install_root):
    for fname in ("LICENSE", "COPYING", "COPYRIGHT"):
        p = os.path.join(src_root, fname)
        if os.path.isfile(p):
            dst = os.path.join(install_root, "LICENSE")
            print(f"📄 Copying {fname} → {dst}")
            shutil.copy(p, dst)
            break

def copy_package_py(source_path, install_root):
    src = os.path.join(source_path, "package.py")
    dst = os.path.join(install_root, "package.py")
    if os.path.isfile(src):
        print(f"📄 Copying package.py → {dst}")
        shutil.copy(src, dst)

def write_build_marker(build_root):
    marker = os.path.join(build_root, "build.rxt")
    print(f"📝 Touching build marker: {marker}")
    open(marker, "a").close()

def create_symlinks(install_root):
    bin_dir = os.path.join(install_root, "bin")
    for src, dst in (("python3","python"), ("pip3","pip")):
        s = os.path.join(bin_dir, src)
        d = os.path.join(bin_dir, dst)
        if os.path.isfile(s) and not os.path.exists(d):
            print(f"🔗 Linking {dst} → {src}")
            os.symlink(src, d)

def find_python_source(source_path):
    parent = os.path.join(source_path, "source")
    if not os.path.isdir(parent):
        sys.exit(f"❌ source 디렉터리 자체가 없습니다: {parent}")
    candidates = [
        d for d in os.listdir(parent)
        if d.startswith("Python-") and os.path.isdir(os.path.join(parent, d))
    ]
    if not candidates:
        sys.exit(f"❌ Python-* 소스 폴더를 찾을 수 없습니다: {parent}")
    if len(candidates) > 1:
        print(f"⚠️ 여러 버전 폴더 발견: {candidates}. '{candidates[0]}' 사용합니다.")
    src = os.path.join(parent, candidates[0])
    print(f"✅ Using source directory: {src}")
    return src

def build(source_path, build_path, install_path, targets):
    # 1) source 자동 탐색
    src_root = find_python_source(source_path)

    # 2) install override
    version = os.environ.get("REZ_BUILD_PROJECT_VERSION", "3.12.10")
    if "install" in targets:
        install_root = f"/core/Linux/APPZ/packages/python/{version}"
        clean_install_dir(install_root)
    else:
        install_root = install_path

    # 3) build dir 초기화
    clean_build_dir(build_path)
    os.makedirs(build_path, exist_ok=True)

    # 3.1) 소스 트리 완전 클린
    print(f"🧹 Cleaning source tree: {src_root}")
    # make clean
    subprocess.run(f"make -C {src_root} clean", shell=True, check=False)
    # make distclean (이걸로 .o, executables, frozen_modules/*.h 모두 제거)
    subprocess.run(f"make -C {src_root} distclean", shell=True, check=False)

    # 4) configure (out-of-source)
    os.chdir(build_path)
    os.environ["LDFLAGS"] = f"-Wl,-rpath={install_root}/lib"
    cmd = [
        f"{src_root}/configure",
        f"--prefix={install_root}",
        "--enable-shared",
        "--with-lto",
        "--with-ensurepip=install",
        "--with-openssl=/core/Linux/APPZ/packages/openssl/3.0.16",
        "--with-system-sqlite={sqlite_path}",  # SQLite 시스템 사용
        "--enable-loadable-sqlite-extensions",   # SQLite 확장 가능
    ]
    run_cmd(" ".join(cmd))

    # 5) build & install
    run_cmd("make -j$(nproc)")
    if "install" in targets:
        run_cmd("make install")
        create_symlinks(install_root)
        copy_license(src_root, install_root)
        copy_package_py(source_path, install_root)

    # 6) build marker 작성
    write_build_marker(build_path)
    print(f"✅ Python {version} build & install completed: {install_root}")

if __name__ == "__main__":
    build(
        source_path  = os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path   = os.environ["REZ_BUILD_PATH"],
        install_path = os.environ["REZ_BUILD_INSTALL_PATH"],
        targets      = sys.argv[1:]
    )
