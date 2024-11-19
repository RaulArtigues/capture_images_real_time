#!/bin/bash
apt-get update
apt-get install -y llvm libllvm12 build-essential
pip install -r requirements.txt