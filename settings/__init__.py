"""Settings for the service"""
import pika.exchange_type
import pydantic


class ServiceSettings(pydantic.BaseSettings):
    """Settings for the general execution of this service"""
    
    name: str = pydantic.Field(
        default='amqp-authorization-service',
        title='Application Name',
        description='The name of the service which will be used when registering the service at '
                    'the service registry',
        env='SERVICE_NAME'
    )
    """
    Application Name
    
    The name of the microservice which is used for registering at the service registry
    """

    log_level: str = pydantic.Field(
        default='INFO',
        title='Logging Level',
        description='The level of logging which the root logger will use',
        env='SERVICE_LOG_LEVEL'
    )
    """
    Logging Level

    The level of logging which will be used by the root logger
    """

    log_format: str = pydantic.Field(
        default='%(levelname)-8s | %(asctime)s | %(name)s | %(message)s',
        title='Logging Format',
        description='The format of logging which the root logger will use',
        env='SERVICE_LOG_FORMAT'
    )
    """
    Logging Format

    The format which will be used by the root logger
    """

    class Config:
        """Configuration of the service settings"""
    
        env_file = 'env\\.application.env'
        """Allow loading the values for the service settings from the specified file"""


class AMQPSettings(pydantic.BaseSettings):
    """Settings related to the connection to a AMQPv0-9-1 compatible message broker"""
    
    dsn: pydantic.AmqpDsn = pydantic.Field(
        default=...,
        alias='AMQP_DSN',
        title='Data Source Name',
        description='A data source name pointing to a message broker supporting the AMQPv0-9-1 '
                    'protocol',
        env='AMQP_DSN'
    )
    """
    Data Source Name
    
    A URI pointing to a message broker. The message broker needs to implement the version 0-9-1
    of the Advanced Message Queuing Protocol.
    """
    
    exchange_name: str = pydantic.Field(
        default=...,
        alias='AMQP_EXCHANGE_NAME',
        title='Message Broker Exchange Name',
        description='The name of the exchange the service will bind itself to for receiving '
                    'messages',
        env='AMQP_EXCHANGE_NAME'
    )
    """
    Exchange Name
    
    The name of the exchange this service will bind. The bound exchange will be used to consume
    messages from other microservices
    """
    
    exchange_type: pika.exchange_type.ExchangeType = pydantic.Field(
        default=pika.exchange_type.ExchangeType.fanout,
        alias='AMQP_EXCHANGE_TYPE',
        title='Exchange Type',
        description='The type of the specified exchange',
        env='AMQP_EXCHANGE_TYPE'
    )
    """
    Exchange Type
    
    The type of exchange this service will bind itself to.
    
    **Important:** If the exchange already exists the supplied exchange type needs to match the
    one with which the exchange has been created.
    
    Available values:
       * direct
       * fanout (default)
       * headers
       * topic
    """

    class Config:
        """Configuration of the service settings"""
    
        env_file = 'env\\.amqp.env'
        """Allow loading the values for the service settings from the specified file"""
