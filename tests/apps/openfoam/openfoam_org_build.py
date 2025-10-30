"""Reframe test for OpenFoam"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from openfoam_org_base import OpenFOAMBase

class FetchOpenFOAM(rfm.RunOnlyRegressionTest):
    """Download OpenFoam"""

    local = True
    tags = {"fetch"}

    valid_systems = ["archer2:login"]
    executable = "bash"
    executable_opts = [
        "-c",
        f"""
        wget -O OpenFOAM-{OpenFOAMBase.openfoam_org_version_major}-{OpenFOAMBase.openfoam_org_version_patch}.tar.gz \
        http://dl.openfoam.org/source/{OpenFOAMBase.openfoam_org_version} &&
        wget -O ThirdParty-{OpenFOAMBase.openfoam_org_version_major}-version-{OpenFOAMBase.openfoam_org_version_major}.tar.gz \
        http://dl.openfoam.org/third-party/{OpenFOAMBase.openfoam_org_version_major}
        """ 
    ]

    @sanity_function
    def validate_download(self):
        """Validate OpenFoam Downloaded"""
        return sn.all([
            sn.path_isfile(f"OpenFOAM-{OpenFOAMBase.openfoam_org_version_major}-{OpenFOAMBase.openfoam_org_version_patch}.tar.gz"),
            sn.path_isfile(f"ThirdParty-{OpenFOAMBase.openfoam_org_version_major}-version-{OpenFOAMBase.openfoam_org_version_major}.tar.gz")
        ])


@rfm.simple_test
class CompileOpenFOAM(rfm.CompileOnlyRegressionTest):
    """Test compilation of OpenFoam"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    tags = {"compile"}

    # local = True
    # build_locally = True

    build_system = "CustomBuild"
    build_locally = False

    openfoam_src = fixture(FetchOpenFOAM, scope="environment")
    
    num_nodes = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
    time_limit = "4h"

    @run_before("compile")
    def copy_sources(self):
        """Copy tarballs from FetchOpenFOAM output."""
        self.prerun_cmds = [
            f"cp {self.openfoam_src.stagedir}/OpenFOAM-*.tar.gz .",
            f"cp {self.openfoam_src.stagedir}/ThirdParty-*.tar.gz ."
        ]

    @run_before('compile')
    def setup_build(self):
        self.build_system.commands = [
            'chmod u+x site/compile.sh',
            './site/compile.sh',
        ]

    # @run_before("compile")
    # def prepare_and_build(self):
    #     """Copy tarballs from FetchOpenFOAM output."""
    #     self.prerun_cmds = [
    #         f"cp {self.openfoam_src.stagedir}/OpenFOAM-*.tar.gz .",
    #         f"cp {self.openfoam_src.stagedir}/ThirdParty-*.tar.gz .",
    #         f"tar xf OpenFOAM-{OpenFOAMBase.openfoam_org_version_major}-{OpenFOAMBase.openfoam_org_version_patch}.tar.gz",
    #         f"tar xf ThirdParty-{OpenFOAMBase.openfoam_org_version_major}-version-{OpenFOAMBase.openfoam_org_version_major}.tar.gz", 
    #         f"mv OpenFOAM-{OpenFOAMBase.openfoam_org_version_major}-{OpenFOAMBase.openfoam_org_version_patch} OpenFOAM-{OpenFOAMBase.openfoam_org_version_major}",
    #         f"mv ThirdParty-{OpenFOAMBase.openfoam_org_version_major}-version-{OpenFOAMBase.openfoam_org_version_major} ThirdParty-{OpenFOAMBase.openfoam_org_version_major}"
    #     ]

    #     self.build_system.commands = [
    #         'chmod u+x site/compile.sh',
    #         './site/compile.sh',
    #     ]




    # executable = 'source'
    # executable_opts = [f'./site-v{OpenFOAMBase.openfoam_org_version_major}.{OpenFOAMBase.openfoam_org_version_patch}/compile.sh']

    @sanity_function
    def validate_build(self):
        """Check that build completed successfully."""
        return sn.assert_found(r"Build complete", self.stdout)







    # env_vars = {"FOAM_VERBOSE": "1", "FFTW_ARCH_PATH": "${FFTW_DIR}"}

    # num_nodes = 1
    # num_tasks_per_node = 1
    # num_cpus_per_task = 1
    # num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
    # time_limit = "4h"

    # @run_before("compile")
    # def prepare_build(self):
    #     """Prepare environment for build"""
    #     version = "v2412"
    #     label1 = "OpenFOAM"
    #     name1 = f"{label1}-{version}"
    #     archive1 = f"{label1}-{version}.tgz"
    #     label2 = "ThirdParty"
    #     name2 = f"{label2}-{version}"
    #     archive2 = f"{label2}-{version}.tgz"

    #     self.build_prefix = f"{name1}"

    #     config_file_fftw = f"{name1}/etc/config.sh/FFTW"
    #     config_file_paraview = f"{name1}/etc/config.sh/paraview"

    #     fullpath1 = os.path.join(self.fetch_openfoam.stagedir, archive1)
    #     fullpath2 = os.path.join(self.fetch_openfoam.stagedir, archive2)

    #     self.prebuild_cmds = [
    #         f"cp {fullpath1} {self.stagedir}",
    #         f"cp {fullpath2} {self.stagedir}",
    #         f"tar xzf {archive1}",
    #         f"tar xzf {archive2}",
    #         f"export FOAM_SRC={self.build_prefix}",
    #         f"export FOAM_THIRDPARTY={name2}",
    #         f"cp prefs.sh {name1}/etc/prefs.sh",
    #         f"sed -i 's/^fftw_version.*/fftw_version=fftw-system/' {config_file_fftw}",
    #         f"sed -i 's/^export FFTW_ARCH_PATH.*//' {config_file_fftw}",
    #         f"sed -i 's/^ParaView_VERSION.*/ParaView_VERSION=none/' {config_file_paraview}",
    #         f"cd {self.build_prefix}",
    #         "pwd",
    #         "ls",
    #         "module list",
    #         "source ./etc/bashrc",
    #         "echo $WM_PROJECT_DIR",
    #         "ls $WM_PROJECT_DIR",
    #         "./Allwmake -j 16",
    #         "./Allwmake -j 1",
    #     ]

    #     self.build_system.options = ["-v", "-n"]

    # @sanity_function
    # def validate_compile(self):
    #     """Validate compilation by checking existance of binary"""
    #     return sn.assert_eq(0, 0)
