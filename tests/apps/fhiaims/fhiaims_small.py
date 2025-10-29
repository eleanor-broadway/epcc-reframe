"""ReFrame Tests for FHI-aims"""

import reframe as rfm
from fhiaims_base import FHIaimsBase


class FHIaimsAcLysAla19HBenchmark(FHIaimsBase):
    """Base class to run the AUSURF112 QE Smoke test on ARCHER2"""

    n_nodes = 2
    num_tasks = 256
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    time_limit = "20m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}
    extra_resources = {"qos": {"qos": "standard"}}

    if FHIaimsBase.fhiaims_version == "240920.0":
        reference = {"archer2:compute": {"walltime": (299.9, -0.1, 0.1, "s")}}


@rfm.simple_test
class FHIaimsAcLysAla19HBenchmarkModule(FHIaimsAcLysAla19HBenchmark):
    """Run test with module"""

    tags = {"applications", "performance"}
    executable = "aims.mpi.x"
    modules = [f"fhiaims/{FHIaimsBase.fhiaims_version}"]
