"""Module containing all settings which are used throughout the whole application"""
from pydantic import BaseSettings, AmqpDsn, stricturl, Field


class ServiceSettings(BaseSettings):
    """Settings related to the general operation of the service"""
    
    name: str = Field(
        default='water-usage-forecast-calculations',
        title='Service Name',
        description='The name of the service which is used for registering at the service '
                    'registry and for authorization in AMQP requests/responses',
        env='SERVICE_NAME'
    )
    """
    Service Name
    
    The name of the service which is used for registering at the service registry and for
    authorization in AMQP responses
    """
    
    log_level: str = Field(
        default='INFO',
        title='Logging Level',
        description='The level of logging which the root logger will be configured for',
        env='SERVICE_LOG_LEVEL'
    )
    """
    Logging Level
    
    The level of logging which will displayed during the service execution
    """
    
    class Config:
        """Configuration of the Service Settings"""
        
        env_file = '.service.env'
        """The location of the environment file from which the settings may be read"""
        

class ServiceRegistrySettings(BaseSettings):
    """Settings related to the connection to the service registry"""
    
    host: str = Field(
        default=...,
        title='Service Registry Host',
        description='The hostname or ip address of the service registry on which the service will '
                    'register itself',
        env='SERVICE_REGISTRY_HOST'
    )
    """
    Service Registry Host [REQUIRED]
    
    The hostname or IP address of the host on which the service registry runs.
    """
    
    port: int = Field(
        default=8761,
        title='Service Registry Port',
        description='The port on which the service registry listens, defaults 8761',
        env='SERVICE_REGISTRY_PORT'
    )
    """
    Service Registry Port [OPTIONAL, default value: `8761`]
    
    The port on which the service registry listens
    """
    
    class Config:
        """The configuration of hte service registry settings"""
        
        env_file = '.registry.env'
        """The location of the environment file from which the settings may be read"""


class AMQPSettings(BaseSettings):
    """Settings related to the AMQP connection and the communication"""
    
    dsn: AmqpDsn = Field(
        default=...,
        title='AMQP Data Source Name',
        description='The URI pointing to the installation of a AMQP-0-9-1 compatible message '
                    'broker',
        env='AMQP_DSN'
    )
    """
    AMQP Data Source Name [REQUIRED]
    
    The URI pointing to the installation of a AMQP-0-9-1 compatible message broker
    """
    
    exchange: str = Field(
        default='water-usage-forecasts',
        title='AMQP Exchange Name',
        description='The name of the AMQP exchange this service listens to for messages',
        env='AMQP_EXCHANGE'
    )
    """
    AMQP Exchange Name [OPTIONAL, default value: `water-usage-forecasts`]
    
    The name of the AMQP exchange which this service listens on for new messages
    """
    
    class Config:
        """Configuration of the AMQP connection settings"""
        
        env_file = '.amqp.env'
        """The location of the environment file from which the settings may be read"""
    