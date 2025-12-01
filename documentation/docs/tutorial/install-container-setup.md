---
hide:
  - toc
---

# Container setup installation

!!! tip "Recommended installation"

    This installation method is recommended for new installations of DSMR-reader.
    It uses containerization (Podman) to run DSMR-reader and its dependencies in isolated environments.
    This approach simplifies the installation process, enhances security, and makes it **a lot** easier for you to update.
    You'll no longer need to manually update Python or DSMR-reader dependencies manually!

    Presumes using a RaspberryPi (5) or similar hardware. Older hardware *may* work, depending on the I/O.


## OS packages
- Install system packages:
```shell
sudo apt-get update
sudo apt-get install podman podman-compose podman-docker crun
podman info --debug

# It's not mandatory to use "ser2net", 
# but it _may_ avoid some USB permission issues at the "cost" of running ser2net
sudo apt-get install ser2net
```

## OS user
- Add dedicated system user for DSMR-reader to run on:
```shell
sudo useradd dsmrreader --create-home
sudo loginctl enable-linger dsmrreader

# Write down the IDs in the output (they are likely the same, e.g. "1001") 
id --user dsmrreader
id --group dsmrreader
```

## DSMR-reader user
- Login as "dsmrreader" user:
```shell
sudo su - dsmrreader
```

- Download container Compose template file:
```shell
# TODO: Change to "latest" after releasing DSMR-reader v6.
wget https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/development/provisioning/container/compose.prod.yml -O compose.yml
```

- Configure Compose file to your needs
```shell
# Or use "nano" instead of "vi" if you prefer that text editor.
vi compose.yml
```

```yaml
# Simplified compose.yml - Find DUID=1001 and DGID=1001 and change them if dsmrreader has different IDs on your system.
services:
  dsmrdb:
      environment:
        # Set the user and group IDs, e.g. DUID=1001 (id --user dsmrreader) and DGID=1001 (id --group dsmrreader) of the "id" commands executed above.
        DUID=1001
        DGID=1001
  dsmr:
      environment:
        # Set the user and group IDs, e.g. DUID=1001 (id --user dsmrreader) and DGID=1001 (id --group dsmrreader) of the "id" commands executed above.
        DUID=1001
        DGID=1001
```

## Running
- Try running the containers:
```shell
# This may take a few minutes, mostly depending on the hardware available.
podman-compose up -d
```

- Check folders created:
```shell
ls -l
```
- It should now at least have the file `compose.yml` and folders `dsmr_database` and `dsmr_backups`.
- Check logs for any weird stuff:
```shell
podman-compose logs -f
```
