"""Water Usage Forecast Service"""
import asyncio
import logging
import os
import signal
import sys
import threading
import time
import typing

import amqp_rpc_server
import pydantic.error_wrappers

import server_functions
import settings
import tools

_stop_event = threading.Event()
_stop_event.clear()

amqp_server: typing.Optional[amqp_rpc_server.Server] = None


def signal_handler(sign, frame):
    logging.info("Received shutdown signal. Stopping the AMQP server")
    _stop_event.set()


if __name__ == "__main__":
    # Read the service settings and configure the logging
    _service_settings = settings.ServiceSettings()
    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
        level=_service_settings.logging_level.upper(),
    )
    logging.info('Starting the "%s" service as PID: %s', _service_settings.name, os.getpid())
    # = Read the AMQP Settings and check the server connection =
    try:
        _amqp_settings = settings.AMQPSettings()
    except pydantic.error_wrappers.ValidationError as config_error:
        logging.critical(
            "Unable to read the settings for the connection to the message broker",
            exc_info=config_error,
        )
        sys.exit(1)
    # Now check the connection to the message broker
    logging.debug(
        "Successfully read the settings for the message broker connection:\n%s",
        _amqp_settings.json(indent=2, by_alias=True),
    )
    # Set the port if it is None
    _amqp_settings.dsn.port = 5672 if _amqp_settings.dsn.port is None else _amqp_settings.dsn.port
    # Check the connectivity to the message broker
    _message_broker_available = asyncio.run(
        tools.is_host_available(host=_amqp_settings.dsn.host, port=_amqp_settings.dsn.port)
    )
    if not _message_broker_available:
        logging.critical(
            "The specified message broker (Host: %s | Port: %s) is not reachable",
            _amqp_settings.dsn.host,
            _amqp_settings.dsn.port,
        )
        sys.exit(1)

    try:
        _db_settings = settings.DatabaseSettings()
    except pydantic.error_wrappers.ValidationError as config_error:
        logging.critical(
            "Unable to read the settings for the connection to the database",
            exc_info=config_error,
        )
        sys.exit(1)
    # Now check the connection to the message broker
    logging.debug(
        "Successfully read the settings for the database connection:\n%s",
        _db_settings.json(indent=2, by_alias=True),
    )
    # Set the port if it is None
    _db_settings.dsn.port = 5432 if _db_settings.dsn.port is None else _db_settings.dsn.port
    # Check the connectivity to the message broker
    _message_broker_available = asyncio.run(
        tools.is_host_available(host=_db_settings.dsn.host, port=_db_settings.dsn.port)
    )
    if not _message_broker_available:
        logging.critical(
            "The specified PostgreSQL database (Host: %s | Port: %s) is not reachable",
            _db_settings.dsn.host,
            _db_settings.dsn.port,
        )
        sys.exit(1)
    logging.info("Passed all pre-startup checks and all dependent services are reachable")
    logging.info("Starting the AMQP Server")
    amqp_server = amqp_rpc_server.Server(
        amqp_dsn=_amqp_settings.dsn,
        exchange_name=_amqp_settings.bind_exchange,
        content_validator=server_functions.content_validator,
        executor=server_functions.executor,
        max_reconnection_attempts=1,
    )
    # Attach the signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    # Start the server
    amqp_server.start_server()
    while not _stop_event.is_set():
        try:
            amqp_server.raise_exceptions()
            time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("Detected a KeyboardInterrupt. Stopping the AMQP server")
            _stop_event.set()
        except amqp_rpc_server.exceptions.MaxConnectionAttemptsReached:
            sys.exit(1)
    amqp_server.stop_server()
    logging.info("Stopped the AMQP Server. Exiting the service")
