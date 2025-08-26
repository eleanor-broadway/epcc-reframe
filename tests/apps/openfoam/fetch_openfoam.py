#!/usr/bin/env python3

"""Reframe test for OpenFoam"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
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
        """Validate openFoam Downloaded"""
        return sn.path_isfile(f"ThirdParty-{self.version}.tgz") and sn.path_isfile(f"OpenFOAM-{self.version}.tgz")
