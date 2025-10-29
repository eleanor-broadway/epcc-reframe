#!/usr/bin/env python3

"""ReFrame test for cp2k"""

import reframe as rfm
import reframe.utility.sanity as sn


class OpenFOAMDamBreakBase(rfm.RunOnlyRegressionTest):
    """Base class for all DamBreak OpenFOAM tests"""

    modules = ["openfoam/org/v10.20230119"]
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    executable = "interFoam"
    extra_resources = {"qos": {"qos": "standard"}}
    keep_files = ["rfm_job.out"]

    maintainers = ["j.richings@epcc.ed.ac.uk", "e.broadway@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications", "performance"}

    freq = parameter(["2250000", "2000000"])

    # Reference value to validate run with
    reference = {
        "archer2:compute": {"performance": (6, -0.05, 0.05, "seconds")},
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


@rfm.simple_test
class OpenFOAMDamBreak(OpenFOAMDamBreakBase):

    executable_opts = ("").split()
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 128
    time_limit = "10m"

    reference_performance = {
        "2000000": (6, -0.1, 0.1, "seconds"),
        "2250000": (3.6, -0.1, 0.1, "seconds"),
    }

    # @run_after("init")
    # def setup_params(self):
    #     """sets up extra parameters"""
    #     self.descr += self.freq
    #     if self.current_system.name in ["archer2"]:
    #         self.env_vars = {
    #             "OMP_NUM_THREADS": str(self.num_cpus_per_task),
    #             "OMP_PLACES": "cores",
    #             "SLURM_CPU_FREQ_REQ": self.freq,
    #         }

    # @run_before("performance")
    # def set_reference(self):
    #     """Changes reference values"""
    #     if self.current_system.name in ["archer2"]:
    #         # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
    #         self.reference["archer2:compute:performance"] = self.reference_performance[self.freq]


@rfm.simple_test
class OpenFOAMDamBreakParallel(OpenFOAMDamBreakBase):

    executable_opts = ("-parallel").split()
    num_tasks = 4
    num_tasks_per_node = 1
    num_cpus_per_task = 128
    time_limit = "10m"

    reference_performance = {
        "2000000": (5, -0.5, 0.5, "seconds"),
        "2250000": (5, -0.5, 0.5, "seconds"),
    }

    # @run_after("init")
    # def setup_params(self):
    #     """sets up extra parameters"""
    #     self.descr += self.freq
    #     if self.current_system.name in ["archer2"]:
    #         self.env_vars = {
    #             "OMP_NUM_THREADS": str(self.num_cpus_per_task),
    #             "OMP_PLACES": "cores",
    #             "SLURM_CPU_FREQ_REQ": self.freq,
    #         }

    # @run_before("run")
    # def setup_testcase(self):
    #     """set up test case"""
    #     self.prerun_cmds = [
    #         "source ${FOAM_INSTALL_DIR}/etc/bashrc",
    #         "cp -r ${FOAM_INSTALL_DIR}/tutorials/multiphase/interFoam/laminar/damBreak/damBreak .",
    #         "cd damBreak",
    #         "blockMesh",
    #         "cp 0/alpha.water.orig 0/alpha.water",
    #         "setFields",
    #         "decomposePar",
    #     ]

    @run_before("run")
    def setup_testcase(self):
        """set up test case"""
        self.prerun_cmds = [
            "decomposePar"
        ]

    @sanity_function
    def assert_finished_parallel(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Finalising parallel run", self.keep_files[0])

    # @run_before("performance")
    # def set_reference(self):
    #     """Changes reference values"""
    #     if self.current_system.name in ["archer2"]:
    #         # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
    #         self.reference["archer2:compute:performance"] = self.reference_performance[self.freq]
