# """Test MLPerf DeepCAM"""

# import reframe as rfm
# import reframe.utility.sanity as sn
# from pytorch_base import PyTorchBaseEnvironment
# from mlperf_build import MLPerfEnvBuild

# @rfm.simple_test
# class MLPerfDeepCAMARCHER2(MLPerfEnvBuild):
#     """Base class to run the DeepCAM Benchmark on ARCHER2"""
#     num_tasks = None
#     time_limit = "1h"
#     num_nodes = 1
#     num_gpus = parameter([4])

#     @run_after("init")
#     def setup_systems(self):
#         """Setup environment"""
#         self.executable = ""
#         self.extra_resources = {
#             "qos": {"qos": "gpu-exc"},
#             "gpu": {"num_gpus_per_node": str(self.num_gpus)},
#         }
#         self.prerun_cmds = [
#             'export HOME=${HOME/home/work}',
#             'source ${HOME/home/work}/pyenvs/mlperf-pt-gpu/bin/activate',
#             'git clone https://github.com/mlcommons/hpc',
#             'cd hpc/deepcam/src/deepCam/'
#         ]
#         self.env_vars = {
#             "OMP_NUM_THREADS": "1",
#         }
#         self.executable_opts = [
#             "train.py",
#             '--wireup_method "nccl-slurm"',
#             '--data_dir_prefix /work/z19/shared/mlperf-hpc/deepcam/mini', 
#             '--local_batch_size 8', 
#             '--max_epochs 5'
#         ]
