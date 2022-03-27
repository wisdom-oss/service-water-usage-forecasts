"""Module containing the data models for incoming forecast requests"""
import typing

import pydantic

import enums
import models
import models.shared


class ForecastRequest(models.BaseModel):
    """The data needed for a forecast"""
    
    type: enums.ForecastType = pydantic.Field(
        default=...,
        alias='forecastType'
    )
    """
    Forecast Type
    
    The type of forecast which shall be executed
    """
    
    predicted_years: typing.Optional[int] = pydantic.Field(
        default=15,
        alias='predictedYears'
    )
    """
    Predicted Years
    
    The amount of years which shall be predicted with the supplied model
    """
    
    usage_data: models.shared.WaterUsages = pydantic.Field(
        default=...,
        alias='usageData'
    )
    """
    Actual water usage data
    
    This object contains the current water usages and the range of years for the current water
    usages
    """
