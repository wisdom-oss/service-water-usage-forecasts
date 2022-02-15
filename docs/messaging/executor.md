---
sidebar_label: executor
title: messaging.executor
---

This module will be used to execute the incoming messages


#### execute

```python
def execute(message: dict) -> dict
```

AMQP Message Executor

This executor is responsible for selecting the correct forecasting procedures depending on
the data present in the message. The message is expected as a dictionary.

**Arguments**:

- `message` (`dict`): Message from the message broker

**Returns**:

Response which should be sent back to the message broker

