"""Module for describing incoming and outgoing data and settings"""
from pydantic import BaseSettings, Field, conint, constr


class ServiceSettings(BaseSettings):
    """
    Settings this service will use throughout the execution
    """

    eureka_hostname: constr(strip_whitespace=True, to_lower=True, min_length=1) = Field(
        # Require this setting to be set
        default=...,
        # Name of the environment variable which will be read
        env="EUREKA_HOSTNAME"
    )
    """
    Hostname of the eureka service registry at which the instance will announce itself as available
    """

    eureka_port: conint(gt=0, lt=65536) = Field(
        default=8761,
        env="EUREKA_PORT"
    )
    """
    Port of the eureka installation, defaults to port 8761
    """
