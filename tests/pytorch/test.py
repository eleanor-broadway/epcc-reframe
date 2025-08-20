"""ReFrame Tests for PyTorch"""

import reframe as rfm
import reframe.utility.sanity as sn

class PyTorchBaseEnvironment(rfm.RunOnlyRegressionTest):
    """Common elements for PyTorch tests ---> is this actually MLPerf? i.e. with logging""" 

    valid_systems = ["archer2:compute-gpu"]
    valid_prog_environs = ["rocm-PrgEnv-cray"]

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("success", self.stdout)


@rfm.simple_test
class DeepCAMtest(PyTorchBaseEnvironment):
    """Running DeepCAM on GPU"""
    num_tasks = None
    num_nodes = 1
    num_gpus = 4
    time_limit = "1h"

    # Currently set-up for ARCHER2 but should be easy to extend 
    # Very dependant on 
    # (1) Source files being accessible (need to edit utils/bnstats.py for CPU)
    # (2) Python environment already existing and being installed 
    # @run_after("init")
    # def setup_source(self): 
    #     """Ideally this would be shared for all MLPerf tests"""
        # get source code and put it somewhere discoverable? 
        # https://reframe-hpc.readthedocs.io/en/stable/tutorial.html#multi-node-tests
    # Also need to consider performance testing - can I include my edits? patch? 

    @run_after("init", always_last=True)
    def setup_systems(self):
        self.executable = "python"
        self.executable_opts = {"/work/z19/z19/eleanorb/reframe/hpc/deepcam/src/deepCam/train.py",
            "--wireup_method nccl-slurm",
            "--run_tag reframe",
            "--output_dir $PWD",
            "--data_dir_prefix /work/z19/shared/mlperf-hpc/deepcam/mini",
            "--local_batch_size 8",
            "--max_epochs 5"
        }
        self.extra_resources = {
            "qos": {"qos": "gpu-exc"},
            "gpu": {"num_gpus_per_node": str(self.num_gpus)},
        }
        self.env_vars = {
            "OMP_NUM_THREADS": "1",
            "HOME": "${HOME/home/work}",
            "JOB_OUTPUT_PATH": "./results/${SLURM_JOB_ID}"
        }
        self.prerun_cmds = {
            "source ${HOME/home/work}/pyenvs/mlperf-pt-gpu/bin/activate",
            "mkdir -p ${JOB_OUTPUT_PATH}/logs" 
        }

    @run_before("run")
    def set_task_distribution(self):
        self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]
