"""This file will bootstrap the service and announce it at the service registry"""
import asyncio
import logging
import os
import signal
import sys
import time
from threading import Thread
from typing import Optional

import pydantic.error_wrappers
from py_eureka_client.eureka_client import EurekaClient

import tools
from messaging.reconnecting_consumer import ReconnectingAMQPConsumer
from settings import AMQPSettings, ServiceRegistrySettings, ServiceSettings

_amqp_server: Optional[ReconnectingAMQPConsumer] = None
_amqp_thread: Optional[Thread] = None


def signal_handler(signum, frame):
    raise KeyboardInterrupt


if __name__ == '__main__':
    # Try reading the current settings
    _service_settings = ServiceSettings()
    logging.basicConfig(
        format='%(levelname)-8s | %(asctime)s | %(name)-25s | %(message)s',
        level=tools.resolve_log_level(_service_settings.log_level)
    )
    # Log a startup message
    logging.info(f'Starting the {_service_settings.name} service')
    logging.debug('Reading the settings for the AMQP connection')
    try:
        _amqp_settings = AMQPSettings()
    except pydantic.ValidationError as error:
        logging.error('The settings for the AMQP connection could not be read')
        sys.exit(1)
    logging.debug('Reading the settings for the Service Registry connection')
    try:
        _registry_settings = ServiceRegistrySettings()
    except pydantic.ValidationError as error:
        logging.error('The settings for the Service Registry could not be read')
        sys.exit(2)
    
    # Get the current event loop
    _loop = asyncio.get_event_loop()
    # Check if the service registry is reachable
    logging.info('Checking the communication to the service registry')
    _registry_available = _loop.run_until_complete(
        tools.is_host_available(
            host=_registry_settings.host,
            port=_registry_settings.port
        )
    )
    if not _registry_available:
        logging.critical(
            'The service registry is not reachable. The service may not be reachable via the '
            'Gateway'
        )
        sys.exit(4)
    else:
        logging.info('SUCCESS: The service registry appears to be running')
    # Check if the message broker is reachable
    logging.info('Checking the communication to the message broker')
    _message_broker_available = _loop.run_until_complete(
        tools.is_host_available(
            host=_amqp_settings.dsn.host,
            port=5672 if _amqp_settings.dsn.port is None else int(_amqp_settings.dsn.port)
        )
    )
    if not _message_broker_available:
        logging.critical(
            'The message broker is not reachable. Since this is a security issue the service will '
            'not start'
        )
        sys.exit(5)
    else:
        logging.info('SUCCESS: The message registry appears to be running')
    
    logging.info('Creating a new service registry client')
    _eureka_client_options = {
        'eureka_server':            f'http://{_registry_settings.host}:{_registry_settings.port}',
        'app_name':                 _service_settings.name,
        'instance_port':            65535,  # Port 65535 is used to signalize that the service is
        # not usable via HTTP
        'should_register':          True,
        'should_discover':          False,
        'renewal_interval_in_secs': 1,
        'duration_in_secs':         5
    }
    logging.debug('Client Properties: %s', _eureka_client_options)
    __service_registry_client = EurekaClient(**_eureka_client_options)
    # Start the registry client
    __service_registry_client.start()
    __service_registry_client.status_update('STARTING')
    # Set the status of this service to starting to disallow routing to them
    try:
        _amqp_server = ReconnectingAMQPConsumer()
        _amqp_thread = Thread(
            target=_amqp_server.start,
            daemon=False
        )
        _amqp_thread.start()
        __service_registry_client.status_update('UP')
        signal.signal(signal.SIGTERM, signal_handler)
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        _amqp_server.stop()
        _amqp_thread.join()
        __service_registry_client.stop()
