"""Module containing functions for the AMQP server"""
import json
import logging
import time
import concurrent.futures

import pandas
import pydantic.error_wrappers
import sqlalchemy
from sqlalchemy.sql import *
from sqlalchemy.sql.functions import sum as sum_
import database
import database.tables
import enums
import functions
import models
import tools

_validator_logger = logging.getLogger("content_validator")
_executor_logger = logging.getLogger("executor")


def content_validator(message: bytes) -> bool:
    """Check if the content is parseable by the pydantic data model"""
    try:
        models.ForecastQuery.parse_raw(message)
        return True
    except pydantic.error_wrappers.ValidationError as e:
        _validator_logger.critical("Unable to parse message. Rejecting the message", exc_info=e)
        return False


def executor(message: bytes) -> bytes:
    """Parse the message and run the appropriate actions"""
    request: models.ForecastQuery = models.ForecastQuery.parse_raw(message)
    # %% Get the municipals which are within the districts
    municipal_ids = {}
    if request.granularity == enums.ForecastGranularity.DISTRICT:
        municipals = []
        for obj in request.objects:
            municipal_query = select(
                [database.tables.municipals.c.id, database.tables.municipals.c.name],
                func.ST_Within(
                    database.tables.municipals.c.geom,
                    select(database.tables.districts.c.geom).where(
                        database.tables.districts.c.name == obj
                    ),
                ),
            )
            results = database.engine.execute(municipal_query)
            for municipal_tuple in results:
                municipals.append(municipal_tuple[1])
        request.objects = municipals
    # %% Convert the municipals into ids
    municipal_id_query = select(
        [database.tables.municipals.c.id], database.tables.municipals.c.name.in_(request.objects)
    )
    results = database.engine.execute(municipal_id_query).all()
    municipal_ids = [row[0] for row in results]
    # %% Convert the Consumer Groups into ids
    consumer_group_id_query = select(
        [database.tables.consumer_groups.c.id],
        database.tables.consumer_groups.c.parameter.in_(request.consumer_groups),
    )
    cg_results = database.engine.execute(consumer_group_id_query).all()
    consumer_group_ids = [row[0] for row in cg_results]
    # %% Get the water usage data for every municipal and consumer group
    data_query = select(
        [
            database.tables.usages.c.municipal,
            database.tables.usages.c.consumer_group,
            database.tables.usages.c.year,
            sum_(database.tables.usages.c.value),
        ],
        sqlalchemy.and_(
            database.tables.usages.c.municipal.in_(municipal_ids),
            database.tables.usages.c.consumer_group.in_(consumer_group_ids),
        ),
    ).group_by(
        database.tables.usages.c.municipal,
        database.tables.usages.c.consumer_group,
        database.tables.usages.c.year,
    )
    data_query_results = database.engine.execute(data_query).all()
    usage_data = pandas.DataFrame(data_query_results)
    municipal_usage_data = dict(tuple(usage_data.groupby("municipal")))
    forecast_results = []
    with concurrent.futures.ThreadPoolExecutor(thread_name_prefix="CALC") as tpe:
        forecast_parameters = []
        for municipal, data in municipal_usage_data.items():
            for consumer_group, data in dict(tuple(data.groupby("consumer_group"))).items():
                usages = []
                years = []
                data: pandas.DataFrame
                data = data.sort_values(["year"])
                for v in data["sum_1"]:
                    usages.append(float(v))
                for v in data["year"]:
                    years.append(int(v))
                years = sorted(years)
                forecast_parameters.append(
                    {
                        "result_list": forecast_results,
                        "consumer_group": consumer_group,
                        "model": request.model,
                        "usages": usages,
                        "start_year": years[0],
                        "end_year": years[-1],
                        "forecast_size": request.forecast_size,
                        "municipal": municipal,
                    }
                )
        tpe.map(lambda args: functions.run_forecast(**args), forecast_parameters)
    responses = []
    municipals = tools.get_municipal_names_from_query(municipal_ids)
    consumer_groups = tools.get_consumer_group_names_from_query(consumer_group_ids)
    for result in forecast_results:
        responses.append(
            models.ForecastResult(
                model=result.get('forecastType'),
                equation=result.get('forecastEquation'),
                score=result.get('forecastScore'),
                forecasted_usages=models.UsageData(
                    start=result.get('forecastValuesStart'),
                    end=result.get("forecastValuesStart") + request.forecast_size - 1,
                    usages=result.get("forecastedUsages")
                ),
                reference_usages=models.UsageData(
                    start=result.get('referenceValuesStart'),
                    end=result.get("referenceValuesStart") + len(result.get("referenceUsages")) - 1,
                    usages=result.get("referenceUsages")
                ),
                municipal=municipals[result.get('municipalID')],
                consumer_group=consumer_groups[result.get('consumerGroupID')]
            ).dict(by_alias=True)
        )
    return json.dumps(responses).encode('utf-8')
