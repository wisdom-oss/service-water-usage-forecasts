"""Module containing all data models used for forecasts"""
from typing import List, Union

from pydantic import BaseModel, Field, root_validator

from data_models.forecasts.enums import ConsumerGroup, ForecastType


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
    water_usage_amounts: List[float] = Field(
        default=...,
        alias='waterUsageAmounts'
    )

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

    @root_validator
    def check_data_consistency(cls, values):
        time_period_start = values.get("time_period_start")
        time_period_end = values.get("time_period_end")
        water_usage_amounts = values.get("water_usage_amounts")
        if time_period_start >= time_period_end:
            raise ValueError(
                'The start of the time period may not be after the end of the time '
                'period'
            )
        expected_values_in_list = time_period_end - (time_period_start + 1)
        value_discrepancy = expected_values_in_list - len(water_usage_amounts)
        if value_discrepancy > 0:
            raise ValueError(f'The Water usage amounts list is missing {value_discrepancy} entries')
        if value_discrepancy < 0:
            raise ValueError(
                f'The Water usage amounts list has {abs(value_discrepancy)} entries '
                f'too much'
            )
        return values


class ForecastRequest(RealData):
    forecast_type: ForecastType = Field(
        default=...,
        alias='forecastType'
    )
    consumer_group: ConsumerGroup = Field(
        default=...,
        alias='consumerGroup'
    )

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ForecastData(BaseModel):
    forecast_starts: int = Field(
        default=...,
        alias='start'
    )
    forecast_period: int = Field(
        default=...,
        alias='timePeriod'
    )
    forecast_equation: str = Field(
        default=...,
        alias='equation'
    )
    forecast_score: float = Field(
        default=...,
        alias='score'
    )
    forecast_values: List[float] = Field(
        default=...,
        alias='usageAmounts'
    )

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ForecastResponse(BaseModel):
    forecast_type: ForecastType = Field(
        default=...,
        alias='forecastType'
    )
    consumer_group: ConsumerGroup = Field(
        default=...,
        alias='consumerGroup'
    )
    base_data: RealData = Field(
        default=...,
        alias='reference'
    )
    prediction_data: ForecastData = Field(
        default=...,
        alias='forecast'
    )

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True
