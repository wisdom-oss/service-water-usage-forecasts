# WISdoM - Water Usage Forecasts (Calculation Module)
Maintainer: [Jan Eike Suchard](mailto:jan.eike.suchard@uni-oldenburg.de)
<hr/>

## Deployment
To deploy this project, please use the information present in the deployment repository

## General

This module implements the following forecasting methods:
- Linear
- Exponential
- Polynomial

To create a request the following JSON Schema needs to be used
```json
{
    "title": "Forecast Request",
    "definitions": {
        "ForecastType": {
            "title": "ForecastType",
            "description": "An enumeration.",
            "enum": [
                "logarithmic",
                "linear",
                "polynomial"
            ],
            "type": "string"
        },
        "ConsumerGroup": {
            "title": "ConsumerGroup",
            "description": "An enumeration.",
            "enum": [
                "businesses",
                "households_and_small_businesses",
                "farming_forestry_fishing_industry",
                "public_institutions",
                "all"
            ],
            "type": "string"
        },
        "ForecastRequest": {
            "title": "ForecastRequest",
            "description": "Data model for the incoming real water usage data.",
            "type": "object",
            "properties": {
                "timePeriodStart": {
                    "title": "Forecast Time Period Start",
                    "type": "integer"
                },
                "timePeriodEnd": {
                    "title": "Forecast Time Period End",
                    "type": "integer"
                },
                "waterUsageAmounts": {
                    "title": "Water usage amounts",
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "forecastType": {
                    "$ref": "#/definitions/ForecastType"
                },
                "consumerGroup": {
                    "$ref": "#/definitions/ConsumerGroup"
                }
            },
            "required": [
                "timePeriodStart",
                "timePeriodEnd",
                "waterUsageAmounts",
                "forecastType",
                "consumerGroup"
            ]
        }
    }
}
```
> This scheme may also be found [here](schemas/new-request.json)

A response sent by this service should have the following schema
```json
{
    "title": "Forecast Response",
    "definitions": {
        "ForecastType": {
            "title": "ForecastType",
            "description": "An enumeration.",
            "enum": [
                "logarithmic",
                "linear",
                "polynomial"
            ],
            "type": "string"
        },
        "ConsumerGroup": {
            "title": "ConsumerGroup",
            "description": "An enumeration.",
            "enum": [
                "businesses",
                "households_and_small_businesses",
                "farming_forestry_fishing_industry",
                "public_institutions",
                "all"
            ],
            "type": "string"
        },
        "RealData": {
            "title": "RealData",
            "description": "Data model for the incoming real water usage data.",
            "type": "object",
            "properties": {
                "timePeriodStart": {
                    "title": "Time period start",
                    "type": "integer"
                },
                "timePeriodEnd": {
                    "title": "Time period end",
                    "type": "integer"
                },
                "waterUsageAmounts": {
                    "title": "Water usage amounts",
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            },
            "required": [
                "timePeriodStart",
                "timePeriodEnd",
                "waterUsageAmounts"
            ]
        },
        "ForecastData": {
            "title": "ForecastData",
            "type": "object",
            "properties": {
                "start": {
                    "title": "Start",
                    "type": "integer"
                },
                "timePeriod": {
                    "title": "Time period",
                    "type": "integer"
                },
                "equation": {
                    "title": "Equation",
                    "type": "string"
                },
                "score": {
                    "title": "Score",
                    "type": "number"
                },
                "usageAmounts": {
                    "title": "Usage amounts",
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            },
            "required": [
                "start",
                "timePeriod",
                "equation",
                "score",
                "usageAmounts"
            ]
        },
        "ForecastResponse": {
            "title": "ForecastResponse",
            "type": "object",
            "properties": {
                "forecastType": {
                    "$ref": "#/definitions/ForecastType"
                },
                "consumerGroup": {
                    "$ref": "#/definitions/ConsumerGroup"
                },
                "reference": {
                    "$ref": "#/definitions/RealData"
                },
                "forecast": {
                    "$ref": "#/definitions/ForecastData"
                }
            },
            "required": [
                "forecastType",
                "consumerGroup",
                "reference",
                "forecast"
            ]
        }
    }
}
```
> This scheme may also be found [here](schemas/response.json)
