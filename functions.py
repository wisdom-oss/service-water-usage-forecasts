import typing

import numpy
import numpy.polynomial
import pandas
import sklearn.metrics

import enums
import models


def run_forecast(**kwargs):
    _run_forecast(**kwargs)


def _run_forecast(
    result_list: list,
    consumer_group: int,
    model: enums.ForecastModel,
    usages: list,
    start_year: int,
    end_year: int,
    forecast_size: int,
    municipal: int,
):
    data_x_axis = numpy.linspace(start=start_year, stop=end_year, num=len(usages), dtype=int)
    forecast_x_axis = numpy.linspace(start=start_year, stop=end_year + forecast_size,
                                     num=len(usages) + forecast_size, dtype=int)
    data_y_axis = numpy.array(usages, dtype=int)
    if model is enums.ForecastModel.LINEAR:
        curve = numpy.polynomial.Polynomial.fit(data_x_axis, data_y_axis, deg=1)
        all_calculated_values = curve(forecast_x_axis).tolist()
        calculated_reference_values = all_calculated_values[:len(data_x_axis)]
        calculated_forecast_values = all_calculated_values[len(data_x_axis):]
        forecast_score = sklearn.metrics.r2_score(usages, calculated_reference_values)
        equation = str(curve)
        forecast_result = {
            "municipalID": municipal,
            "consumerGroupID": consumer_group,
            "forecastedUsages": calculated_forecast_values,
            "referenceUsages": usages,
            "forecastEquation": equation,
            "forecastScore": forecast_score,
            "forecastType": model.value,
            "forecastValuesStart": end_year + 1,
            "referenceValuesStart": start_year
        }
        result_list.append(forecast_result)
    elif model is enums.ForecastModel.POLYNOMIAL:
        curve = numpy.polynomial.Polynomial.fit(data_x_axis, data_y_axis, deg=2)
        all_calculated_values = curve(forecast_x_axis).tolist()
        calculated_reference_values = all_calculated_values[:(len(data_x_axis) - 1)]
        calculated_forecast_values = all_calculated_values[len(data_x_axis):]
        forecast_score = sklearn.metrics.r2_score(usages, calculated_reference_values)
        equation = str(curve)
        forecast_result = {
            "municipalID": municipal,
            "consumerGroupID": consumer_group,
            "forecastedUsages": calculated_forecast_values,
            "referenceUsages": usages,
            "forecastEquation": equation,
            "forecastScore": forecast_score,
            "forecastType": model.value,
            "forecastValuesStart": end_year + 1,
            "referenceValuesStart": start_year
        }
        result_list.append(forecast_result)

    elif model is enums.ForecastModel.LOGARITHMIC:
        curve = numpy.polynomial.Polynomial.fit(numpy.log(data_x_axis), data_y_axis, deg=1)
        all_calculated_values = curve(forecast_x_axis).tolist()
        calculated_reference_values = all_calculated_values[:(len(data_x_axis) - 1)]
        calculated_forecast_values = all_calculated_values[len(data_x_axis):]
        forecast_score = sklearn.metrics.r2_score(usages, calculated_reference_values)
        equation = str(curve)
        forecast_result = {
            "municipalID": municipal,
            "consumerGroupID": consumer_group,
            "forecastedUsages": calculated_forecast_values,
            "referenceUsages": usages,
            "forecastEquation": equation,
            "forecastScore": forecast_score,
            "forecastType": model.value,
            "forecastValuesStart": end_year + 1,
            "referenceValuesStart": start_year
        }
        result_list.append(forecast_result)
    else:
        raise ValueError("The supplied forecast model is not allowed")


def build_response(responses, request, municipals, consumer_groups, forecast_result):
    responses.append(
        models.ForecastResult(
            model=forecast_result.get('forecastType'),
            equation=forecast_result.get('forecastEquation'),
            score=forecast_result.get('forecastScore'),
            forecasted_usages=models.UsageData(
                start=forecast_result.get('forecastValuesStart'),
                end=forecast_result.get("forecastValuesStart") + request.forecast_size - 1,
                usages=forecast_result.get("forecastedUsages")
            ),
            reference_usages=models.UsageData(
                start=forecast_result.get('referenceValuesStart'),
                end=forecast_result.get("referenceValuesStart") + len(
                    forecast_result.get("referenceUsages")) - 1,
                usages=forecast_result.get("referenceUsages")
            ),
            municipal=municipals[forecast_result.get('municipalID')],
            consumer_group=consumer_groups[forecast_result.get('consumerGroupID')]
        ).dict(by_alias=True)
    )


