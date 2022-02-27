import logging
import secrets
import time
from threading import Event
from typing import Optional

from messaging.basic_consumer import BasicAMQPConsumer
from settings import AMQPSettings


class ReconnectingAMQPConsumer:
    """
    This consumer will automatically reconnect itself to the message broker if the connection was
    terminated in an unnatural way
    """

    def __init__(
            self,
            amqp_queue: str = "authorization-service#" + secrets.token_hex(nbytes=4),
            amqp_reconnection_delay: float = 5.0,
            amqp_reconnection_tries: int = 3
    ):
        """Create a new ReconnectingAMQPConsumer

        :param amqp_queue: Name of the queue which should be bound to the exchange,
            defaults to "water-usage-forecast-service#" + UUID4
        :param amqp_reconnection_delay: Time which should be waited until a reconnection is tried
        :param amqp_reconnection_tries: Number of reconnection attempts
        """
        __amqp_settings = AMQPSettings()
        self.__amqp_url = __amqp_settings.dsn
        self.__amqp_exchange = __amqp_settings.exchange
        self.__amqp_queue = amqp_queue
        self.__amqp_reconnection_delay = amqp_reconnection_delay
        self.__amqp_reconnection_tries = amqp_reconnection_tries
        self.__logger = logging.getLogger('AMQP.ReconnectingConsumer')
        self.__consumer: Optional[BasicAMQPConsumer] = BasicAMQPConsumer(
            amqp_url=self.__amqp_url,
            amqp_queue=self.__amqp_queue,
            amqp_exchange=self.__amqp_exchange
        )
        self.stop_event = Event()
        self.__amqp_reconnection_try_counter = amqp_reconnection_tries
        self.__logger.info('Created a new ReconnectingConsumer')

    def start(self):
        """Start the consumer"""
        self.__logger.info('Clearing any set events.')
        self.stop_event.clear()
        self.__logger.info('Starting the contained BasicConsumer')
        self.__run_consumer()

    def stop(self):
        self.__logger.info('Received shutdown trigger')
        self.stop_event.set()
        self.__consumer.stop()

    def __run_consumer(self):
        while not self.stop_event.is_set():
            self.__consumer.start()
            if self.__amqp_reconnection_try_counter < self.__amqp_reconnection_tries:
                self.__logger.warning('Trying to reconnect to the message broker. Try #%i', self.__amqp_reconnection_tries)
                self.__reconnect()
            else:
                if not self.__consumer.graceful_shutdown:
                    self.__logger.critical('The amount of reconnection tries has been exceeded. No '
                                           'new reconnection try will be executed until the '
                                           'application is restarted')
                    self.stop()
                else:
                    self.__logger.info('Successfully shut down the Reconnecting Consumer')

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
