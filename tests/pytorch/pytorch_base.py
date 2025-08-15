"""ReFrame Base PyTorch"""

import reframe as rfm
import reframe.utility.sanity as sn 


class PyTorchBaseEnvironment(rfm.RunOnlyRegressionTest):
    """Definition of functions used for all PyTorch ReFrame tests"""

    maintainers = ["e.broadway@epcc.ed.ac.uk"]
    strict_check = True
    valid_systems = ["archer2:compute-gpu"]
    valid_prog_environs = ["PrgEnv-cray"]

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("success.", self.stdout)
