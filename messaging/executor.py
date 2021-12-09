"""This module will be used to execute the incoming messages"""
import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from data_models.forecasts import ForecastRequest, ForecastType

__logger = logging.getLogger(__name__)


def execute(message: dict) -> dict:
    """AMQP Message Executor

    This executor is responsible for selecting the correct forecasting procedures depending on
    the data present in the message. The message is expected as a dictionary.

    :param message: Message from the message broker
    :type message: dict
    :return: Response which should be sent back to the message broker
    """
    # Parse the dictionary though a pydantic model to check the consistency
    try:
        request = ForecastRequest.parse_obj(message)
    except ValueError:
        return {
            "errors": "values_not_fitting"
        }
    if request.forecast_type == ForecastType.LINEAR_FORECAST:
        __logger.info('Running linear forecast of dataset')
        # Create a numpy array for the x-Axis
        x = np.arange(
            request.time_period_start, stop=request.time_period_end
        ).reshape((-1, 1))
        # Create an array for the y-Axis
        water_usage_amounts = np.array(request.water_usage_amounts)
        # Initialize the regression model
        model = LinearRegression()
        # Run the linear regression
        model.fit(x, water_usage_amounts)
        # Create a new array for years to predict outgoing from the end of the available data
        x_to_predict = np.arange(
            request.time_period_end, stop=request.time_period_end + 10
        ).reshape((-1, 1))
        return {
            "r_squared": model.score(x, water_usage_amounts),
            "equation": f"y = {model.coef_} * x + {model.intercept_}",
            "predicted_values": model.predict(x_to_predict).tolist()
        }



