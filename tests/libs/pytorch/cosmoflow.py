import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from mlperf_base import MLPerfBase

@rfm.simple_test
class CosmoFlowCPUtest(MLPerfBase):
    """Running CosmoFlow on CPU"""
    num_nodes = 1
    num_tasks_per_node = 8
    num_cpus_per_task = 16
    num_tasks = 8
    time_limit = "1h"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    extra_resources = {"qos": {"qos": "standard"}}
    modules = ["tensorflow/2.13.0"]
    reference = {"archer2:compute": {"total-epochs-time": (446, -0.1, 0.1, "s")}}

    @performance_function("s", perf_key="total-epochs-time")
    def extract_time(self): 
        return sn.extractsingle(r"Total epoch time:\s+(\S+)",
            self.stdout,
            tag=1, 
            conv=float,
        ) 

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("All done!", self.stderr)

    @run_after('setup')
    def setup_job(self):
        self.env_vars = {
            "UCX_MEMTYPE_CACHE": "n", 
            "SRUN_CPUS_PER_TASK": "${SLURM_CPUS_PER_TASK}",
            "MPICH_DPM_DIR": "${SLURM_SUBMIT_DIR}/dpmdir",
            "OMP_NUM_THREADS": "${SLURM_CPUS_PER_TASK}",
            "TF_ENABLE_ONEDNN_OPTS": "1"
        }
        train_script = os.path.join(
            self.mlperf_benchmarks.stagedir,
            "hpc", "cosmoflow", "train.py"
        )
        cosmo_config = os.path.join(
            self.mlperf_benchmarks.stagedir,
            "hpc", "cosmoflow", "configs", "cosmo.yaml"
        )
        self.executable_opts = [
            train_script,
            cosmo_config,
            "--distributed",
            "--omp-num-threads ${OMP_NUM_THREADS}",
            "--inter-threads 0",
            "--intra-threads 0",
            "--n-train 32", 
            "--n-valid 32",
            "--data-dir /work/z19/shared/mlperf-hpc/cosmoflow/mini/cosmoUniverse_2019_05_4parE_tf_v2_mini",
        ]

    @run_before('run')
    def add_srun_options(self):
        self.job.launcher.options += [
            "--cpu-freq=2250000",
            "--hint=nomultithread", 
            "--distribution=block:block"       
        ]
