#! /bin/bash

STARTDIR=$(pwd)
INSTALL_PREFIX="$STARTDIR"/libs

PYTHON_PATH="$INSTALL_PREFIX"/lib/python2.6/site-packages

mkdir -p "$INSTALL_PREFIX"
mkdir -p "$PYTHON_PATH"

export LOCALBASE="$INSTALL_PREFIX"
export PYTHONPATH="$PYTHONPATH:$PYTHON_PATH" # easy_install needs python path to be set up

# Add path to pythonpath
STR="export PYTHONPATH=\$PYTHONPATH:$PYTHON_PATH"
grep -Fxq "$STR" ~/.bashrc || echo "$STR" >> ~/.bashrc

# echo "Installing OpenCV..."
# svn co -q https://code.ros.org/svn/opencv/branches/2.3/opencv /tmp/opencv_svn

# mkdir /tmp/opencv_svn/release
# cd /tmp/opencv_svn/release

# cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" -D WITH_FFMPEG=OFF ..
# make && make install

# cd "$STARTDIR"
# rm -rf /tmp/opencv_svn

# echo "Installing PyGame"
# mkdir tmp/
# cd tmp

# Install sdl_font module
wget http://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-2.0.11.tar.gz
tar -xzvf SDL_ttf-2.0.11.tar.gz
cd SDL_ttf-2.0.11
./configure --prefix="$INSTALL_PREFIX"
make && make install

cd "$STARTDIR"
rm -rf tmp/

easy_install --prefix="$INSTALL_PREFIX" pygame

echo "installing SimpleCV"
easy_install --prefix="$INSTALL_PREFIX" simplecv