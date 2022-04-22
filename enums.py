"""Enumerations for the forecasts"""
import enum
import settings


class ForecastModel(str, enum.Enum):
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    LOGARITHMIC = "logarithmic"


class ForecastGranularity(str, enum.Enum):
    MUNICIPAL = "municipalities"
    DISTRICT = "districts"


class ErrorReasons(tuple, enum.Enum):
    __service__ = settings.ServiceSettings()

    INSUFFICIENT_DATA = (__service__.name + ".INSUFFICIENT_DATA", "Insufficient Data for forecast")
    DATABASE_CONNECTION_ERROR = (
        __service__.name + ".DB_CONNECTION_ERROR",
        "Database Connection Error",
    )
    DATABASE_QUERY_ERROR = (__service__.name + ".DB_QUERY_ERROR", "Database Query Error")
    OBJECT_NOT_FOUND_ERROR = (
        __service__.name + ".QUERY_RETURNED_NULL",
        "Database Returned Null Unexpectedly",
    )
