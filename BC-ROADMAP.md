# Backwards incompatibility roadmap

## v4.x

### dsmr_mqtt
- Refactor to dsmr_export
- Add: Mqtt, mindergas, pvoutput
- Mandatory process now

### Backend status_info()
- Remove backup status info from `tools`, now available in `scheduled_processes`
- Remove mindergas status info from `tools`, now available in `scheduled_processes`
- Maybe also drop the entire API support for status_info() 