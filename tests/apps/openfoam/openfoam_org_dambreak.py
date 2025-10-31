"""ReFrame test for OpenFOAM DamBreak"""

import os
import reframe as rfm
import reframe.utility.sanity as sn

from openfoam_org_base import OpenFOAMBase
from openfoam_org_build import CompileOpenFOAM


class OpenFOAMDamBreakBase(OpenFOAMBase):
    """OpenFOAM DamBreak test base class"""

    num_tasks_per_node = 1
    num_cpus_per_task = 128
    time_limit = "10m"
    freq = parameter(["2250000", "2000000"])

    @run_after("init")
    def setup_params(self):
        """sets up extra parameters"""
        if self.current_system.name in ["archer2"]:
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "OMP_PLACES": "cores",
                "SLURM_CPU_FREQ_REQ": self.freq,
            }

    @run_before("run")
    def setup_testcase(self):
        """set up test case"""
        self.prerun_cmds = [
            "source ${FOAM_INSTALL_DIR}/etc/bashrc",
            "cp -r ${FOAM_INSTALL_DIR}/tutorials/multiphase/interFoam/laminar/damBreak/damBreak .",
            "cd damBreak",
            "blockMesh",
            "cp 0/alpha.water.orig 0/alpha.water",
            "setFields",
            "which interFoam",
        ]

    @run_before("performance")
    def set_reference(self):
        """Changes reference values"""
        if self.current_system.name in ["archer2"]:
            # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
            self.reference["archer2:compute:performance"] = self.reference_performance[self.freq]


class OpenFOAMDamBreakOneNode(OpenFOAMDamBreakBase):
    """OpenFOAM DamBreak base test on 1 node"""

    executable = "interFoam"
    executable_opts = ("").split()
    modules = [f"openfoam/org/v{OpenFOAMBase.version}"]

    num_tasks = 1

    reference_performance = {
        "2000000": (6, -0.1, 0.1, "seconds"),
        "2250000": (3.6, -0.1, 0.1, "seconds"),
    }


@rfm.simple_test
class OpenFOAMDamBreakOneNodeModule(OpenFOAMDamBreakOneNode):
    """OpenFOAM DamBreak test on 1 node with module"""

    executable = "interFoam"
    modules = [f"openfoam/org/v{OpenFOAMBase.version}"]


@rfm.simple_test
class OpenFOAMDamBreakOneNodeBuild(OpenFOAMDamBreakOneNode):
    """OpenFOAM DamBreak test on 1 node with reframe source build"""

    interfoam_binary = fixture(CompileOpenFOAM, scope="environment")

    @run_after("setup")
    def setup_extra_params(self):
        """sets up extra parameters"""
        super().setup_params()
        self.env_vars.update(
            {"FOAM_INSTALL_DIR": os.path.join(self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}")}
        )

    @run_after("setup")
    def set_executable(self):
        """Sets up executable"""
        self.executable = os.path.join(
            self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}/platforms/crayGccDPInt32Opt/bin/interFoam"
        )


class OpenFOAMDamBreakParallel(OpenFOAMDamBreakBase):
    """OpenFOAM DamBreak base test on 4 nodes"""

    num_tasks = 4
    executable_opts = ("-parallel").split()

    reference_performance = {
        "2000000": (5, -0.5, 0.5, "seconds"),
        "2250000": (5, -0.5, 0.5, "seconds"),
    }

    @run_before("run")
    def setup_testcase(self):
        """Set up test case"""
        super().setup_testcase()
        self.prerun_cmds = [*self.prerun_cmds, "decomposePar"]

    @sanity_function
    def assert_finished_parallel(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Finalising parallel run", self.stdout)


@rfm.simple_test
class OpenFOAMDamBreakParallelModule(OpenFOAMDamBreakParallel):
    """OpenFOAM DamBreak test on 4 nodes with module"""

    executable = "interFoam"
    modules = [f"openfoam/org/v{OpenFOAMBase.version}"]


@rfm.simple_test
class OpenFOAMDamBreakParallelBuild(OpenFOAMDamBreakParallel):
    """OpenFOAM DamBreak test on 4 nodes with reframe source build"""

    interfoam_binary = fixture(CompileOpenFOAM, scope="environment")

    @run_after("setup")
    def setup_extra_params(self):
        """sets up extra parameters"""
        super().setup_params()
        self.env_vars.update(
            {"FOAM_INSTALL_DIR": os.path.join(self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}")}
        )

    @run_after("setup")
    def set_executable(self):
        """Sets up executable"""
        self.executable = os.path.join(
            self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}/platforms/crayGccDPInt32Opt/bin/interFoam"
        )
