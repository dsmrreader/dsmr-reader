from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView

from dsmr_api.models import APISettings
from dsmr_backend.models.settings import BackendSettings, EmailSettings
from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.settings import DataloggerSettings, RetentionSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_influxdb.models import InfluxdbIntegrationSettings
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_mqtt.models.settings.consumption import JSONGasConsumptionMQTTSettings, SplitTopicGasConsumptionMQTTSettings
from dsmr_mqtt.models.settings.day_totals import JSONDayTotalsMQTTSettings, SplitTopicDayTotalsMQTTSettings
from dsmr_mqtt.models.settings.meter_statistics import SplitTopicMeterStatisticsMQTTSettings
from dsmr_mqtt.models.settings.telegram import JSONTelegramMQTTSettings, RawTelegramMQTTSettings, \
    SplitTopicTelegramMQTTSettings
from dsmr_notification.models.settings import NotificationSetting
from dsmr_pvoutput.models.settings import PVOutputAPISettings, PVOutputAddStatusSettings
from dsmr_weather.models.settings import WeatherSettings


class Configuration(LoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/configuration.html'

    def get_context_data(self, **kwargs):
        context_data = super(Configuration, self).get_context_data(**kwargs)
        # 20+ queries, we should cache this at some point.
        context_data.update(dict(
            api_settings=APISettings.get_solo(),
            backend_settings=BackendSettings.get_solo(),
            backup_settings=BackupSettings.get_solo(),
            consumption_settings=ConsumptionSettings.get_solo(),
            datalogger_settings=DataloggerSettings.get_solo(),
            dropbox_settings=DropboxSettings.get_solo(),
            email_settings=EmailSettings.get_solo(),
            frontend_settings=FrontendSettings.get_solo(),
            mindergas_settings=MinderGasSettings.get_solo(),
            mqtt_broker_settings=MQTTBrokerSettings.get_solo(),
            mqtt_jsondaytotals_settings=JSONDayTotalsMQTTSettings.get_solo(),
            mqtt_splittopicdaytotals_settings=SplitTopicDayTotalsMQTTSettings.get_solo(),
            mqtt_jsongasconsumption_settings=JSONGasConsumptionMQTTSettings.get_solo(),
            mqtt_splittopicgasconsumption_settings=SplitTopicGasConsumptionMQTTSettings.get_solo(),
            mqtt_splittopicmeterstatistics_settings=SplitTopicMeterStatisticsMQTTSettings.get_solo(),
            mqtt_jsontelegram_settings=JSONTelegramMQTTSettings.get_solo(),
            mqtt_rawtelegram_settings=RawTelegramMQTTSettings.get_solo(),
            mqtt_splittopictelegram_settings=SplitTopicTelegramMQTTSettings.get_solo(),
            notification_settings=NotificationSetting.get_solo(),
            pvoutput_api_settings=PVOutputAPISettings.get_solo(),
            pvoutput_addstatus_settings=PVOutputAddStatusSettings.get_solo(),
            retention_settings=RetentionSettings.get_solo(),
            weather_settings=WeatherSettings.get_solo(),
            influxdb_settings=InfluxdbIntegrationSettings.get_solo(),
        ))
        return context_data
