"""ReFrame Tests for PyTorch"""

# To dos: 
# Check that the performance for 4 GPUs is inlined with the "proper" job script (concerned because of the lack of --ntasks etc after srun) - DONE! 
# Improve the file structure (i.e. base, build, test)
# ARCHER2 CPU (currently testing outside of reframe)
# Add a build python environment test (currently testing to see if CPU uses same)
#   Can we make the build script generic? i.e. is the process the same on Cirrus with only a module change?  
# Add a performance reference
# Linting to bring up to code

import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

@rfm.simple_test
class fetch_mlperf_hpc_benchmarks(rfm.CompileOnlyRegressionTest): 
    """Download mlcommons/hpc and prepare for deepcam test"""

    # Can this be done once and put in a common location? Or does it have to happen twice? 

    build_system = "CustomBuild"
    local = True
    valid_systems = ["archer2:compute-gpu"]
    valid_prog_environs = ["rocm-PrgEnv-cray"]

    @run_before("compile")
    def setup_build(self):
        """Setup build"""
        repo_dir = os.path.join(self.stagedir, "hpc")
        target_dir = os.path.join(repo_dir, "deepcam", "src", "deepCam")

        self.build_system.commands = [
            f"git clone https://github.com/mlcommons/hpc.git {repo_dir}",
            f"cp modified-train.py {target_dir}/train.py",
            f"sed -i 's/torch\\.cuda\\.synchronize()/if torch.cuda.is_available(): torch.cuda.synchronize()/' {target_dir}/utils/bnstats.py",
        ]
    
    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("ERROR", self.stderr)

@rfm.simple_test
class DeepCAMGPUtest(rfm.RunOnlyRegressionTest):
    """Running DeepCAM on GPU"""
    num_tasks = None
    num_nodes = 1
    num_gpus = 4
    time_limit = "1h"
    valid_systems = ["archer2:compute-gpu"]
    valid_prog_environs = ["rocm-PrgEnv-cray"]

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("success", self.stdout)

    @run_after('init')
    def add_dependencies(self):
        self.depends_on('fetch_mlperf_hpc_benchmarks', udeps.fully)

    @require_deps
    def setup_job(self, fetch_mlperf_hpc_benchmarks):
        mlperf_files = fetch_mlperf_hpc_benchmarks()
        train_script = os.path.join(
            mlperf_files.stagedir,
            "hpc", "deepcam", "src", "deepCam", "train.py"
        )
        self.executable = "python"
        self.executable_opts = [
            train_script,
            "--wireup_method nccl-slurm",
            "--run_tag reframe-gpu",
            "--output_dir ${JOB_OUTPUT_PATH}",
            "--data_dir_prefix /work/z19/shared/mlperf-hpc/deepcam/mini",
            "--local_batch_size 8",
            "--max_epochs 5"
        ]
        self.extra_resources = {
            "qos": {"qos": "gpu-exc"},
            "gpu": {"num_gpus_per_node": str(self.num_gpus)},
        }
        self.env_vars = {
            "OMP_NUM_THREADS": "1",
            "HOME": "${HOME/home/work}",
            "JOB_OUTPUT_PATH": "./results/${SLURM_JOB_ID}"
        }
        self.prerun_cmds = [
            "source ${HOME/home/work}/pyenvs/reframe-mlperf/bin/activate",
            "mkdir -p ${JOB_OUTPUT_PATH}/logs" 
        ]

    @run_before('run')
        def add_srun_options(self):
            # This appends custom options to the srun command
            self.job.launcher.options += [
                "--ntasks=4",
                "--tasks-per-node=4",
                "--hint=nomultithread,
            ]

    @run_before("run")
    def set_task_distribution(self):
        self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]


# #!/bin/bash
# #SBATCH --job-name="rfm_job"
# #SBATCH --output=rfm_job.out
# #SBATCH --error=rfm_job.err
# #SBATCH --time=1:0:0
# #SBATCH --partition=gpu
# #SBATCH --qos=gpu-exc
# #SBATCH --gres=gpu:4
# #SBATCH --nodes=1
# #SBATCH --exclusive
# module load PrgEnv-cray
# export OMP_NUM_THREADS=1
# export HOME=${HOME/home/work}
# export JOB_OUTPUT_PATH=./results/${SLURM_JOB_ID}
# source ${HOME/home/work}/pyenvs/mlperf-pt-gpu/bin/activate
# mkdir -p ${JOB_OUTPUT_PATH}/logs
# srun python /mnt/lustre/a2fs-work2/work/z19/z19/eleanorb/reframe/epcc-reframe/stage/archer2/compute-gpu/rocm-PrgEnv-cray/fetch_mlperf_hpc_benchmarks/hpc/deepcam/src/deepCam/train.py --wireup_method nccl-slurm --run_tag reframe --output_dir ${JOB_OUTPUT_PATH} --data_dir_prefix /work/z19/shared/mlperf-hpc/deepcam/mini --local_batch_size 8 --max_epochs 5
# 
@rfm.simple_test
class DeepCAMCPUtest(rfm.RunOnlyRegressionTest):
    """Running DeepCAM on CPU"""
    num_nodes = 4
    num_tasks_per_node = 8
    num_cpus_per_task = 16
    num_tasks = 32
    time_limit = "1h"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    extra_resources = {"qos": {"qos": "standard"}}

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("success", self.stdout)

    @run_after('init')
    def add_dependencies(self):
        self.depends_on('fetch_mlperf_hpc_benchmarks', udeps.fully)

    @require_deps
    def setup_job(self, fetch_mlperf_hpc_benchmarks):
        mlperf_files = fetch_mlperf_hpc_benchmarks()
        train_script = os.path.join(
            mlperf_files.stagedir,
            "hpc", "deepcam", "src", "deepCam", "train.py"
        )
        self.executable = "python"
        self.executable_opts = [
            train_script,
            "--wireup_method mpi",
            "--run_tag reframe-cpu",
            "--output_dir ${JOB_OUTPUT_PATH}",
            "--data_dir_prefix /work/z19/shared/mlperf-hpc/deepcam/mini",
            "--local_batch_size 1",
            "--max_epochs 5",
            "--seed ${SLURM_JOB_ID}",
        ]
        self.env_vars = {
            "OMP_NUM_THREADS": "${SLURM_CPUS_PER_TASK}",
            "HOME": "${HOME/home/work}",
            "JOB_OUTPUT_PATH": "./results/${SLURM_JOB_ID}"
            "SRUN_CPUS_PER_TASK": "${SLURM_CPUS_PER_TASK}"
        }
        self.prerun_cmds = [
            "source ${HOME/home/work}/pyenvs/reframe-mlperf-cpu/bin/activate",
            "mkdir -p ${JOB_OUTPUT_PATH}/logs" 
        ]

    # @run_before("run")
    # def set_task_distribution(self):
    #     self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]

    @run_before('run')
        def add_srun_options(self):
            # This appends custom options to the srun command
            # Update this to be variables... 
            self.job.launcher.options += [
                "--ntasks=32",
                "--tasks-per-node=8",
                "--hint=nomultithread,
            ]
