import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

from mlperf_build import fetch_mlperf_hpc_benchmarks
from mlperf_build import BuildMLPerfPytorchEnv

class MLPerfBase(rfm.RunOnlyRegressionTest):
    executable = "python"
    mlperf_benchmarks = fixture(fetch_mlperf_hpc_benchmarks, scope='session')

class DeepCAMBase(MLPerfBase):

    pytorch_env = fixture(BuildMLPerfPytorchEnv, scope='environment')
    
    @performance_function("s", perf_key="epoch-time")
    def extract_time(self): 
        return sn.extractsingle(r'Time For Epoch 5 : (\S+) s',
            self.stdout,
            tag=1, 
            conv=float,
        )

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("success", self.stdout)