def accumulate_data(forecast_results: list[models.ForecastResult]) -> typing.Tuple[dict, dict]:
    forecast_results = [models.ForecastResult.parse_obj(raw) for raw in forecast_results]
    consumer_group_accumulations = []
    municipal_accumulations = []
    df_reference_usage = pandas.DataFrame(columns=['municipal', 'year', 'usage'])
    # ========================== CITY ACCUMULATION =================================
    # %% Compile the data for the reference usages
    for result in forecast_results:
        municipal_list = []
        years = map(str, numpy.arange(start=result.reference_usages.start,
                                      stop=result.reference_usages.end + 1).tolist()
                    )
        for value in result.reference_usages.usages:
            municipal_list.append(result.municipal)
        data = zip(municipal_list, years, result.reference_usages.usages)
        _df = pandas.DataFrame.from_records(data, columns=['municipal', 'year', 'usage'])
        df_reference_usage = pandas.concat([df_reference_usage, _df], ignore_index=True)
    municipal_groups = df_reference_usage.groupby(["municipal", "year"])
    reference_city_aggregation = municipal_groups.aggregate(numpy.sum)
    # %% Compile the data for the forecasted values


def accumulate_by_municipals(forecast_results: list[dict]) -> typing.Dict:
    # %% Convert the dictionaries into pydantic objects
    forecast_results = [models.ForecastResult.parse_obj(o) for o in forecast_results]
    # %% Create an empty dataframe which will contain the data
    df_reference_usages = pandas.DataFrame(columns=['municipal', 'year', 'usage'])
    df_forecasted_usages = pandas.DataFrame(columns=['municipal', 'year', 'usage'])
    # %% Create and append data to the reference usage data frame
    for r in forecast_results:
        # Create the row values for the reference data
        ref_municipal = [r.municipal for v in r.reference_usages.usages]
        ref_years = [str(y) for y in range(r.reference_usages.start, r.reference_usages.end+1)]
        ref_rows = zip(ref_municipal, ref_years, r.reference_usages.usages)
        # Concatenate the reference data values
        _df = pandas.DataFrame(ref_rows, columns=['municipal', 'year', 'usage'])
        df_reference_usages = pandas.concat([df_reference_usages, _df], ignore_index=True)
        # Create the row values for the forecast data
        forecast_municipal = [r.municipal for _ in r.forecasted_usages.usages]
        forecast_years = [str(y) for y in range(r.forecasted_usages.start, r.forecasted_usages.end + 1)]
        forecast_rows = zip(forecast_municipal, forecast_years, r.forecasted_usages.usages)
        # Concatenate the forecasted data values
        _df = pandas.DataFrame(forecast_rows, columns=['municipal', 'year', 'usage'])
        df_forecasted_usages = pandas.concat([df_forecasted_usages, _df], ignore_index=True)
    # %% Group the data and sum up the reference data
    reference_aggregation = df_reference_usages.groupby(["municipal", "year"]).aggregate(numpy.sum)
    forecast_aggregation = df_forecasted_usages.groupby(["municipal", "year"]).aggregate(numpy.sum)
    raw_reference_aggregation = reference_aggregation.to_dict(orient='dict')["usage"]
    raw_forecast_aggregation: dict = forecast_aggregation.to_dict(orient='dict')["usage"]
    # %% Transform the reference aggregation data
    reference_aggregation_dict = {}
    years = {}
    usages = {}
    for key, usage in raw_reference_aggregation.items():
        municipal, year = key
        if years.get(municipal, None) is None:
            years.update({municipal: []})
        if usages.get(municipal, None) is None:
            usages.update({municipal: []})
        years.get(municipal, None).append(year)
        usages.get(municipal, None).append(usage)
    for municipal in years:
        return_values = {
            "startYear": years.get(municipal)[0],
            "endYear": years.get(municipal)[-1],
            "usages": usages.get(municipal)
        }
        reference_aggregation_dict.update({municipal: return_values})
    # %% Transform the forecast aggregation data
    forecast_aggregation_dict = {}
    years = {}
    usages = {}
    for key, usage in raw_forecast_aggregation.items():
        municipal, year = key
        if years.get(municipal, None) is None:
            years.update({municipal: []})
        if usages.get(municipal, None) is None:
            usages.update({municipal: []})
        years.get(municipal, None).append(year)
        usages.get(municipal, None).append(usage)
    for municipal in years:
        return_values = {
            "startYear": years.get(municipal)[0],
            "endYear": years.get(municipal)[-1],
            "usages": usages.get(municipal)
        }
        forecast_aggregation_dict.update({municipal: return_values})
    return {
        "reference": reference_aggregation_dict,
        "forecast": forecast_aggregation_dict
    }


