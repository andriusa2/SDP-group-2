# openCVbuilder.sh - A shell script to build a local copy of openCV in DICE..
unzip opencv-2.4.9
cd opencv-2.4.9
sed -i '50 d' ./cmake/cl2cpp.cmake
mkdir build
cd build
cmake -D BUILD_DOCS=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF -DCMAKE_INSTALL_PREFIX=$HOME/usr ..
make
make install
