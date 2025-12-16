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

!!! danger "Heads up"

    Originally this project was built to run on SD-cards, but through the years it became clear that SD-cards are not reliable enough for this purpose.
    They will randomly and suddenly get corrupted, so be warned!

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


### OS user
- Add dedicated system user for DSMR-reader to run on:

``` shell
sudo useradd dsmrreader --create-home
sudo usermod -a -G dialout dsmrreader

# Write down the IDs in the output (they are likely the same, e.g. "1001") 
id --user dsmrreader
id --group dsmrreader
```

### DSMR-reader user
- Login as "dsmrreader" user:

``` shell
sudo su - dsmrreader
```

- Download container Compose template file by [manually downloading](https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/v6/provisioning/container/compose.prod.yml) it or running the command below:

[View compose.yml on GitHub](https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/v6/provisioning/container/compose.prod.yml){ .md-button }

``` shell
wget https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/v6/provisioning/container/compose.prod.yml -O compose.yml
```

- Configure Compose file to your needs:

!!! tip

    You can remove all `# TODO for you:` lines from the `compose.yml` file after completing them, or if you don't need them.

``` shell
vi compose.yml
# Or use "nano" instead of "vi" if you prefer another text editor.
```

- If your smart meter is connected via a different port or device than `/dev/ttyUSB0`, change it accordingly.
  Or if you use the API to provide data, you can disable this line by adding a `#` at the start of the line:

``` yaml title="compose.yml" hl_lines="6"
# Simplified
services:
    dsmr:
        devices:
            # TODO for you: Disable (#) or change this if your smart meter is connected via another port or device. Or if you use the API to provide data.
            - /dev/ttyUSB0:/dev/ttyUSB0
```

- Configure the user and group IDs for the `dsmrreader` user created earlier.

``` yaml title="compose.yml" hl_lines="6-7 11-12"
# Simplified
services:
    dsmrdb:
        environment:
            # TODO for you: Check whether the "1001" ID defaults below match the "dsmrreader" user on your system
            DUID=1001
            DGID=1001
    dsmr:
        environment:
            # TODO for you: Check whether the "1001" ID defaults below match the "dsmrreader" user on your system
            DUID=1001
            DGID=1001
```

- Find a password generator (e.g. [LastPass Password Generator](https://www.lastpass.com/features/password-generator)) and generate a new `DJANGO_SECRET_KEY` (50 characters, no symbols).
- Configure the generated key in the Compose file as `DJANGO_SECRET_KEY` and **replace** the dummy `change_me_if_you_host_dsmr_reader_on_the_internet` value.

``` yaml title="compose.yml" hl_lines="7"
# Simplified
services:
    dsmr:
        environment:
            # TODO for you: Change DJANGO_SECRET_KEY below to a truly random value if you host DSMR-reader publicly facing the Internet
            # TODO for you: E.g. by using https://www.lastpass.com/features/password-generator - 50 characters and NO symbols
            - DJANGO_SECRET_KEY=change_me_if_you_host_dsmr_reader_on_the_internet
```

- Configure a password for the admin interface of DSMR-reader by setting `DSMRREADER_ADMIN_PASSWORD`:

``` yaml title="compose.yml" hl_lines="6"
# Simplified
services:
    dsmr:
        environment:
            # TODO for you: Set an admin interface password to your liking - make it a strong one if you host DSMR-reader publicly facing the Internet
            - DSMRREADER_ADMIN_PASSWORD=
```

- The default admin username is `admin`. You can update it by setting `DSMRREADER_ADMIN_USERNAME` if you want to.

!!! tip

    You can remove all `# TODO for you:` lines from the `compose.yml` file after completing them, or if you don't need them.


### Running
- Try running the containers:

``` shell
# This may take a moment, mostly depending on the hardware available.
podman-compose up -d
```

- Check folders created:

``` shell
ls -l
```

- It should now at least have the file `compose.yml` and folders `dsmr_database` and `dsmr_backups`.
- Check logs for any weird stuff:

``` shell
podman-compose ps
podman-compose logs -f
```

### Testing

If everything looks good, you should be able to access DSMR-reader at: `http://<hostname>:7777`.
E.g. is your hardware is accessible at `123.456.78.90`, go to: `http://123.456.78.90:7777`.


### Automatic startup

- To have DSMR-reader start automatically on boot, create a systemd user service.

```shell
mkdir -p ~/.config/systemd/user/
```

```shell
podman generate systemd --new --name dsmr -f
podman generate systemd --new --name dsmrdb -f

mv *.service ~/.config/systemd/user/
```

- Go to root user:

``` shell
logout
# Or press CTRL + D
```

- Enable and start the service:

```shell
sudo loginctl enable-linger dsmrreader
sudo systemctl daemon-reload --user
sudo systemctl --user -M dsmrreader@ enable container-dsmr.service
sudo systemctl --user -M dsmrreader@ enable container-dsmrdb.service
sudo systemctl --user -M dsmrreader@ enable podman-restart.service
```

- Reboot to test automatic startup:

```shell
sudo reboot
```

- After reboot, login as `dsmrreader` user again and check if containers are running:

``` shell
sudo su - dsmrreader

podman-compose ps
```
