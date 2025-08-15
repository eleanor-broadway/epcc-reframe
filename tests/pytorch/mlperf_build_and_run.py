"""Build MLPerf Env"""

import reframe as rfm
import reframe.utility.sanity as sn
from pytorch_base import PyTorchBaseEnvironment

@rfm.simple_test
class MLPerfDeepCAMBuildAndRun(PyTorchBaseEnvironment):
    """Build MLPerf env, then run DeepCAM benchmark"""
    num_nodes = 1
    num_gpus = parameter([4])
    time_limit = "1h"

    # === Compile phase ===
    build_system = "CustomBuild"
    modules = ["pytorch/1.13.1-gpu"]
    local = True
    build_locally = True

    @rfm.run_before("compile")
    def setup_build(self):
        self.build_system.commands = [
            './build_python_env.sh'
        ]

    @rfm.sanity_function
    def sanity_check_build(self):
        return sn.assert_not_found("ERROR", self.stderr)

    # === Run phase ===
    @rfm.run_after("compile")
    def setup_run(self):
        self.executable = "python"
        self.executable_opts = [
            "train.py",
            '--wireup_method', "nccl-slurm",
            '--data_dir_prefix', '/work/z19/shared/mlperf-hpc/deepcam/mini',
            '--local_batch_size', '8',
            '--max_epochs', '5'
        ]
        self.extra_resources = {
            "qos": {"qos": "gpu-exc"},
            "gpu": {"num_gpus_per_node": str(self.num_gpus)},
        }
        self.prerun_cmds = [
            'export HOME=${HOME/home/work}',
            'source ${HOME/home/work}/pyenvs/mlperf-pt-gpu/bin/activate',
            'git clone https://github.com/mlcommons/hpc',
            'cd hpc/deepcam/src/deepCam/'
        ]
        self.env_vars = {"OMP_NUM_THREADS": "1"}