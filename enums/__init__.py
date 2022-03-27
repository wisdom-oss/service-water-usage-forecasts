"""Enumerations for the forecasts"""
import enum


class ForecastType(str, enum.Enum):
    LOGARITHMIC = "logarithmic"
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
