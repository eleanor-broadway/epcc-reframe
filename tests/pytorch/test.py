"""ReFrame Tests for PyTorch"""

import reframe as rfm
import reframe.utility.sanity as sn

class PyTorchBaseEnvironment(rfm.RunOnlyRegressionTest): 
    maintainers = ["e.broadway@epcc.ed.ac.uk"]
    strict_check = True
    use_multithreading = False
    valid_systems = ["archer2:compute-gpu"]
    valid_prog_environs = ["PrgEnv-cray"]

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("success", self.stdout)

@rfm.simple_test
class DeepCAMARCHER2GPUBase(PyTorchBaseEnvironment):
    time_limit = "1h"
    num_tasks = None
    num_nodes = 1
    num_gpus = parameter([4])
    executable = "python"

    # @run_after("init")
    # def setup_systems(self):
    #     """Setup environment"""
    #     if self.current_system.name in ["archer2"]:
    #         self.executable = "python"
    #         self.extra_resources = {
    #             "qos": {"qos": "gpu-exc"},
    #             "gpu": {"num_gpus_per_node": str(self.num_gpus)},
    #         }
    #         self.prerun_cmds = ['source ${HOME/home/work}/pyenvs/mlperf-pt-gpu/bin/activate']
    #         self.env_vars = {
    #             "OMP_NUM_THREADS": "1",
    #             "HOME": "${HOME/home/work}",
    #         }
    #         self.executable_opts = [
    #             "/work/z19/z19/eleanorb/reframe/hpc/deepcam/src/deepCam/train.py",
    #             "--wireup_method", "nccl-slurm",
    #             "--run_tag test",
    #             "--data_dir_prefix /work/z19/shared/mlperf-hpc/deepcam/mini",
    #             "--output_dir ${JOB_OUTPUT_PATH}",
    #             "--local_batch_size 8",
    #             "--max_epochs 5"
    #         ]

    # @run_before("run")
    # def set_task_distribution(self):
    #     """Setup task distribution"""
    #     if self.num_gpus <= 4:
    #         self.num_nodes = 1
    #     else:
    #         if self.num_gpus / 4 - float(self.num_gpus // 4) == 0:
    #             self.num_nodes = self.num_gpus // 4
    #         else:
    #             self.num_nodes = self.num_nodes // 4 + 1

    #     if self.current_system.name in ["cirrus"]:
    #         self.job.options = [
    #             f"--nodes={self.num_nodes}",
    #             "--exclusive",
    #             f"--gres=gpu:{self.num_gpus if self.num_gpus <= 4 else 4}",
    #         ]  # make sure you change ntasks in PARAMS
    #     elif self.current_system.name in ["archer2"]:
    #         self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]

