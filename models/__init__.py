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

    model: enums.ForecastModel = pydantic.Field(default=..., alias="model")
    """The forecast model which shall be used to forecast the usage values"""

    keys: list[str] = pydantic.Field(default=..., alias="keys")
    """The municipal and district keys for which objects the forecast shall be executed"""

    consumer_groups: typing.Optional[list[str]] = pydantic.Field(
        default=None, alias="consumerGroups"
    )
    """The consumer groups for which the forecast shall be calculated"""

    forecast_size: int = pydantic.Field(default=20, alias="forecastSize", gt=0)
    """The amount of years for which the forecast shall be calculated"""

    @pydantic.validator("keys")
    def check_keys(cls, v):
        """
        Check if the keys are of a valid length and are present in the database

        :param v: The values which are already present in the database
        :return: The object containing the keys
        """
        if v is None:
            raise ValueError("At least one key needs to be present in the list of keys")
        # Now check if the keys are present in the database
        shape_query = sql.select(
            [database.tables.shapes.c.key],
            database.tables.shapes.c.key.in_(v),
        )
        db_shapes = database.engine.execute(shape_query).all()
        unrecognized_keys = [k for k in v if (k,) not in db_shapes]
        if len(unrecognized_keys) > 0:
            raise ValueError(
                f"The following keys have not been recognized by the module: {unrecognized_keys}"
            )
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


class Usages(BaseModel):
    start: int = pydantic.Field(default=..., alias="start")
    """The year from which on the data is contained in the ``usages`` property"""

    end: int = pydantic.Field(default=..., alias="end")
    """The year in which the data in the ``usages`` property ends"""

    amounts: list[float] = pydantic.Field(default=..., alias="amounts")
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
        usage_data = values.get("amounts")
        expected_list_length = (data_end - data_start) + 1
        if len(usage_data) == expected_list_length:
            return values
        raise ValueError(
            f"The usage value list contains {len(usage_data)} items, whereas {expected_list_length}"
            f" items were expected in the list"
        )


class Municipal(BaseModel):

    key: str = pydantic.Field(default=..., alias="key")
    """The official municipal key of a municipal"""

    name: str = pydantic.Field(default=..., alias="name")
    """The name of the municipal"""

    nuts_key: str = pydantic.Field(default=..., alias="nutsKey")


class ConsumerGroup(BaseModel):

    key: str = pydantic.Field(default=..., alias="key")
    """The official municipal key of a municipal"""

    name: str = pydantic.Field(default=..., alias="name")
    """The name of the municipal"""


class Forecast(BaseModel):

    model: enums.ForecastModel = pydantic.Field(default=..., alias="model")
    """The model used to fit a curve to the reference values"""

    equation: str = pydantic.Field(default=..., alias="equation")
    """The equation fitted to the reference values used to the forecasted values"""

    score: float = pydantic.Field(default=..., alias="float")
    """The R² score of the forecast"""

    usages: Usages = pydantic.Field(default=..., alias="usages")


class ForecastResult(BaseModel):

    forecast: Forecast = pydantic.Field(default=..., alias="forecast")
    """The usage values that have been forecasted"""

    reference_usages: Usages = pydantic.Field(default=..., alias="referenceUsages")
    """The usage values on which the model has been built"""

    municipal: Municipal = pydantic.Field(default=..., alias="municipal")

    consumer_group: ConsumerGroup = pydantic.Field(default=..., alias="consumerGroup")
    """The parameter of the consumer group"""


class ErrorResponse(BaseModel):

    error_code: str = pydantic.Field(default=..., alias="error")

    error_name: str = pydantic.Field(default=None, alias="errorName")

    error_description: str = pydantic.Field(default=None, alias="errorDescription")
