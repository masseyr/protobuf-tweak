#simple script to kickstart pycrtm
mkdir crtm_v2.4.0
cd crtm_v2.4.0
echo "[kickstart] making crtm in crtm-bundle/crtm_v2.4.0:"
ecbuild ../
echo "[kickstart] compiling crtm:"
make -j8
echo "[kickstart] linking to modules:"
ln -fs `find ./ -name "crtm_module.mod" | sed 's/crtm_module.mod//'` ./include
cd ..

cd crtm
echo "[kickstart] getting remote binary data."
sh Get_CRTM_Binary_Files.sh
cd ..

echo "[kickstart] installing pycrtm"

cd pycrtm
ls -la
cp -v ~/setup_pycrtm.py .
./setup_pycrtm.py  --install $PWD/../crtm_install --repos $PWD/../crtm --jproc 1 --coef $PWD/../crtm_install --ncpath_lib /usr/lib/x86_64-linux-gnu --ncpath_inc /usr/include --h5path_lib /usr/lib/x86_64-linux-gnu/hdf5/serial --h5path_inc /usr/include/hdf5/serial --arch gfortran --inplace
ln -fs $PWD/../crtm_install/crtm_coef_pycrtm $PWD
ln -fs `find ./ -maxdepth 1 -name "pycrtm.cpython*.so"` ./pycrtm.so
ln -fs ../crtm_v2.4.0/lib/libcrtm.so .
echo "[kickstart] running a testcase."
./testCases/test_cris.py
echo "[kickstart] running another testcase."
./testCases/test_atms.py
echo "[kickstart] Read the README.md file for more information (note *_threads.py files currently not functional)."
