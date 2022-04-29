"""Module containing functions for the AMQP server"""
import concurrent.futures
import logging
import time

import pandas
import pydantic.error_wrappers
import sqlalchemy
import ujson
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
    single_forecast_responses = []
    municipals = tools.get_municipal_names_from_query(municipal_ids)
    consumer_groups = tools.get_consumer_group_names_from_query(consumer_group_ids)
    with concurrent.futures.ThreadPoolExecutor() as tpe:
        forecast_parameters = []
        for municipal, data in municipal_usage_data.items():
            for consumer_group, data in dict(tuple(data.groupby("consumer_group"))).items():
                usages = []
                years = []
                data: pandas.DataFrame
                data = data.sort_values(["year"])
                for v in data["sum_1"]:
                    usages.append(v)
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
        calc_threads = tpe.map(lambda args: functions.run_forecast(**args), forecast_parameters)
        while len(forecast_results) < len(forecast_parameters):
            time.sleep(0.05)
        response_builder_threads = tpe.map(lambda forecast_result: functions.build_response(
            single_forecast_responses, request, municipals, consumer_groups, forecast_result),
                                           forecast_results
                                           )
        while len(single_forecast_responses) < len(forecast_parameters):
            time.sleep(0.05)
    # %% Accumulate the forecasted data into municipals and consumer groups
    functions.accumulate_by_municipals(single_forecast_responses)
    response = {
        "partials": single_forecast_responses,
        "accumulations": {
            "city": functions.accumulate_by_municipals(single_forecast_responses),
            "consumerGroup": functions.accumulate_by_consumer_groups(single_forecast_responses)
        }
    }
    print(ujson.dumps(response, ensure_ascii=False, indent=2))
    return ujson.dumps(response, ensure_ascii=False).encode('utf-8')
