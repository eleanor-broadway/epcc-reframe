#!/usr/bin/env python3

"""Reframe test for XCompact3D"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

# class XCompact3dFetchStable(AppsFetchBase):
#     """Test to fetch xcompact3d from github"""
#     executable = 'git clone'
#     executable_opts = [
#         f'https://github.com/xcompact3d/Incompact3d.git'
#     ]

#     local = True

#     valid_systems = ['*']
#     valid_prog_environs = ['']


# class Xcompact3dBuildStable(AppsCompileBase):
#     """Reframe base class for application compilation tests"""
#     descr = 'Build app'
#     build_system = ''
#     valid_systems = ['']
#     valid_prog_environs = ['']

@rfm.simple_test
class XCompact3DSourceBuild(rfm.CompileOnlyRegressionTest):
    """Build XCompact3D from source"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    # tags = {"performance", "applications"}

    # num_nodes = 64
    # num_tasks_per_node = 128
    # num_cpus_per_task = 1
    # num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task

    # env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    # time_limit = "1h"

    build_system = "CMake"
    modules = ["cmake"]
    local = True
    build_locally = True

    prebuild_cmds = [
        "git clone https://github.com/xcompact3d/Incompact3d.git",
        "cd Incompact3d",
        "git checkout v5.0",
    ]

    builddir = "build"
    executable = "build/bin/xcompact3d"
    max_concurreny = 8 

    # executable_opts = ["input-64.i3d"]
    # modules = ["cmake/3.29.4"]
    # reference = {"archer2:compute": {"steptime": (6.3, -0.2, 0.2, "seconds")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that build finished successfully"""
        return sn.assert_not_found("ERROR", self.stdout)



# @run_before("compile")
#     def prepare_build(self):
#         """Prepare the system to build"""

#         self.build_system.max_concurrency = 8
#         self.build_system.builddir = "build"
#         self.build_system.config_opts = [
#             "-DCMAKE_Fortran_COMPILER=ftn",
#             "-DCMAKE_C_COMPILER=cc",
#             "-DQE_ENABLE_SCALAPACK=ON",
#             "-DQE_ENABLE_HDF5=ON",
#             '-DCMAKE_Fortran_FLAGS="-O3 -g \
#                 -fallow-argument-mismatch -fopenmp -ffpe-summary=none"',
#         ]

#     @sanity_function
#     def sanity_check_build(self):
#         """Ensure build completed without errors"""
#         return sn.assert_not_found("ERROR", self.stderr)


    # @performance_function("seconds", perf_key="performance")
    # def extract_perf(self):
    #     """Extract performance value to compare with reference value"""
    #     return sn.extractsingle(
    #         r"Averaged time per step \(s\):\s+(?P<steptime>\S+)",
    #         self.stdout,
    #         "steptime",
    #         float,
    #     )



# Instructions for building xcompact3d: 

# module swap PrgEnv-cray PrgEnv-gnu
# module load cmake 

# git clone https://github.com/xcompact3d/Incompact3d.git
# cd Incompact3d
# git checkout v5.0 
# mkdir build 
# cd build 
# cmake .. 
# make -j 8 



# cmake -S . -B build
# cd build 
# cmake --build . -j 8

# Executable in build/bin/xcompact3d 