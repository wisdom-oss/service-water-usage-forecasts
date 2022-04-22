import pydantic


class ServiceSettings(pydantic.BaseSettings):
    """Settings which are related to the general service execution"""

    name: str = pydantic.Field(
        default="water-usage-forecasts-calculations",
        alias="CONFIG_SERVICE_NAME",
        env="CONFIG_SERVICE_NAME",
    )
    """
    Microservice Name

    The name of the service which is used for registering at the service registry
    """

    logging_level: str = pydantic.Field(
        default="INFO", alias="CONFIG_LOGGING_LEVEL", env="CONFIG_LOGGING_LEVEL"
    )
    """
    Logging Level

    The logging level which will be visible on the stdout
    """

    class Config:
        env_file = ".env"


class AMQPSettings(pydantic.BaseSettings):
    """Settings which are related to the communication with our message broker"""

    dsn: pydantic.AmqpDsn = pydantic.Field(
        default=..., alias="CONFIG_AMQP_DSN", env="CONFIG_AMQP_DSN"
    )
    """
    Advanced Message Queueing Protocol data source name

    The data source name (expressed as URI) pointing to a AMQPv-0-9-1 compatible message broker
    """

    bind_exchange: str = pydantic.Field(
        default="water-usage-forecasts",
        alias="CONFIG_AMQP_BIND_EXCHANGE",
        env="CONFIG_AMQP_BIND_EXCHANGE",
    )
    """
    Incoming Message Broker Exchange

    The exchange that this service will bind itself to, for receiving messages
    """

    class Config:
        env_file = ".env"


class DatabaseSettings(pydantic.BaseSettings):
    """Settings which are related to the database connection"""

    dsn: pydantic.PostgresDsn = pydantic.Field(
        default=..., alias="CONFIG_DB_DSN", env="CONFIG_DB_DSN"
    )
    """
    PostgreSQL data source name

    The data source name (expressed as URI) pointing to the installation of the used postgresql database
    """

    class Config:
        env_file = ".env"
