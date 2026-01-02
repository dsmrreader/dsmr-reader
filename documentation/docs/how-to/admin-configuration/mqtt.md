# MQTT

The application has native support for MQTT. In the screen displayed below you can enter all information about the broker you're using.

![Broker settings](../../static/screenshots/admin/mqttbrokersettings.png)

There are multiple configurations available for sending MQTT messages to your broker.
You can enable them separately, depending on your needs.
Many of these also allow you to define which fields are sent and how they should be identified in messages sent to the broker.

## Day totals

This allows you to receive the day totals in JSON format:

![MQTT JSON day Totals](../../static/screenshots/admin/jsondaytotalsmqttsettings.png)

The same data, but split among topics. This allows you to post a single piece of data on a separate topic:

![MQTT Split Topic Day Totals](../../static/screenshots/admin/splittopicdaytotalsmqttsettings.png)

## Meter statistics

Statistics of your meter, split among topics:

![MQTT Split Topic Meter Statistics](../../static/screenshots/admin/splittopicmeterstatisticsmqttsettings.png)

## Telegram

Telegram in JSON format:

![MQTT JSON Telegram](../../static/screenshots/admin/jsontelegrammqttsettings.png)

Or split among topics:

![MQTT Split Topic Telegram](../../static/screenshots/admin/splittopictelegrammqttsettings.png)

Or in raw DSMR protocol format (when available):

![MQTT Raw Telegram](../../static/screenshots/admin/rawtelegrammqttsettings.png)
