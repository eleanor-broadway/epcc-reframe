"""Build MLPerf Env"""

import reframe as rfm
import reframe.utility.sanity as sn
from pytorch_base import PyTorchBaseEnvironment

class MLPerfEnvBuild(rfm.CompileOnlyRegressionTest): 
    #  Build system could be spack 
    build_system = "CustomBuild" 
    # Could we make this generic i.e. pull the version in from the base? 
    modules = ["pytorch/1.13.1-gpu"]
    local = True
    build_locally = True


    @run_before('compile')
    def setup_build(self):
        self.build_system.commands = [
            './build_python_env.sh',
            # Could add a clone repo here, if this env is for setting up mlperf? 
        ]

    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("ERROR", self.stderr)
