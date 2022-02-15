---
sidebar_label: reconnecting_consumer
title: messaging.reconnecting_consumer
---

Module implementing a consumer which will reonnect itself if the need arises


## ReconnectingAMQPConsumer Objects

```python
class ReconnectingAMQPConsumer()
```

This consumer will automatically reconnect itself to the message broker if the connection was

terminated in an unnatural way


#### \_\_init\_\_

```python
def __init__(amqp_url: stricturl(tld_required=False, allowed_schemes={"amqp"}), amqp_exchange: str, eureka_client: EurekaClient, amqp_queue: str = "water-usage-forecast-service#" + str(uuid.uuid4()), amqp_reconnection_delay: float = 5.0, amqp_reconnection_tries: int = 3)
```

Create a new ReconnectingAMQPConsumer

**Arguments**:

- `amqp_url`: URL pointing to the message broker
- `amqp_exchange`: Name of the exchange the consumer should attach itself to
- `eureka_client`: Instance of the service registry client
- `amqp_queue`: Name of the queue which should be bound to the exchange,
defaults to &quot;water-usage-forecast-service#&quot; + UUID4
- `amqp_reconnection_delay`: Time which should be waited until a reconnection is tried
- `amqp_reconnection_tries`: Number of reconnection attempts

#### start

```python
def start()
```

Start the consumer


#### \_\_reconnect

```python
def __reconnect()
```

Try to reconnect to the message broker


