---
hide:
  - toc
---

# Container setup installation

!!! note ""

    The [containerized version of DSMR-reader](https://github.com/xirixiz/dsmr-reader-docker) is created and maintained by Xirixiz a.k.a. Bram van Dartel.
    He has been working on it since 2017 and it is widely used by the DSMR-reader community. Since DSMR-reader v6 this is the only installation method supported.

    [DSMR-reader Docker on GitHub](https://github.com/xirixiz/dsmr-reader-docker){ .md-button .md-button--primary } [Xirixiz](https://github.com/xirixiz){ .md-button .md-button--primary }


This installation method is recommended for new installations of DSMR-reader.
It uses containerization (Podman) to run DSMR-reader and its dependencies in isolated environments.

!!! tip

    Recommended is using a RaspberryPi 5 or similar hardware. Older hardware *may* work, depending on the I/O.

This guide presumes you use Podman, however you can also use Docker or other container hosts that are compatible.
See also [container setup upgrade instructions](../../how-to/upgrade/to-v6.md) for a schematic overview of the setup.

[Schematic overview](../../how-to/upgrade/to-v6.md){ .md-button }


## Installation
### OS packages
- Install system packages:

``` shell
sudo apt-get update
sudo apt-get install podman podman-compose podman-docker crun
podman info --debug
```

``` shell
# It's not mandatory to use "ser2net", 
# but it _may_ avoid some USB permission issues at the "cost" of running ser2net
sudo apt-get install ser2net
```

### OS user
- Add dedicated system user for DSMR-reader to run on:

``` shell
sudo useradd dsmrreader --create-home
sudo loginctl enable-linger dsmrreader

# Write down the IDs in the output (they are likely the same, e.g. "1001") 
id --user dsmrreader
id --group dsmrreader
```

### DSMR-reader user
- Login as "dsmrreader" user:

``` shell
sudo su - dsmrreader
```

- Download container Compose template file:

``` shell
# TODO: Change to "latest" after releasing DSMR-reader v6.
wget https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/development/provisioning/container/compose.prod.yml -O compose.yml
```

- Configure Compose file to your needs:

``` shell
# Or use "nano" instead of "vi" if you prefer that text editor.
vi compose.yml
```

``` yaml title="compose.yml" hl_lines="6 7 11 12"
# Simplified - Find DUID=1001 and DGID=1001 and change them if dsmrreader has different IDs on your system.
services:
    dsmrdb:
        environment:
            # Set the user and group IDs, e.g. DUID=1001 (id --user dsmrreader) 
            # and DGID=1001 (id --group dsmrreader) of the "id" commands executed above.
            DUID=1001
            DGID=1001
    dsmr:
        environment:
            # Set the user and group IDs, e.g. DUID=1001 (id --user dsmrreader) 
            # and DGID=1001 (id --group dsmrreader) of the "id" commands executed above.
            DUID=1001
            DGID=1001
```

- Find a password generator (e.g. [LastPass Password Generator](https://www.lastpass.com/features/password-generator)) and generate a new `DJANGO_SECRET_KEY` (50 characters, no symbols).
- Configure the generated key in the Compose file as `DJANGO_SECRET_KEY` and replace the dummy `change_me_if_you_host_dsmr_reader_on_the_internet` value.

``` yaml title="compose.yml" hl_lines="6"
# Simplified - Find DJANGO_SECRET_KEY=change_me_if_you_host_dsmr_reader_on_the_internet and change them if dsmrreader has different IDs on your system.
services:
    dsmr:
        environment:
            # Sample generated key, use your own!
            DJANGO_SECRET_KEY=1XfxLJX28ooPoE1SB6BjaZayFDmx2JoDf5bsfIa9MZIP8HOesw
```

### Running
- Try running the containers:

``` shell
# This may take a few minutes, mostly depending on the hardware available.
podman-compose up -d
```

- Check folders created:

``` shell
ls -l
```

- It should now at least have the file `compose.yml` and folders `dsmr_database` and `dsmr_backups`.
- Check logs for any weird stuff:

``` shell
podman-compose logs -f
```

### Testing

If everything looks good, you should be able to access DSMR-reader at: `http://<hostname>:7777`.
E.g. is your hardware is accessible at `123.456.78.90`, go to: `http://123.456.78.90:7777`.