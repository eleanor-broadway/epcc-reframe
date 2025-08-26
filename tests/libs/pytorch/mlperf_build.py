"""Downloading and building python environments for MLPerf HPC"""

import os
import reframe as rfm
import reframe.utility.sanity as sn


class MLPerfHPCFetchBenchmarks(rfm.RunOnlyRegressionTest):
    """Fetching the MLPerf HPC Benchmark Suite"""

    local = True
    executable = " "

    @run_before("run")
    def prepare_deepcam(self):
        """Clone the repository and and make modifications"""
        repo_dir = os.path.join(self.stagedir, "hpc")
        target_dir = os.path.join(repo_dir, "deepcam", "src", "deepCam")

        self.prerun_cmds = [
            f"git clone https://github.com/mlcommons/hpc.git {repo_dir}",
            f"cp deepcam-modified-train.txt {target_dir}/train.py",
            (
                "sed -i 's/torch\\.cuda\\.synchronize()/"
                "if torch.cuda.is_available(): torch.cuda.synchronize()/' "
                f"{target_dir}/utils/bnstats.py"
            ),
            # f"sed -i 's/torch\\.cuda\\.synchronize()/if torch.cuda.is_available():
            # torch.cuda.synchronize()/' {target_dir}/utils/bnstats.py",
        ]

    @sanity_function
    def sanity_check_build(self):
        """Sanity checks"""
        return sn.assert_not_found("ERROR", self.stderr)


class BuildMLPerfPytorchEnv(rfm.CompileOnlyRegressionTest):
    """Build a Python environment for MLPerf HPC tests, based on pytorch module"""

    build_system = "CustomBuild"

    @run_before("compile")
    def prepare_env(self):
        """Load the correct modules and name env"""
        part = self.current_partition.fullname
        if part in ("archer2:compute-gpu", "cirrus:compute-gpu"):
            self.modules = ["pytorch/1.13.1-gpu"]
            self.env_vars["PYVENV_NAME"] = "reframe-mlperf-gpu"
        elif part == "archer2:compute":
            self.modules = ["pytorch/1.13.0a0"]
            self.env_vars["PYVENV_NAME"] = "reframe-mlperf-cpu"

        self.build_system.commands = ["chmod u+x build_pytorch_env.sh", "./build_pytorch_env.sh"]

    @sanity_function
    def sanity_check_build(self):
        """Sanity checks"""
        return sn.assert_not_found("ERROR", self.stderr)
