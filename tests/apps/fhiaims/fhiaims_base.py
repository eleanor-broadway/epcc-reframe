"""ReFrame Base FHI-aims"""

import reframe as rfm
import reframe.utility.sanity as sn


class FHIaimsBase(rfm.RunOnlyRegressionTest):
    """Definition of functions used for all FHI-aims ReFrame tests"""

    fhiaims_version = "240920.0"
    maintainers = ["e.broadway@epcc.ed.ac.uk"]
    strict_check = True
    use_multithreading = False
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Have a nice day.", self.stdout)

    @performance_function("s", perf_key="walltime")
    def extract_walltime(self):
        """Extract walltime for performance check"""
        return sn.extractsingle(
            r"^\s*\|\s*Total time\s*:\s*(?P<cpu>\d+\.\d+)\s*s\s+(?P<walltime>\d+\.\d+)\s*s",
            self.stdout,
            "walltime",
            float,
        )
