"""
    Default settings as defined in the base.py config.
    Some settings can be overridden by system env vars or the .env.
"""
from decouple import Csv

from dsmrreader.config.base import *
from dsmrreader.config.django_overrides import *
import dsmrreader


"""
DSMR-reader project settings (non Django related).
"""

DSMRREADER_LOGLEVEL = config('DSMRREADER_LOGLEVEL', cast=str, default=None)

if DSMRREADER_LOGLEVEL in ('DEBUG', 'WARNING'):
    LOGGING['loggers']['dsmrreader']['level'] = DSMRREADER_LOGLEVEL

CACHES['mqtt']['TIMEOUT'] = config('DSMRREADER_MQTT_MAX_CACHE_TIMEOUT', cast=int, default=0)

DSMRREADER_PLUGINS = config('DSMRREADER_PLUGINS', cast=Csv(post_process=tuple), default='')

# Officially we only support PostgreSQL, but w/e.
DSMRREADER_SUPPORTED_DB_VENDORS = ('postgresql', 'mysql')

DSMRREADER_BACKUP_PG_DUMP = 'pg_dump'
DSMRREADER_BACKUP_MYSQLDUMP = 'mysqldump'
DSMRREADER_BACKUP_SQLITE = 'sqlite3'
DSMRREADER_REST_FRAMEWORK_API_USER = 'api-user'

DSMRREADER_MANAGEMENT_COMMANDS_PID_FOLDER = '/tmp/'

DSMRREADER_MAIN_BRANCH = 'v4'
DSMRREADER_VERSION = dsmrreader.__version__
DSMRREADER_RAW_VERSION = dsmrreader.VERSION
DSMRREADER_USER_AGENT = 'DSMR-reader v{}'.format(DSMRREADER_VERSION)
DSMRREADER_LATEST_TAGS_LIST = 'https://api.github.com/repos/dsmrreader/dsmr-reader/tags'

# Scheduled Process modules.
DSMRREADER_MODULE_EMAIL_BACKUP = 'dsmr_backup.services.email.run'
DSMRREADER_MODULE_AUTO_UPDATE_CHECKER = 'dsmr_backend.services.update_checker.run'
DSMRREADER_MODULE_WEATHER_UPDATE = 'dsmr_weather.services.run'
DSMRREADER_MODULE_STATS_GENERATOR = 'dsmr_stats.services.run'
DSMRREADER_MODULE_MINDERGAS_EXPORT = 'dsmr_mindergas.services.run'
DSMRREADER_MODULE_GENERATE_CONSUMPTION = 'dsmr_consumption.services.run'
DSMRREADER_MODULE_RETENTION_DATA_ROTATION = 'dsmr_datalogger.services.retention.run'
DSMRREADER_MODULE_DAILY_BACKUP = 'dsmr_backup.services.backup.run'
DSMRREADER_MODULE_DROPBOX_EXPORT = 'dsmr_dropbox.services.run'
DSMRREADER_MODULE_PVOUTPUT_EXPORT = 'dsmr_pvoutput.services.run'

# Refers to the Dropbox app "Official DSMR-Reader" which is a "Scoped App (App Folder)". Public access allowed with PKCE
DSMRREADER_DROPBOX_DEFAULT_APP_KEY = 'w5z4vlw9t2dqq5g'
DSMRREADER_DROPBOX_MAX_FILE_MODIFICATION_TIME = 60 * 60 * 24 * 7
DSMRREADER_DROPBOX_SYNC_INTERVAL = 1  # Only check for changes once per hour.
DSMRREADER_DROPBOX_ERROR_INTERVAL = 12  # Skip new files for 12 hours when insufficient space in Dropbox account.

DSMRREADER_CLIENT_TIMEOUT = 20

# See #1391 #1387 #1393 and https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/
DSMRREADER_MQTT_QOS_LEVEL = 2

# Max telegrams to compact in a single run.
DSMRREADER_COMPACT_MAX = 1024

# When processes should reconnect to the DB, to ensure the connection is still there.
DSMRREADER_MAX_DATABASE_CONNECTION_SESSION_IN_SECONDS = 30 * 60

# Maximum interval allowed since the latest reading, before ringing any alarms.
DSMRREADER_STATUS_READING_OFFSET_MINUTES = 60

DSMRREADER_STATUS_MAX_UNPROCESSED_READINGS = 100
DSMRREADER_STATUS_WARN_OVER_EXCESSIVE_READING_COUNT = 20 * 1000 * 1000  # In millions
DSMRREADER_STATUS_WARN_OVER_EXCESSIVE_DATABASE_SIZE = 1 * 1000 * 1000 * 1000  # In GB

# The cooldown period until the next status notification will be sent.
DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS = 3
DSMRREADER_DAILY_NOTIFICATION_TIME_HOURS = 6  # E.g. 6 = 6 AM

# The time scheduled processes are allowed to lagg behind before failing the monitoring.
DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES = 15

# Days statistics should be generated daily.
DSMRREADER_STATUS_ALLOWED_DAY_STATISTICS_LAGG_IN_DAYS = 2

# Number of queued messages the application will retain. Any excess will be purged.
DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE = config('DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE', cast=int, default=5000)
DSMRREADER_INFLUXDB_MAX_MEASUREMENTS_IN_QUEUE = 500

# Number of hours to clean up in one run of applying retention.
DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN = 24

DSMRREADER_BUIENRADAR_API_URL = 'https://data.buienradar.nl/2.0/feed/json'

# https://pvoutput.org/help.html#api-addstatus
DSMRREADER_PVOUTPUT_ADD_STATUS_URL = 'https://pvoutput.org/service/r2/addstatus.jsp'

DSMRREADER_DATALOGGER_MIN_SLEEP_FOR_RECONNECT = 1.0

DSMRREADER_CAPABILITIES_CACHE = 'capabilities'
DSMRREADER_MONITORING_CACHE = 'monitoring_status'

# Allow users to disable the warnings. Use at own risk.
if config('DSMRREADER_SUPPRESS_STORAGE_SIZE_WARNINGS', cast=bool, default=False):
    DSMRREADER_STATUS_WARN_OVER_EXCESSIVE_READING_COUNT = 999 * 1000 * 1000  # In millions
    DSMRREADER_STATUS_WARN_OVER_EXCESSIVE_DATABASE_SIZE = 999 * 1000 * 1000 * 1000  # In GB

DSMRREADER_SYSTEM_CHECK_001 = 'dsmrreader.E001'
DSMRREADER_SYSTEM_CHECK_002 = 'dsmrreader.E002'
