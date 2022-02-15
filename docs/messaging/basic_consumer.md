---
sidebar_label: basic_consumer
title: messaging.basic_consumer
---

AMQP Basic Consumer


## BasicAMQPConsumer Objects

```python
class BasicAMQPConsumer()
```

This consumer works asynchronously and consumes messages from a specified RabbitMQ server via

the AMQP v0-9-1 protocol. The consumer is based on the example made by the pika library.
Furthermore, this consumer will import an executor module which will handle the execution of
some actions based on the messages content and headers.


#### \_\_init\_\_

```python
def __init__(amqp_url: stricturl(allowed_schemes={'amqp'}, tld_required=False), amqp_exchange: str, amqp_queue: str)
```

Create a new BasicAMQPConsumer

This consumer will not connect itself to the message broker and start listening to the
queue on the exchange with the routing key.

**Arguments**:

- `amqp_url` (`str`): URL containing the connection settings to the AMQP Message Broker
- `amqp_exchange` (`str`): Name of the exchange which this consumer will use to listen to
- `amqp_queue` (`str`): Name of the queue the consumer will bind itself to

#### start

```python
def start()
```

Start the consumer and the consuming process


#### stop

```python
def stop()
```

Close the existing message broker connection in a clean way


#### \_\_connect

```python
def __connect() -> pika.SelectConnection
```

Open a connection to the AMQP message broker

**Returns**:

`pika.SelectConnection`: Connection to the message broker

#### \_\_open\_channel

```python
def __open_channel()
```

Open a new channel to the message broker


#### \_\_close\_channel

```python
def __close_channel()
```

Close the current channel


#### \_\_close\_connection

```python
def __close_connection()
```

Close the connection to the message broker


#### \_\_stop\_consuming

```python
def __stop_consuming()
```

This will stop the consuming of messages by this consumer


#### \_\_reconnect

```python
def __reconnect()
```

Set the reconnection need to true


#### \_\_setup\_exchange

```python
def __setup_exchange()
```

Set up the exchange on the channel present in the consumer


#### \_\_setup\_queue

```python
def __setup_queue()
```

Set up a queue which is attached to the fanout exchange


#### \_\_enable\_message\_consuming

```python
def __enable_message_consuming()
```

This will start the consuming of messages by this consumer


#### \_\_callback\_connection\_opened

```python
def __callback_connection_opened(__connection: pika.BaseConnection)
```

Callback for a successful connection attempt.

If this callback is called, the consumer will try to open up a channel

**Arguments**:

- `__connection`: Connection handle which was opened

#### \_\_callback\_connection\_error

```python
def __callback_connection_error(__connection: pika.BaseConnection, __error: Exception)
```

Callback for a failed connection attempt

**Arguments**:

- `__connection` (`pika.BaseConnection`): Connection which could not be established
- `__error` (`Exception`): Connection error

#### \_\_callback\_connection\_closed

```python
def __callback_connection_closed(__connection: pika.connection.Connection, __reason: Exception)
```

Callback for an unexpected connection closure

**Arguments**:

- `__connection`: The connection which was closed
- `__reason`: The closure reason

#### \_\_callback\_channel\_opened

```python
def __callback_channel_opened(__channel: pika.channel.Channel)
```

Callback for a successfully opened channel

This will save the channel to the object and try to set up an exchange on this channel


#### \_\_callback\_channel\_closed

```python
def __callback_channel_closed(__channel: pika.channel.Channel, __reason: Exception)
```

Callback for a closed channel

**Arguments**:

- `__channel` (`pika.channel.Channel`): The closed channel
- `__reason` (`Exception`): Reason for closing the channel

#### \_\_callback\_cancel\_ok

```python
def __callback_cancel_ok(__frame: pika.frame.Method)
```

Callback which is called if the channel was cancelled successfully

**Arguments**:

- `__frame`: 

#### \_\_callback\_exchange\_declare\_ok

```python
def __callback_exchange_declare_ok(__frame: pika.frame.Method)
```

Callback used for a successful exchange declaration on the message broker

**Arguments**:

- `__frame`: Method frame

#### \_\_callback\_queue\_declare\_ok

```python
def __callback_queue_declare_ok(__frame: pika.frame.Method)
```

Callback for successfully declaring a queue on an exchange

**Arguments**:

- `__frame`: Frame indicating the status of the executed command

#### \_\_callback\_queue\_bind\_ok

```python
def __callback_queue_bind_ok(__frame: pika.frame.Method)
```

Callback for a successful queue bind

**Arguments**:

- `__frame`: 

#### \_\_callback\_queue\_delete\_ok

```python
def __callback_queue_delete_ok(__frame: pika.frame.Method)
```

Callback for a successful queue bind

**Arguments**:

- `__frame`: 

#### \_\_callback\_basic\_qos\_ok

```python
def __callback_basic_qos_ok(__frame: pika.frame.Method)
```

Callback for a successful QOS (Quality of Service) setup

**Arguments**:

- `__frame`: 

#### \_\_callback\_consumer\_cancelled

```python
def __callback_consumer_cancelled(__frame: pika.frame.Method)
```

Callback which will be called if the consumer was cancelled

**Arguments**:

- `__frame`: 

#### \_\_callback\_new\_message

```python
def __callback_new_message(channel: pika.channel.Channel, delivery: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, content: bytes)
```

Callback for new messages read from the server

**Arguments**:

- `channel`: Channel used to get the message
- `delivery`: Basic information about the message delivery
- `properties`: Message properties
- `content`: Message content

