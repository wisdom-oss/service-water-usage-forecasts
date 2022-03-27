"""Module containing functions for the AMQP server"""
import json
import logging
import typing

import numpy.polynomial
import pydantic.error_wrappers
import numpy as np
import sklearn.linear_model

import enums
import models.requests
import models.responses
import models.shared

_validator_logger = logging.getLogger('content_validator')
_executor_logger = logging.getLogger('executor')


def content_validator(message: bytes) -> bool:
    """Check if the content is parseable by the pydantic data model"""
    try:
        models.requests.ForecastRequest.parse_raw(message)
        return True
    except pydantic.error_wrappers.ValidationError as e:
        _validator_logger.critical('Unable to parse message. Rejecting the message', exc_info=e)
        return False


def executor(message: bytes) -> bytes:
    """Parse the message and run the appropriate actions"""
    request = models.requests.ForecastRequest.parse_raw(message)
    # Create a range of values for the x-Axis
    x_axis = np.arange(
        start=request.usage_data.start,
        stop=request.usage_data.end + 1
    )
    # Create a range of x-Axis values for the prediction
    prediction_x_axis = np.arange(
        start=request.usage_data.start,
        stop=request.usage_data.end + 1 + request.predicted_years
    )
    # Create the y-Axis values from the usage amounts
    y_axis = np.array(request.usage_data.usages)
    # Create an empty forecast_result
    forecast_result: typing.Optional[dict] = None
    # Now switch between the different regression models
    if request.type == enums.ForecastType.LINEAR:
        _executor_logger.debug('Running a linear forecast of the dataset')
        # Fit the given values to a polynom in the first degree
        curve = numpy.polynomial.Polynomial.fit(x_axis, y_axis, 1)
        # Now forecast all values
        values = curve(prediction_x_axis).tolist()
        # Now get the forecasted values by slicing just after the y-axis ends
        forecasted_values = values[len(y_axis):]
        # Now get the reference values for the r² calculation
        predicted_current_values = values[:len(x_axis)]
        # Now calculate the r² value
        forecast_r2 = sklearn.metrics.r2_score(y_axis, predicted_current_values)
        # Now build the equation for the forecast model
        equation = "y = {} * x + {}".format(
            curve.coef[0], curve.coef[1]
        )
        # Now pre-build the response object
        forecasted_usages = models.shared.WaterUsages(
            start=request.usage_data.end + 1,
            end=request.usage_data.end + request.predicted_years,
            usages=forecasted_values
        )
        forecast_result = {
            'usage_data': forecasted_usages,
            'equation':   equation,
            'score':      forecast_r2
        }
    elif request.type == enums.ForecastType.POLYNOMIAL:
        _executor_logger.debug('Running a linear forecast of the dataset')
        # Fit the given values to a polynom in the first degree
        curve = numpy.polynomial.Polynomial.fit(x_axis, y_axis, 2)
        # Now forecast all values
        values = curve(prediction_x_axis).tolist()
        # Now get the forecasted values by slicing just after the y-axis ends
        forecasted_values = values[len(y_axis):]
        # Now get the reference values for the r² calculation
        predicted_current_values = values[:len(x_axis)]
        # Now calculate the r² value
        forecast_r2 = sklearn.metrics.r2_score(y_axis, predicted_current_values)
        # Now build the equation for the forecast model
        equation = "y = {} * x^2 + {} * x + {}".format(
            curve.coef[0], curve.coef[1], curve.coef[2]

        )
        # Now pre-build the response object
        forecasted_usages = models.shared.WaterUsages(
            start=request.usage_data.end + 1,
            end=request.usage_data.end + 1 + request.predicted_years,
            usages=forecasted_values
        )
        forecast_result = {
            'usage_data': forecasted_usages,
            'equation':   equation,
            'score':      forecast_r2
        }
    elif request.type == enums.ForecastType.LOGARITHMIC:
        _executor_logger.debug('Running a linear forecast of the dataset')
        # Fit the given values to a polynom in the first degree
        curve = numpy.polynomial.Polynomial.fit(numpy.log(x_axis), y_axis, 1)
        # Now forecast all values
        values = curve(prediction_x_axis).tolist()
        # Now get the forecasted values by slicing just after the y-axis ends
        forecasted_values = values[len(y_axis):]
        # Now get the reference values for the r² calculation
        predicted_current_values = values[:len(x_axis)]
        # Now calculate the r² value
        forecast_r2 = sklearn.metrics.r2_score(y_axis, predicted_current_values)
        # Now build the equation for the forecast model
        equation = "y = {} * log(x) + {}".format(
            curve.coef[0], curve.coef[1]
        )
        forecasted_usages = models.shared.WaterUsages(
            start=request.usage_data.end + 1,
            end=request.usage_data.end + 1 + request.predicted_years,
            usages=forecasted_values
        )
        # Now build the response object
        forecast_result = {
            'usage_data':  forecasted_usages,
            'equation':    equation,
            'score':       forecast_r2
        }
    if forecast_result is not None:
        return models.responses.ForecastResponse(
            type=request.type,
            equation=forecast_result['equation'],
            score=forecast_result['score'],
            forecasted_usages=forecast_result['usage_data'],
            reference_usages=request.usage_data
        ).json(by_alias=True).encode('utf-8')
    else:
        return json.dumps(
            {
                "error": "forecast_model_not_available"
            }
        ).encode('utf-8')