def accumulate_by_consumer_groups(forecast_results: list[dict]) -> typing.Dict:
    # %% Convert the dictionaries into pydantic objects
    forecast_results = [models.ForecastResult.parse_obj(o) for o in forecast_results]
    # %% Create an empty dataframe which will contain the data
    df_reference_usages = pandas.DataFrame(columns=['consumerGroup', 'year', 'usage'])
    df_forecasted_usages = pandas.DataFrame(columns=['consumerGroup', 'year', 'usage'])
    # %% Create and append data to the reference usage data frame
    for r in forecast_results:
        # Create the row values for the reference data
        ref_cg = [r.consumer_group for v in r.reference_usages.usages]
        ref_years = [str(y) for y in range(r.reference_usages.start, r.reference_usages.end+1)]
        ref_rows = zip(ref_cg, ref_years, r.reference_usages.usages)
        # Concatenate the reference data values
        _df = pandas.DataFrame(ref_rows, columns=['consumerGroup', 'year', 'usage'])
        df_reference_usages = pandas.concat([df_reference_usages, _df], ignore_index=True)
        # Create the row values for the forecast data
        forecast_cg = [r.consumer_group for _ in r.forecasted_usages.usages]
        forecast_years = [str(y) for y in range(r.forecasted_usages.start, r.forecasted_usages.end + 1)]
        forecast_rows = zip(forecast_cg, forecast_years, r.forecasted_usages.usages)
        # Concatenate the forecasted data values
        _df = pandas.DataFrame(forecast_rows, columns=['consumerGroup', 'year', 'usage'])
        df_forecasted_usages = pandas.concat([df_forecasted_usages, _df], ignore_index=True)
    # %% Group the data and sum up the reference data
    reference_aggregation = df_reference_usages.groupby(["consumerGroup", "year"]).aggregate(numpy.sum)
    forecast_aggregation = df_forecasted_usages.groupby(["consumerGroup", "year"]).aggregate(numpy.sum)
    raw_reference_aggregation = reference_aggregation.to_dict(orient='dict')["usage"]
    raw_forecast_aggregation: dict = forecast_aggregation.to_dict(orient='dict')["usage"]
    # %% Transform the reference aggregation data
    reference_aggregation_dict = {}
    years = {}
    usages = {}
    for key, usage in raw_reference_aggregation.items():
        cg, year = key
        if years.get(cg, None) is None:
            years.update({cg: []})
        if usages.get(cg, None) is None:
            usages.update({cg: []})
        years.get(cg, None).append(year)
        usages.get(cg, None).append(usage)
    for cg in years:
        return_values = {
            "startYear": years.get(cg)[0],
            "endYear": years.get(cg)[-1],
            "usages": usages.get(cg)
        }
        reference_aggregation_dict.update({cg: return_values})
    # %% Transform the forecast aggregation data
    forecast_aggregation_dict = {}
    years = {}
    usages = {}
    for key, usage in raw_forecast_aggregation.items():
        cg, year = key
        if years.get(cg, None) is None:
            years.update({cg: []})
        if usages.get(cg, None) is None:
            usages.update({cg: []})
        years.get(cg, None).append(year)
        usages.get(cg, None).append(usage)
    for cg in years:
        return_values = {
            "startYear": years.get(cg)[0],
            "endYear": years.get(cg)[-1],
            "usages": usages.get(cg)
        }
        forecast_aggregation_dict.update({cg: return_values})
    return {
        "reference": reference_aggregation_dict,
        "forecast": forecast_aggregation_dict
    }
