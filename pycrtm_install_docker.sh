mkdir dockerdir
cd dockerdir
cp ~/ubuntu.dockerfile .
cp ~/setup_pycrtm.py .
cp ~/kickstart_pyCRTM_Ubuntu2204.sh .
docker build -f ubuntu.dockerfile . --no-cache
