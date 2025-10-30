#!/usr/bin/env bash

set -e

source ./site/version.sh

tar xf OpenFOAM-${version_major}-${version_patch}.tar.gz
tar xf ThirdParty-${version_major}-version-${version_major}.tar.gz

mv OpenFOAM-${version_major}-${version_patch} OpenFOAM-${version_major}
mv ThirdParty-${version_major}-version-${version_major} ThirdParty-${version_major}

# Patch various issues:
settings=etc/config.sh/settings
cp site/$settings OpenFOAM-${version_major}/$settings

rules=wmake/rules/crayGcc
cp -r site/$rules OpenFOAM-${version_major}/$rules

file="ThirdParty-10/etc/wmakeFiles/scotch/Makefile.inc.i686_pc_linux2.shlib-OpenFOAM"

sed -i "s/gcc/\$(WM_CC)/"    ${file}
sed -i "s/mpicc/\$(WM_CC)/"  ${file}

cd OpenFOAM-${version_major}

source ./etc/bashrc || printf "./etc/bashrc returned %s\n" "$?"

./Allwmake -j 16 dep
./Allwmake -j 64
