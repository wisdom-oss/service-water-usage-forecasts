"""Module containing all data models used for forecasts"""
from typing import List

from pydantic import BaseModel, Field, root_validator

from data_models.forecasts.enums import ForecastType


class RealData(BaseModel):
    """
    Data model for the incoming real water usage data.
    """
    time_period_start: int = Field(
        default=...,
        alias='timePeriodStart'
    )
    time_period_end: int = Field(
        default=...,
        alias='timePeriodEnd'
    )
    water_usage_amounts: List[int] = Field(
        default=...,
        alias='waterUsageAmounts'
    )

    @root_validator
    def check_data_consistency(cls, values):
        time_period_start, time_period_end, water_usage_amounts, _ = values.values()
        if time_period_start >= time_period_end:
            raise ValueError('The start of the time period may not be after the end of the time '
                             'period')
        expected_values_in_list = time_period_end - time_period_start
        value_discrepancy = expected_values_in_list - len(water_usage_amounts)
        if value_discrepancy > 0:
            raise ValueError(f'The Water usage amounts list is missing {value_discrepancy} entries')
        if value_discrepancy < 0:
            raise ValueError(f'The Water usage amounts list has {abs(value_discrepancy)} entries '
                             f'too much')
        return values


class ForecastRequest(RealData):
    forecast_type: ForecastType = Field(
        default=...,
        alias='forecastType'
    )

