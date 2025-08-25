import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

class fetch_mlperf_hpc_benchmarks(rfm.RunOnlyRegressionTest): 
    local = True
    executable = " "

    @run_before('run')    
    def prepare_deepcam(self):
        repo_dir = os.path.join(self.stagedir, "hpc")
        target_dir = os.path.join(repo_dir, "deepcam", "src", "deepCam")

        self.prerun_cmds = [
            f"git clone https://github.com/mlcommons/hpc.git {repo_dir}",
            f"cp deepcam-modified-train.py {target_dir}/train.py",
            f"sed -i 's/torch\\.cuda\\.synchronize()/if torch.cuda.is_available(): torch.cuda.synchronize()/' {target_dir}/utils/bnstats.py",
        ]
    
    @sanity_function
    def sanity_check_build(self):
        return sn.assert_not_found("ERROR", self.stderr)


class BuildMLPerfPytorchEnv(rfm.CompileOnlyRegressionTest):
    build_system = "CustomBuild"
    @run_before("compile")
    def prepare_env(self):
        part = self.current_partition.fullname

        # Check if this is still needed: 
        if part == "cirrus:compute-gpu": 
            self.prerun_cmds = ["module unload openmpi"]
        if part in ("archer2:compute-gpu", "cirrus:compute-gpu"):
            self.modules = ["pytorch/1.13.1-gpu"]
            self.env_vars["PYVENV_NAME"] = "reframe-mlperf-gpu"
        elif part == "archer2:compute":
            self.modules = ["pytorch/1.13.0a0"]
            self.env_vars["PYVENV_NAME"] = "reframe-mlperf-cpu"

        self.build_system.commands = [
            "chmod u+x build_pytorch_env.sh",
            "./build_pytorch_env.sh"
        ]

    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("ERROR", self.stderr)
