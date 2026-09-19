from enum import Enum


class WorkloadType(str, Enum):
    """
    Types of workloads supported by GreenCloud Optimizer.
    """

    BATCH = "batch"
    REAL_TIME = "real_time"
    MACHINE_LEARNING = "machine_learning"
    HPC = "hpc"