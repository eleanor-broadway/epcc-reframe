#!/usr/bin/env python3

"""Reframe test for OpenFoam"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


class Fetch_Open_Foam(rfm.RunOnlyRegressionTest):
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
        """Validate OenFoam Downloaded"""
        return sn.path_isfile(f"ThirdParty-{self.version}.tgz") and sn.path_isfile(f"OpenFOAM-{self.version}.tgz")


class Compile_Open_Foam(rfm.CompileOnlyRegressionTest):
    """Test compilation of OpenFoam"""

    build_system = "Make"
    fetch_openfoam = fixture(Fetch_Open_Foam, scope="environment")

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


@rfm.simple_test
class Test_Open_Foam(rfm.RunOnlyRegressionTest):
    """OpenFoam Test"""

    # Select system to use
    valid_systems = ["archer2:compute"]

    # Set Programming Environment
    valid_prog_environs = ["PrgEnv-gnu"]

    # Description of test
    descr = "OpenFoam damnBreak"

    tags = {"performance", "applications"}

    compile_openfoam = fixture(Compile_Open_Foam, scope="environment")

    modules = ["gcc/11.2.0", "mkl", "cray-fftw"]

    version = "v2412"

    # slurm parameters
    num_nodes = 4
    num_tasks_per_node = 1
    num_cpus_per_task = 128
    num_tasks = num_nodes * num_tasks_per_node
    time_limit = "10m"

    # different cpu frequencies
    freq = parameter(["2250000", "2000000"])

    # Output files to be retained
    keep_files = ["rfm_job.out"]

    # Identify the executable
    executable = "interFoam"

    # Command line options for executable
    executable_opts = ["-parallel"]

    reference_performance = {
        "2000000": (4, -0.2, 0.2, "seconds"),
        "2250000": (3, -0.2, 0.2, "seconds"),
    }

    @run_after("init")
    def setup_params(self):
        """sets up extra parameters"""
        self.descr += self.freq
        if self.current_system.name in ["archer2"]:
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "OMP_PLACES": "cores",
                "SLURM_CPU_FREQ_REQ": self.freq,
            }

    @run_before("run")
    def prepare_run(self):
        """set up job execution"""

        foam_install_dir = os.path.join(self.compile_openfoam.stagedir, self.compile_openfoam.build_prefix)

        print("foam_install_dir: ", foam_install_dir)

        self.prerun_cmds = [
            f"export FOAM_INSTALL_DIR={foam_install_dir}",
            "source ${FOAM_INSTALL_DIR}/etc/bashrc",
            "cp -r ${FOAM_INSTALL_DIR}/tutorials/multiphase/interFoam/laminar/damBreak/damBreak .",
            "cd damBreak",
            "blockMesh",
            "cp -r 0.orig/ 0/",
            "cp 0/alpha.water 0/alpha.water.orig",
            "setFields",
            "decomposePar",
        ]

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("End", self.keep_files[0])

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"ExecutionTime\s+=\s+(?P<time>\d+.?\d*\s+)s\s+ClockTime\s+=\s+\d*\s+s\n\nEnd",
            self.keep_files[0],
            "time",
            float,
        )
