"""This file will bootstrap the service and announce it at the service registry"""
import logging
import os

import py_eureka_client.eureka_client
import pydantic.error_wrappers

from data_models import ServiceSettings

if __name__ == '__main__':
    # Configure the logger for this service
    logger_level_raw = os.getenv('LOG_LEVEL', 'INFO')
    logger_level = getattr(logging, logger_level_raw.upper())
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(lineno)s - %(message)s',
        level=logger_level,
        force=True
    )
    logger = logging.getLogger('BOOTSTRAP')

    # Try reading the current settings
    settings = None
    try:
        settings = ServiceSettings()
    except pydantic.error_wrappers.ValidationError as parser_error:
        logger.error(f"Error while parsing the settings from env:\n{parser_error}")
        exit(1)
    if settings is None:
        logger.error("Error while reading the settings. The service will now exit")
        exit(2)
    # Debug log the settings read by pydantic
    logger.debug(f'Read the following settings: {settings.json()}')
    logger.info("Bootstrapping the forecast service...")

    # Registering the service at the service registry
    eureka_client = py_eureka_client.eureka_client.EurekaClient(
        eureka_server=f'http://{settings.eureka_hostname}:{settings.eureka_port}',
        app_name='water-usage-forecasts',
        should_discover=False,
        should_register=True,
        renewal_interval_in_secs=5
    )
    eureka_client.start()

