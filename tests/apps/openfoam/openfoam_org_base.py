"""Base class for OpenFoam.org tests"""

import reframe as rfm
import reframe.utility.sanity as sn


class OpenFOAMBase(rfm.RunOnlyRegressionTest):
    """ReFrame OpenFOAM test base class"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["openfoam/org/v10.20230119"]
    maintainers = ["e.broadway@epcc.ed.ac.uk", "j.richings@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications", "performance"}

    # Default reference value to validate run with
    # reference = {
    #     "archer2:compute": {"performance": (6, -0.05, 0.05, "seconds")},
    # }

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

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("End", self.stdout)

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"ExecutionTime\s+=\s+(?P<time>\d+.?\d*\s+)s\s+ClockTime\s+=\s+\d*\s+s\n\nEnd",
            self.stdout,
            "time",
            float,
        )
