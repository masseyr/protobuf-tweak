FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install build-essential git wget tar openssh-server -y
RUN apt-get install python3 python3-pip python3-venv -y
RUN apt-get install netcdf-bin libnetcdff-dev libhdf5-dev hdf5-tools h5utils -y
RUN apt-get install gfortran cmake ecbuild -y
RUN mkdir .env
RUN python3 -m venv .env/crtm
RUN . .env/crtm/bin/activate
RUN pip install netcdf4 h5py numpy matplotlib scikit-build
RUN git clone https://github.com/jcsda/crtm-bundle.git crtm
WORKDIR crtm
COPY kickstart_pyCRTM_Ubuntu2204.sh .
COPY setup_pycrtm.py .
RUN ls -la
RUN sh kickstart_pyCRTM_Ubuntu2204.sh
EXPOSE 22
CMD ["service", "ssh", "start", "-D"]
