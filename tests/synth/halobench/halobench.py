#!/usr/bin/env python3
"""
HaloBench Input/Output test

Simple MPI benchmark of various 3D halo swapping approaches.

The code sets up a 3D array of processes and swaps halo data up and down in
all three directions. It uses a number of different methods - the aim is to
see which is fastest.

Please note that the code runs three times. The first two times are warm-up;
the third one is reported by the performance test.

Function `extractall` returns an array of 24 elements [0:23]
We use the last 8 elements, i.e., [16:23]

Eight tests:
1. Sendrecv
2. Redblack
3. Isend / Recv / Wait
4. Irecv / Send / Wait
5. Irecv / Isend / Wait (pairwise)
6. Irecv / Isend / Waitall
7. Persistent / Startall / Waitall
8. Neighbourhood Collective

# Based on work by:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause
"""

import os

import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class halobench_build_test(rfm.RegressionTest):

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    
    build_system = 'Make'
    sourcesdir = 'https://github.com/davidhenty/halobench.git'
    executable = './halobench'
    
    num_nodes = 8
    num_tasks = 1024
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    time_limit = "3m"
    
    reference = {
        'archer2:compute': {
            'sendrecv':                     (668, -0.1, 0.1, 'MB/s'),
            'redblack':                     (858, -0.1, 0.1, 'MB/s'),
            'isend_recv_wait':              (676, -0.1, 0.1, 'MB/s'),
            'irecv_send_wait':              (672, -0.1, 0.1, 'MB/s'),
            'irecv_isend_wait_pairwise':    (671, -0.1, 0.1, 'MB/s'),
            'irecv_isend_waitall':         (1075, -0.1, 0.1, 'MB/s'),
            'persistent_startall_waitall': (1076, -0.1, 0.1, 'MB/s'),
            'neighbourhood_collective':    (1074, -0.1, 0.1, 'MB/s')
        }
    }

    @run_before('compile')
    def prepare_build(self):
        self.build_system.makefile = "Makefile-archer2"

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Finished', self.stdout)

    @performance_function('MB/s')
    def sendrecv(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[16]

    @performance_function('MB/s')
    def redblack(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[17]

    @performance_function('MB/s')
    def isend_recv_wait(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[18]

    @performance_function('MB/s')
    def irecv_send_wait(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[19]

    @performance_function('MB/s')
    def irecv_isend_wait_pairwise(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[20]

    @performance_function('MB/s')
    def irecv_isend_waitall(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[21]

    @performance_function('MB/s')
    def persistent_startall_waitall(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[22]

    @performance_function('MB/s')
    def neighbourhood_collective(self):
        return sn.extractall(r'bwidth\s=\s+(\S+)', self.stdout, 1, float)[23]
