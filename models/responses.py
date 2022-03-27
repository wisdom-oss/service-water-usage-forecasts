"""Module containing the data models for responses"""
import typing

import pydantic

import enums
import models
import models.shared


class ForecastResponse(models.BaseModel):
    """A complete forecast response"""
    
    type: enums.ForecastType = pydantic.Field(
        default=...,
        alias='forecastType'
    )
    """
    Forecast Model
    
    The model which was used to create the forecast
    """
    
    equation: str = pydantic.Field(
        default=...,
        alias='forecastEquation'
    )
    """
    Forecast Equation
    
    The mathematical equation with which the forecast was calculated
    """
    
    score: float = pydantic.Field(
        default=...,
        alias='forecastScore'
    )
    """
    The R² Score of the forecast
    
    This score determines how reliable the modeled equation is for the already existing data. The
    higher the value the more reliable is the modeled equation
    """
    
    forecasted_usages: models.shared.WaterUsages = pydantic.Field(
        default=...,
        alias='forecastedUsages'
    )
    """
    The forecasted water usage amounts
    """
    
    reference_usages: models.shared.WaterUsages = pydantic.Field(
        default=...,
        alias='referenceUsages'
    )
    """
    The usage amounts on which the models is based
    """
