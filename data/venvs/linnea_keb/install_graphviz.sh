#!/bin/bash
BUILD_DIR=$(pwd)/venv
mkdir -p tmp
cd tmp
wget https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/8.1.0/graphviz-8.1.0.tar.gz
tar -xzf graphviz-8.1.0.tar.gz
cd graphviz-8.1.0
./configure --prefix=$BUILD_DIR/ --with-qt=no --with-gts=no
make -j4 
make install
cd ../../
rm -rf tmp/
