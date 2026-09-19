from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carbon_data import CarbonData


class CarbonService:
    """
    Provides carbon-intensity data for cloud providers.

    This service is responsible for retrieving environmental data.
    It does not decide which provider should be selected.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest_carbon_intensity(
        self,
        provider_id: UUID,
    ) -> float:
        """
        Return the most recent carbon-intensity measurement
        for a cloud provider.
        """

        result = await self.db.execute(
            select(CarbonData)
            .where(CarbonData.provider_id == provider_id)
            .order_by(CarbonData.measurement_time.desc())
            .limit(1)
        )

        carbon_data = result.scalar_one_or_none()

        if carbon_data is None:
            raise ValueError(
                f"No carbon data found for provider {provider_id}"
            )

        return carbon_data.carbon_intensity

    async def get_carbon_data(
        self,
        provider_id: UUID,
        measurement_time: datetime | None = None,
    ) -> CarbonData:
        """
        Return the carbon measurement closest to the requested time.

        If no time is provided, the latest available measurement
        is returned.
        """

        if measurement_time is None:
            result = await self.db.execute(
                select(CarbonData)
                .where(CarbonData.provider_id == provider_id)
                .order_by(CarbonData.measurement_time.desc())
                .limit(1)
            )
        else:
            result = await self.db.execute(
                select(CarbonData)
                .where(
                    CarbonData.provider_id == provider_id,
                    CarbonData.measurement_time <= measurement_time,
                )
                .order_by(CarbonData.measurement_time.desc())
                .limit(1)
            )

        carbon_data = result.scalar_one_or_none()

        if carbon_data is None:
            raise ValueError(
                f"No suitable carbon data found for provider {provider_id}"
            )

        return carbon_data

    @staticmethod
    def calculate_emissions(
        energy_kwh: float,
        carbon_intensity: float,
    ) -> float:
        """
        Calculate estimated CO2 emissions in kilograms.

        Formula:

            CO2 emissions = energy consumption × carbon intensity

        The calculation is deterministic and does not involve
        the LLM.
        """

        return energy_kwh * carbon_intensity