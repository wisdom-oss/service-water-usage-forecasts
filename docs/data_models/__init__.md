---
sidebar_label: data_models
title: data_models
---

Module for describing incoming and outgoing data and settings


## ServiceSettings Objects

```python
class ServiceSettings(BaseSettings)
```

Settings this service will use throughout the execution


#### eureka\_hostname

Hostname of the eureka service registry at which the instance will announce itself as available


#### amqp\_url

Connection URL for the message broker


#### amqp\_exchange

Name of the amqp exchange the consumer will bind itself to.


