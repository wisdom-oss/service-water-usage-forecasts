"""Module for describing incoming and outgoing data and settings"""
from pydantic import BaseSettings, Field, conint, constr, stricturl


class ServiceSettings(BaseSettings):
    """
    Settings this service will use throughout the execution
    """

    eureka_hostname: str = Field(
        # Require this setting to be set
        default=...,
        # Name of the environment variable which will be read
        env="SERVICE_REGISTRY_HOST"
    )
    """
    Hostname of the eureka service registry at which the instance will announce itself as available
    """

    amqp_url: stricturl(tld_required=False, allowed_schemes={"amqp"}) = Field(
        default=...,
        env="AMQP_DSN"
    )
    """Connection URL for the message broker"""

    amqp_exchange: str = Field(
        default='weather-forecast-requests',
        env='AMQP_EXCHANGE'
    )
    """Name of the amqp exchange the consumer will bind itself to."""
