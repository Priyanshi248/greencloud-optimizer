import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.enums.provider import CloudProviderType
from app.enums.workload import WorkloadType
from app.models.carbon_data import CarbonData
from app.models.cloud_provider import CloudProvider
from app.models.workload import Workload



async def seed_database():
    """
    Insert prototype cloud-provider, carbon and workload data.

    The values are simulated data for demonstrating the optimizer.
    They are not live measurements from cloud providers.
    """

    async with AsyncSessionLocal() as db:

        # ---------------------------------------------------------
        # Check whether seed data already exists
        # ---------------------------------------------------------

        existing_provider = await db.execute(
            select(CloudProvider).limit(1)
        )

        if existing_provider.scalar_one_or_none():
            print("Seed data already exists.")
            return

        # ---------------------------------------------------------
        # Cloud providers
        # ---------------------------------------------------------

        providers = [
            CloudProvider(
                provider_type=CloudProviderType.AWS,
                provider_name="AWS",
                region="us-west-2",
                cpu_cores=32,
                memory_gb=128,
                storage_gb=1000,
                cpu_power_efficiency=0.45,
                dcie=0.80,
                cost_per_cpu_hour=0.30,
                is_active=True,
                execution_time_factor=1.10,
            ),
            CloudProvider(
                provider_type=CloudProviderType.AZURE,
                provider_name="Azure",
                region="sweden-central",
                cpu_cores=32,
                memory_gb=128,
                storage_gb=1000,
                cpu_power_efficiency=0.40,
                dcie=0.85,
                cost_per_cpu_hour=0.25,
                is_active=True,
                execution_time_factor=0.90,
            ),
            CloudProvider(
                provider_type=CloudProviderType.GCP,
                provider_name="GCP",
                region="us-central1",
                cpu_cores=32,
                memory_gb=128,
                storage_gb=1000,
                cpu_power_efficiency=0.50,
                dcie=0.75,
                cost_per_cpu_hour=0.20,
                is_active=True,
                execution_time_factor=1.00,
            ),
        ]

        db.add_all(providers)

        await db.flush()

        # ---------------------------------------------------------
        # Carbon intensity
        # ---------------------------------------------------------

        measurement_time = datetime.now(timezone.utc)

        carbon_records = [
            CarbonData(
                provider_id=providers[0].id,
                carbon_intensity=0.20,
                measurement_time=measurement_time,
                source="prototype_simulation",
            ),
            CarbonData(
                provider_id=providers[1].id,
                carbon_intensity=0.05,
                measurement_time=measurement_time,
                source="prototype_simulation",
            ),
            CarbonData(
                provider_id=providers[2].id,
                carbon_intensity=0.35,
                measurement_time=measurement_time,
                source="prototype_simulation",
            ),
        ]

        db.add_all(carbon_records)

        # ---------------------------------------------------------
        # Example workload
        # ---------------------------------------------------------

        workload = Workload(
            name="ML Training Demo",
            workload_type=WorkloadType.MACHINE_LEARNING,
            cpu_cores=8,
            memory_gb=32,
            storage_gb=100,
            runtime_minutes=60,
            deadline_minutes=120,
            data_transfer_gb=10,
        )

        db.add(workload)

        await db.commit()

        print("Seed data inserted successfully.")
        print(f"Workload ID: {workload.id}")


if __name__ == "__main__":
    asyncio.run(seed_database())