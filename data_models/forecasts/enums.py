"""Enumerations for the forecasts"""
from enum import Enum, IntFlag, auto


class ForecastType(str, Enum):
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"


class ConsumerGroup(str, Enum):
    BUSINESSES = "businesses"
    HOUSEHOLDS_AND_SMALL_BUSINESSES = "households_and_small_businesses"
    FARMING_FORESTRY_FISHING_INDUSTRY = "farming_forestry_fishing_industry"
    PUBLIC_INSTITUTIONS = "public_institutions"
    ALL = "all"
