"""ReFrame tests for MLPerf HPC's CosmoFlow"""

import os
import reframe as rfm
import reframe.utility.sanity as sn

from mlperf_base import MLPerfBase


@rfm.simple_test
class CosmoFlowCPUtest(MLPerfBase):
    """Running CosmoFlow on CPU"""
    time_limit = "1h"
    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["PrgEnv-cray", "gcc"]
    extra_resources = {"qos": {"qos": "standard"}}
    modules = ["tensorflow/2.13.0"]

    @run_after("init")
    def setup_environment(self):
        """Setup environment"""
        if self.current_system.name in ["archer2"]:
            self.num_nodes = 1
            self.num_tasks = 8
            self.num_tasks_per_node = 8
            self.num_cpus_per_task = 16

        if self.current_system.name in ["cirrus"]:
            self.num_nodes = 4
            self.num_tasks = 8
            self.num_tasks_per_node = 2
            self.num_cpus_per_task = 18

    @performance_function("s", perf_key="total-epochs-time")
    def extract_time(self):
        """Return total epoch time"""
        return sn.extractsingle(
            r"Total epoch time:\s+(\S+)",
            self.stderr,
            tag=1,
            conv=float,
        )

    reference = {
        "archer2:compute": {"total-epochs-time": (446, -0.1, 0.1, "s")},
        "cirrus:compute": {"total-epochs-time": (446, -0.1, 0.1, "s")}}

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("All done!", self.stderr)

    @run_after('setup')
    def setup_job(self):
        """Set-up submission script"""
        part = self.current_partition.fullname

        if part == "archer2:compute":
            data_dir_prefix = "/work/z19/shared/mlperf-hpc/cosmoflow/mini/cosmoUniverse_2019_05_4parE_tf_v2_mini"
            self.env_vars = {
                "UCX_MEMTYPE_CACHE": "n",
                "MPICH_DPM_DIR": "${SLURM_SUBMIT_DIR}/dpmdir",
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "TF_ENABLE_ONEDNN_OPTS": "1"
            }
    # f"OMP_NUM_THREADS": "{num_cpus_per_task}",

        elif part == "cirrus:compute":
            data_dir_prefix = "/work/z04/shared/mlperf-hpc/cosmoflow/mini/cosmoUniverse_2019_05_4parE_tf_v2_mini"
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
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
            f"--data-dir {data_dir_prefix}"
        ]

    @run_before('run')
    def add_srun_options(self):
        """Add additional options to the job launcher"""
        part = self.current_partition.fullname
        self.job.launcher.options += [
            "--hint=nomultithread",
            "--distribution=block:block"
        ]
        if part == "archer2:compute":
            self.job.launcher.options += ["--cpu-freq=2250000"]
