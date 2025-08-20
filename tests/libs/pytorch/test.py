"""ReFrame Tests for PyTorch"""

# To dos: 
# Improve the file structure (i.e. base, build, test)
# ARCHER2 CPU (currently testing outside of reframe)
# Add a build python environment test (currently testing to see if CPU uses same)
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
        f"sed -i 's/logger):/logger, writer):/' {target_dir}/driver/trainer.py",
        f"sed -i '/return step/i\\    writer.add_scalar(\"Accuracy/train\", iou_avg_train, epoch+1)\\n    writer.add_scalar(\"Loss/train\", loss_avg_train, epoch+1)' {target_dir}/driver/trainer.py"
    ]
    
    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("ERROR", self.stderr)


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
            "--run_tag reframe",
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
            "source ${HOME/home/work}/pyenvs/mlperf-pt-gpu/bin/activate",
            "mkdir -p ${JOB_OUTPUT_PATH}/logs" 
        ]

    @run_before("run")
    def set_task_distribution(self):
        self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]
