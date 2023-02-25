#!/bin/sh
set -e

build_dir=${1:-build}
mkdir -p "$build_dir"
build_dir=$(realpath "$build_dir")

install_dir=${2:-${build_dir}/tools}
mkdir -p "$install_dir"
install_dir=$(realpath "$install_dir")

echo "Building tools in $build_dir"
echo "Tools will be installed at $install_dir"
cd "$build_dir"

PATH=install_dir/bin:$PATH

# install cmake
cmake_version="3.25.2"
curl -LO https://github.com/Kitware/CMake/releases/download/v${cmake_version}/cmake-${cmake_version}.tar.gz
tar xf cmake-${cmake_version}.tar.gz

cd cmake-${cmake_version}
./bootstrap --prefix="$install_dir"
make
make install
cd ..

rm cmake-${cmake_version}.tar.gz

# install clang
git clone -b llvmorg-15.0.7 --depth=1 https://github.com/llvm/llvm-project.git
cd llvm-project
mkdir build
cd build
cmake -DLLVM_ENABLE_PROJECTS=clang -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$install_dir" -G "Unix Makefiles" ../llvm
make
make install
cd ../..

# install binutils
binutils_version="2.40"
curl -LO https://ftp.gnu.org/gnu/binutils/binutils-${binutils_version}.tar.xz
tar xf binutils-${binutils_version}.tar.xz

mkdir -p binutils_build
cd binutils_build
../binutils-${binutils_version}/configure --prefix="$install_dir" --enable-targets=all --enable-64-bit-bfd --disable-nls --disable-werror --disable-gprofng
make
make install
cd ..

rm -rf binutils_build
rm -rf binutils-${binutils_version}
rm -f binutils-${binutils_version}.tar.xz
