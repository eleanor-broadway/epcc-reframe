#!/usr/bin/env python3

"""Resnet50 tests for GPUs"""

import reframe as rfm

from resnet_base import ResNet50BaseCheck


@rfm.simple_test
class ResNet50GPUBenchmark(ResNet50BaseCheck):
    """Restnet50 test class for GPUs"""

    valid_prog_environs = ["Default", "rocm-PrgEnv-gnu"]
    valid_systems = ["cirrus:compute-gpu", "archer2:compute-gpu-torch"]
    descr = "ResNet50 GPU Benchmark"

    num_tasks = None
    num_gpus = parameter([4])
    # Due to memory, Cirrus is limited to a lbs of 2
    # lbs = parameter([8])

    time_limit = "1h"
    num_nodes = 1

    @run_after("init")
    def setup_systems(self):
        """Environment setup"""
        if self.current_system.name in ["archer2"]:
            self.executable = ""
            self.extra_resources = {
                "qos": {"qos": "gpu-exc"},
                "gpu": {"num_gpus_per_node": str(self.num_gpus)},
            }
            self.prerun_cmds = [
                'eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"',
                "conda activate mlperf-torch-rocm",
            ]
            self.env_vars = {
                "OMP_NUM_THREADS": "8",
                "LD_LIBRARY_PATH": "$CRAY_MPICH_ROOTDIR/gtl/lib/:$LD_LIBRARY_PATH",
                "LD_PRELOAD": "$CRAY_MPICH_ROOTDIR/gtl/lib/libmpi_gtl_hsa.so:$LD_PRELOAD",
                "HOME": "$PWD",
            }
            self.executable_opts = [
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py",
                "--config",
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/configs/archer2benchmark_config.yaml",
                "--device",
                "cuda",
                "-lbs",
                "8",
                "--t_subset_size",
                "2048",
                "--v_subset_size",
                "512",
            ]

        elif self.current_system.name in ["cirrus"]:
            # self.executable_opts[2] = (
            #     "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/configs/cirrusbenchmark_config.yaml",
            # )
            self.executable = "python"
            self.extra_resources = {
                "qos": {"qos": "gpu"},
            }
            self.modules = ["openmpi/4.1.6-cuda-11.6"]
            self.prerun_cmds = [
                'eval "$(/work/z04/shared/ebroadwa/miniconda3/bin/conda shell.bash hook)"',
                "conda activate torch_mlperf",
            ]
            self.env_vars = {
                "OMP_NUM_THREADS": "5",
                "SRUN_CPUS_PER_TASK": "5",
                "OMPI_MCA_mpi_warn_on_fork": "0",
            }
            self.executable_opts = [
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py",
                "--config",
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/configs/cirrusbenchmark_config.yaml",
                "--device",
                "cuda",
                "-lbs",
                "2",
                "--t_subset_size",
                "2048",
                "--v_subset_size",
                "512",
            ]

    @run_before("run")
    def set_task_distribution(self):
        """Setup task distribution"""
        if self.num_gpus <= 4:
            self.num_nodes = 1
        else:
            if self.num_gpus / 4 - float(self.num_gpus // 4) == 0:
                self.num_nodes = self.num_gpus // 4
            else:
                self.num_nodes = self.num_nodes // 4 + 1

        if self.current_system.name in ["cirrus"]:
            self.job.options = [
                f"--nodes={self.num_nodes}",
                "--exclusive",
                f"--gres=gpu:{self.num_gpus if self.num_gpus <= 4 else 4}",
            ]  # make sure you change ntasks in PARAMS
        elif self.current_system.name in ["archer2"]:
            self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        if self.current_system.name in ["cirrus"]:
            self.job.launcher.options.append(
                f"--ntasks={self.num_gpus} --tasks-per-node={self.num_gpus if self.num_gpus <= 4 else 4}"
            )