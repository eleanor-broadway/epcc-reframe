#!/bin/bash 

PYTHON_TAG=python`echo ${CRAY_PYTHON_LEVEL} | cut -d. -f1-2`

# PRFX=${HOME/home/work}/pyenvs
# PYVENV_ROOT=${PRFX}/${PYVENV_NAME}
# PYVENV_SITEPKGS=${PYVENV_ROOT}/lib/${PYTHON_TAG}/site-packages

echo ${PYVENV_NAME}

mkdir -p ${PYVENV_NAME}
cd ${PYVENV_NAME}

python -m venv --system-site-packages ${PYVENV_NAME}
extend-venv-activate ${PYVENV_NAME}
source ${PYVENV_NAME}/bin/activate

mkdir -p ${PYVENV_NAME}/repos
cd ${PYVENV_NAME}/repos

git clone -b hpc-1.0-branch https://github.com/mlcommons/logging mlperf-logging
python -m pip install -e mlperf-logging

# rm ${PYVENV_SITEPKGS}/mlperf-logging.egg-link
# mv ./mlperf-logging/mlperf_logging ${PYVENV_SITEPKGS}/
# mv ./mlperf-logging/mlperf_logging.egg-info ${PYVENV_SITEPKGS}/

python -m pip install git+https://github.com/ildoonet/pytorch-gradual-warmup-lr.git

deactivate