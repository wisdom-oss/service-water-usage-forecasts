"""Enumerations for the forecasts"""
from enum import Enum


class ForecastType(str, Enum):
    LINEAR_FORECAST = "linear"


class ConsumerGroup(str, Enum):
    BUSINESSES = "businesses"
    HOUSEHOLDS_AND_SMALL_BUSINESSES = "households_small_businesses"
    FARMING_FORESTRY_FISHING_INDUSTRY = "farming_forestry_fishing"
    PUBLIC_INSTITUTIONS = "public_institution"
