"""ReFrame test for OpenFOAM DamBreak"""

import reframe as rfm
import reframe.utility.sanity as sn

from openfoam_org_base import OpenFOAMBase


# Write a base class for the test that includes freq set-up stuff: 
    # @run_after("init")
    # def setup_params(self):
    #     """sets up extra parameters"""
    #     if self.current_system.name in ["archer2"]:
    #         self.env_vars = {
    #             "OMP_NUM_THREADS": str(self.num_cpus_per_task),
    #             "OMP_PLACES": "cores",
    #             "SLURM_CPU_FREQ_REQ": self.freq,
    #         }

    # modules = [f"openfoam/org/{openfoam_org_version}"]



@rfm.simple_test
class OpenFOAMDamBreak(OpenFOAMBase):
    """OpenFOAM Dam break test"""

    executable = "interFoam"
    executable_opts = ("").split()
    modules = [f"openfoam/org/{OpenFOAMBase.openfoam_org_version}"]

    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 128
    time_limit = "10m"

    freq = parameter(["2250000", "2000000"])
    reference_performance = {
        "2000000": (6, -0.1, 0.1, "seconds"),
        "2250000": (3.6, -0.1, 0.1, "seconds"),
    }

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
        ]

    @run_before("performance")
    def set_reference(self):
        """Changes reference values"""
        if self.current_system.name in ["archer2"]:
            # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
            self.reference["archer2:compute:performance"] = self.reference_performance[self.freq]


@rfm.simple_test
class OpenFOAMDamBreakParallel(OpenFOAMBase):
    """OpenFOAM DamBreak test"""

    executable = "interFoam"
    executable_opts = ("-parallel").split()
    modules = [f"openfoam/org/{OpenFOAMBase.openfoam_org_version}"]

    num_tasks = 4
    num_tasks_per_node = 1
    num_cpus_per_task = 128
    time_limit = "10m"

    freq = parameter(["2250000", "2000000"])
    reference_performance = {
        "2000000": (5, -0.5, 0.5, "seconds"),
        "2250000": (5, -0.5, 0.5, "seconds"),
    }

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
            "decomposePar",
        ]

    @sanity_function
    def assert_finished_parallel(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Finalising parallel run", self.stdout)

    @run_before("performance")
    def set_reference(self):
        """Changes reference values"""
        if self.current_system.name in ["archer2"]:
            # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
            self.reference["archer2:compute:performance"] = self.reference_performance[self.freq]
