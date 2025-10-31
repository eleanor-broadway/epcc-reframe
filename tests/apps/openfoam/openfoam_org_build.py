"""Reframe test for building OpenFoam"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

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
        wget -O OpenFOAM-{OpenFOAMBase.v_major}-{OpenFOAMBase.v_patch}.tar.gz \
        http://dl.openfoam.org/source/{OpenFOAMBase.version} &&
        wget -O ThirdParty-{OpenFOAMBase.v_major}-version-{OpenFOAMBase.v_major}.tar.gz \
        http://dl.openfoam.org/third-party/{OpenFOAMBase.v_major}
        """,
    ]

    @sanity_function
    def validate_download(self):
        """Validate OpenFoam Downloaded"""
        return sn.all(
            [
                sn.path_isfile(
                    f"OpenFOAM-{OpenFOAMBase.v_major}-{OpenFOAMBase.v_patch}.tar.gz"
                ),
                sn.path_isfile(
                    f"ThirdParty-{OpenFOAMBase.v_major}-version-{OpenFOAMBase.v_major}.tar.gz"
                ),
            ]
        )


# @rfm.simple_test
class CompileOpenFOAM(rfm.CompileOnlyRegressionTest):
    """Test compilation of OpenFoam"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    tags = {"compile"}

    build_system = "CustomBuild"
    build_locally = False

    openfoam_src = fixture(FetchOpenFOAM, scope="environment")

    num_nodes = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
    time_limit = "4h"

    @run_before("compile")
    def setup_build(self):
        """ "Prepare and run build on compute"""
        self.build_system.commands = [
            f"cp {self.openfoam_src.stagedir}/OpenFOAM-*.tar.gz .",
            f"cp {self.openfoam_src.stagedir}/ThirdParty-*.tar.gz .",
            "chmod u+x site/compile.sh",
            "./site/compile.sh",
        ]

    @sanity_function
    def validate_build(self):
        """Check that build completed successfully."""
        return sn.assert_not_found(r"ERROR", self.stderr)
