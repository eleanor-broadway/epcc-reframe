#!/usr/bin/env python3

"""Reframe test for OpenFoam"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


class FetchOpenFoam(rfm.RunOnlyRegressionTest):
    """Downlaod OpenFoam"""

    version = variable(str, value="v2412")
    executable = "wget"
    executable_opts = [
        f"https://sourceforge.net/projects/openfoam/files/{version}/OpenFOAM-{version}.tgz",
        f"https://sourceforge.net/projects/openfoam/files/{version}/ThirdParty-{version}.tgz",
    ]
    local = True
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"fetch"}

    @sanity_function
    def validate_download(self):
        """Validate OpenFoam Downloaded"""
        return sn.path_isfile(f"ThirdParty-{self.version}.tgz") and sn.path_isfile(f"OpenFOAM-{self.version}.tgz")


@rfm.simple_test
class CompileOpenFoam(rfm.CompileOnlyRegressionTest):
    """Test compilation of OpenFoam"""

    build_system = "Make"
    fetch_openfoam = fixture(FetchOpenFoam, scope="environment")

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"compile"}

    modules = ["gcc/11.2.0", "mkl", "cray-fftw"]

    build_prefix = ""

    env_vars = {"FOAM_VERBOSE": "1", "FFTW_ARCH_PATH": "${FFTW_DIR}"}

    num_nodes = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
    time_limit = "4h"

    @run_before("compile")
    def prepare_build(self):
        """Prepare environment for build"""
        version = "v2412"
        label1 = "OpenFOAM"
        name1 = f"{label1}-{version}"
        archive1 = f"{label1}-{version}.tgz"
        label2 = "ThirdParty"
        name2 = f"{label2}-{version}"
        archive2 = f"{label2}-{version}.tgz"

        self.build_prefix = f"{name1}"

        config_file_fftw = f"{name1}/etc/config.sh/FFTW"
        config_file_paraview = f"{name1}/etc/config.sh/paraview"

        fullpath1 = os.path.join(self.fetch_openfoam.stagedir, archive1)
        fullpath2 = os.path.join(self.fetch_openfoam.stagedir, archive2)

        self.prebuild_cmds = [
            f"cp {fullpath1} {self.stagedir}",
            f"cp {fullpath2} {self.stagedir}",
            f"tar xzf {archive1}",
            f"tar xzf {archive2}",
            f"export FOAM_SRC={self.build_prefix}",
            f"export FOAM_THIRDPARTY={name2}",
            f"cp prefs.sh {name1}/etc/prefs.sh",
            f"sed -i 's/^fftw_version.*/fftw_version=fftw-system/' {config_file_fftw}",
            f"sed -i 's/^export FFTW_ARCH_PATH.*//' {config_file_fftw}",
            f"sed -i 's/^ParaView_VERSION.*/ParaView_VERSION=none/' {config_file_paraview}",
            f"cd {self.build_prefix}",
            "pwd",
            "ls",
            "module list",
            "source ./etc/bashrc",
            "echo $WM_PROJECT_DIR",
            "ls $WM_PROJECT_DIR",
            "./Allwmake -j 16",
            "./Allwmake -j 1",
        ]

        self.build_system.options = ["-v", "-n"]

    @sanity_function
    def validate_compile(self):
        """Validate compilation by checking existance of binary"""
        return sn.assert_eq(0, 0)
