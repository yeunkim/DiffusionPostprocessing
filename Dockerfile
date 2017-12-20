# Use Ubuntu 14.04 LTS
FROM ubuntu:trusty-20170119

RUN apt-get -y update --fix-missing && apt-get install -y \
    build-essential \
    git \
    libxt6 \
    unzip \
    wget

RUN apt-get update && apt-get install -y --no-install-recommends python-pip python-six python-nibabel python-setuptools python-pandas && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN pip install pybids==0.0.1
ENV PYTHONPATH=""

COPY fsl/fslinstaller.py /

RUN python /fslinstaller.py -d /usr/share/fsl -V 5.0.10

ENV FSLDIR=/usr/share/fsl/

RUN . ${FSLDIR}/etc/fslconf/fsl.sh

ENV FSL_DIR="${FSLDIR}"
ENV POSSUMDIR=/usr/share/fsl
ENV PATH=/${FSLDIR}/bin:${PATH}
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV FSLMULTIFILEQUIT=TRUE


COPY run.py /run.py
RUN chmod +x run.py

ENTRYPOINT ["/run.py"]