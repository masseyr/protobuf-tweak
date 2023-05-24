#!/bin/sh
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install build-essential git wget tar openssh-server -y
sudo apt-get install python3 python3-pip python3-venv -y
sudo apt-get install netcdf-bin libnetcdff-dev libhdf5-dev hdf5-tools h5utils -y
sudo apt-get install gfortran cmake ecbuild -y
mkdir .env
python3 -m venv .env/crtm
. .env/crtm/bin/activate
pip install netcdf4 h5py numpy matplotlib scikit-build
git clone https://github.com/masseyr/crtm-bundle.git crtm
cd crtm
cp -v ~/kickstart_pyCRTM_Ubuntu2204.sh .
sh kickstart_pyCRTM_Ubuntu2204.sh
deactivate
