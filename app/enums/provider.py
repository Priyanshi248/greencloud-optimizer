from enum import Enum


class CloudProviderType(str, Enum):
    """
    Cloud providers supported by the GreenCloud Optimizer.
    """

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    PRIVATE = "private"