"""Simple Test for XCompact3D"""

import reframe as rfm
from xcompact3d_base import XCompact3DBaseEnvironment
from xcompact3d_build import XCompact3DSourceBuild


@rfm.simple_test
class XCompact3DSmallTest(XCompact3DBaseEnvironment):
    """Using the source build, run a XCompact3D test on ARCHER2"""

    xcompact3d_binary = fixture(XCompact3DSourceBuild, scope="environment")
    tags = {"applications", "performance"}

    num_nodes = 8
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task

    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    time_limit = "1h"
    executable_opts = ["input-8.i3d"]

    reference = {"archer2:compute": {"steptime": (6.3, -0.2, 0.2, "seconds")}}

    # modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]

    # Is this needed? Executable is in "default" location I think...
    @run_after("setup")
    def set_executable(self):
        """Sets up executable"""
        self.executable = os.path.join(
            self.xcompact3d_binary.stagedir, "bin/xcompact3d"
        )