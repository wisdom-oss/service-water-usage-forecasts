import typing

import pydantic
import sqlalchemy.sql as sql
import sqlalchemy.sql.functions as func

import enums
import database
import database.tables


class BaseModel(pydantic.BaseModel):
    """A preconfigured BaseModel"""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        smart_union = True


class ForecastQuery(BaseModel):
    """A model describing, how the incoming request shall look like"""

    granularity: enums.ForecastGranularity = pydantic.Field(default=..., alias="granularity")
    """The level of granularity from which the object names are originating"""

    model: enums.ForecastModel = pydantic.Field(default=..., alias="model")
    """The forecast model which shall be used to forecast the usage values"""

    objects: list[str] | list[int] = pydantic.Field(default=..., alias="objects")
    """The names of the geo objects for which the query shall be executed"""

    consumer_groups: typing.Optional[list[str]] = pydantic.Field(
        default=None, alias="consumerGroups"
    )
    """The consumer groups for which the forecast shall be calculated"""

    forecast_size: int = pydantic.Field(default=20, alias="forecastSize", gt=0)
    """The amount of years for which the forecast shall be calculated"""

    @pydantic.validator("objects")
    def check_object_existence(cls, v, values):
        granularity = values.get("granularity")
        if granularity == enums.ForecastGranularity.DISTRICT:
            district_query = sql.select(
                [database.tables.districts.c.name], database.tables.districts.c.name.in_(v)
            )
            results = database.engine.execute(district_query).all()
            found_objects = [row[0] for row in results]
            for obj in v:
                if obj not in found_objects:
                    raise ValueError(f"The district {obj} was not found in the database")
        elif granularity == enums.ForecastGranularity.MUNICIPAL:
            municipal_query = sql.select(
                [database.tables.municipals.c.name], database.tables.municipals.c.name.in_(v)
            )
            results = database.engine.execute(municipal_query).all()
            found_objects = [row[0] for row in results]
            for obj in v:
                if obj not in found_objects:
                    raise ValueError(f"The municipal {obj} was not found in the database")
        return v

    @pydantic.validator("consumer_groups", always=True)
    def check_consumer_groups(cls, v):
        if v is None:
            consumer_group_pull_query = sql.select([database.tables.consumer_groups.c.parameter])
            results = database.engine.execute(consumer_group_pull_query).all()
            return [row[0] for row in results]
        else:
            consumer_group_query = sql.select(
                [database.tables.consumer_groups.c.parameter],
                database.tables.consumer_groups.c.parameter.in_(v),
            )
            results = database.engine.execute(consumer_group_query).all()
            found_objects = [row[0] for row in results]
            for obj in v:
                if obj not in found_objects:
                    raise ValueError(f"The consumer group {obj} was not found in the database")
            return v


class UsageData(BaseModel):
    start: int = pydantic.Field(default=..., alias="startYear")
    """The year from which on the data is contained in the ``usages`` property"""

    end: int = pydantic.Field(default=..., alias="endYear")
    """The year in which the data in the ``usages`` property ends"""

    usages: list[float] = pydantic.Field(default=..., alias="usageAmounts")
    """The usage amounts from each year, ordered in a ascending manner"""

    @pydantic.root_validator
    def check_years(cls, values):
        """
        Check if the start and end year is switched around
        """
        start = values.get("start")
        end = values.get("end")
        if start <= end:
            return values
        else:
            raise ValueError("The start year may not be larger than the end year")

    @pydantic.root_validator
    def check_usage_list_length(cls, values):
        """
        Check if the length of the usages matches the
        """
        data_start = values.get("start")
        data_end = values.get("end")
        usage_data = values.get("usages")
        expected_list_length = (data_end - data_start) + 1
        if len(usage_data) == expected_list_length:
            return values
        raise ValueError(
            f"The usage value list contains {len(usage_data)} items, whereas {expected_list_length}"
            f" items were expected in the list"
        )


class ForecastResult(BaseModel):

    model: enums.ForecastModel = pydantic.Field(default=..., alias="forecastType")
    """The model used to create the forecasted values"""

    equation: str = pydantic.Field(default=..., alias="forecastEquation")
    """The equation which has been used to calculate the forecasted values"""

    score: str = pydantic.Field(default=..., alias="forecastScore")
    """The R² score of the forecast"""

    forecasted_usages: UsageData = pydantic.Field(default=..., alias="forecastedUsages")
    """The usage values that have been forecasted"""

    reference_usages: UsageData = pydantic.Field(default=..., alias="referenceUsages")
    """The usage values on which the model has been built"""

    municipal: str = pydantic.Field(default=..., alias='name')
    """The name of the municipal for which the forecast is valid"""

    consumer_group: str = pydantic.Field(default=..., alias='consumerGroup')


class ErrorResponse(BaseModel):

    error_code: str = pydantic.Field(default=..., alias="error")

    error_name: str = pydantic.Field(default=None, alias="errorName")

    error_description: str = pydantic.Field(default=None, alias="errorDescription")
