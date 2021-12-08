"""Module implementing a consumer which will reonnect itself if the need arises"""
import asyncio
import logging
import sys
import time
import uuid
from typing import Optional

from py_eureka_client.eureka_client import (
    EurekaClient,
    INSTANCE_STATUS_UP,
    INSTANCE_STATUS_DOWN,
    INSTANCE_STATUS_OUT_OF_SERVICE
)
from pydantic import stricturl

from messaging.basic_consumer import BasicAMQPConsumer


class ReconnectingAMQPConsumer:
    """
    This consumer will automatically reconnect itself to the message broker if the connection was
    terminated in an unnatural way
    """

    def __init__(
            self,
            amqp_url: stricturl(tld_required=False, allowed_schemes={"amqp"}),
            amqp_exchange: str,
            eureka_client: EurekaClient,
            amqp_queue: str = "water-usage-forecast-service#" + str(uuid.uuid4()),
            amqp_reconnection_delay: float = 5.0,
            amqp_reconnection_tries: int = 3
    ):
        """Create a new ReconnectingAMQPConsumer

        :param amqp_url: URL pointing to the message broker
        :param amqp_exchange: Name of the exchange the consumer should attach itself to
        :param eureka_client: Instance of the service registry client
        :param amqp_queue: Name of the queue which should be bound to the exchange,
            defaults to "water-usage-forecast-service#" + UUID4
        :param amqp_reconnection_delay: Time which should be waited until a reconnection is tried
        :param amqp_reconnection_tries: Number of reconnection attempts
        """
        self.__amqp_url = amqp_url
        self.__amqp_exchange = amqp_exchange
        self.__eureka_client = eureka_client
        self.__amqp_queue = amqp_queue
        self.__amqp_reconnection_delay = amqp_reconnection_delay
        self.__amqp_reconnection_tries = amqp_reconnection_tries
        self.__logger = logging.getLogger(__name__)
        self.__consumer: Optional[BasicAMQPConsumer] = None
        self.__should_run = False
        self.__amqp_reconnection_try_counter = 0

    def start(self):
        """Start the consumer"""
        self.__consumer = BasicAMQPConsumer(
            amqp_url=self.__amqp_url,
            amqp_queue=self.__amqp_queue,
            amqp_exchange=self.__amqp_exchange
        )
        self.__should_run = True
        self.__run_consumer()

    def __run_consumer(self):
        while self.__should_run:
            self.__eureka_client.status_update(INSTANCE_STATUS_UP)
            self.__consumer.start()
            self.__eureka_client.status_update(INSTANCE_STATUS_OUT_OF_SERVICE)
            if self.__amqp_reconnection_try_counter < self.__amqp_reconnection_tries:
                self.__reconnect()
            else:
                self.__eureka_client.status_update(INSTANCE_STATUS_DOWN)
                sys.exit(2)

    def __reconnect(self):
        """Try to reconnect to the message broker

        :return:
        """
        if self.__consumer.should_reconnect:
            self.__amqp_reconnection_try_counter += 1
            self.__consumer.stop()
            self.__logger.info(
                'Reconnecting to the message broker in %d seconds',
                self.__amqp_reconnection_delay
            )
            time.sleep(self.__amqp_reconnection_delay)
            self.start()
