#!/usr/bin/env bash

set -e

source ./site/version.sh

# Note openfoam.org recommend renaming the source directory without
# the extension, although we need to remember somewhere exactly
# what version it is...
# ...

tar xf OpenFOAM-${version_major}-${version_patch}.tar.gz
tar xf ThirdParty-${version_major}-version-${version_major}.tar.gz

mv OpenFOAM-${version_major}-${version_patch} OpenFOAM-${version_major}
mv ThirdParty-${version_major}-version-${version_major} ThirdParty-${version_major}

# Patch various issues

export FOAM_SRC=${FOAM_INST_DIR}/OpenFOAM-${version_major}
export FOAM_THIRDPARTY=${FOAM_INST_DIR}/ThirdParty-${version_major}
printf "Install OpenFOAM in FOAM_INST_DIR: %s\n" ${FOAM_INST_DIR}


# Install our site-specific extras from ./site
# OpenFoam does't deal very well (or at all) with Cray MPICH
# from the environment, so we have edited the settings script
# and replace it here. Further relevant environment variables
# come from ./etc/prefs.sh (included in ${FOAM_SRC}/etc/bashrc).

settings=etc/config.sh/settings
cp ${FOAM_INST_DIR}/site/$settings ${FOAM_SRC}/$settings

rules=wmake/rules/crayGcc
cp -r ${FOAM_INST_DIR}/site/$rules ${FOAM_SRC}/$rules

# Third Party scotch Makefile
# Replace "gcc" and "mpicc" by "$(WM_CC)"

file="${FOAM_THIRDPARTY}/etc/wmakeFiles/scotch/Makefile.inc.i686_pc_linux2.shlib-OpenFOAM"

sed -i "s/gcc/\$(WM_CC)/"    ${file}
sed -i "s/mpicc/\$(WM_CC)/"  ${file}

# To be run from FOAM_INST_DIR
# I make the dependencies first.

cd OpenFOAM-${version_major}

# source ../site/modules.sh
source ./etc/bashrc || printf "./etc/bashrc returned %s\n" "$?"

./Allwmake -j 16 dep
./Allwmake -j 64
