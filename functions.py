import numpy
import numpy.polynomial
import logging

import sklearn.metrics

import enums
import models


def run_forecast(**kwargs):
    _run_forecast(**kwargs)


def _run_forecast(
    result_list: list,
    consumer_group: int,
    model: enums.ForecastModel,
    usages: list[float],
    start_year: int,
    end_year: int,
    forecast_size: int,
    municipal: int,
):
    data_x_axis = numpy.arange(start=start_year, stop=end_year + 1)
    forecast_x_axis = numpy.arange(start=start_year, stop=end_year + forecast_size + 1)
    data_y_axis = numpy.array(usages)
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
                end=forecast_result.get("referenceValuesStart") + len(forecast_result.get("referenceUsages")) - 1,
                usages=forecast_result.get("referenceUsages")
            ),
            municipal=municipals[forecast_result.get('municipalID')],
            consumer_group=consumer_groups[forecast_result.get('consumerGroupID')]
        ).dict(by_alias=True)
    )
