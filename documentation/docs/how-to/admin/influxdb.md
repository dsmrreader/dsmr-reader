# Admin settings: InfluxDB

!!! abstract "For your information"

    This is a feature using or integrating a **third party** and may or may not break along the years.

    Usually this depends on the third party supporting it and the amount of (re)work needed in DSMR-reader to keep it backward/forward compatible.

!!! failure "Deprecated feature"

    The Dropbox feature will be **dropped** from DSMR-reader in a future release.
    
    Reworking DSMR-reader to a Docker/container-only setup allows for generic third party integrations more easily.

    E.g. creating a [plugin script using post-processing hooks](../../reference/plugins.md) or a container that reads the DSMR-reader API and passed it to InfluxDB instead.
