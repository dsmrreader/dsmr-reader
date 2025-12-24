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
### Installation step 1: OS packages
- Install system packages:

``` shell
sudo apt-get update
sudo apt-get install podman podman-compose podman-docker crun
```

``` shell
podman info --debug
```

!!! abstract "Optional"

    - Install ``cu`` package to manually read from the P1 port:

    ``` shell
    # Skip this if you have already read your meter's P1 telegram port (ever) before or are an existing DSMR-reader user.
    sudo apt-get install cu
    ```

----

### Installation step 2: OS user

!!! abstract ""

    There are multiple ways to run containers. This guide uses a dedicated system user (`dsmrreader`) for DSMR-reader to make it does **not** run as `root` user. 
    This is similar to the legacy setup with the legacy system user (`dsmr`) in the past. Feel free to run it any other (unsupported) way to your liking.

    The username (`dsmrreader`) purposely differs from legacy to avoid confusion with the old setup. And to allow legacy users to easily migrate (or roll back).

- Add dedicated `dsmrreader` system user for DSMR-reader (and its database) to run on:

``` shell
sudo useradd dsmrreader --create-home
sudo usermod -a -G dialout dsmrreader
```

```shell
# Write down the IDs in the output (they are likely the same, e.g. "1001")
id --user dsmrreader
id --group dsmrreader
```

- Enable lingering and a systemd service to allow autostart of containers on (re)boot:

```shell
sudo loginctl enable-linger dsmrreader
sudo podman-compose systemd -a create-unit
```

----

### Installation step 3: Containers for DSMR-reader and database
Now we'll configure the DSMR-reader system user we just created.

- Login as "dsmrreader" user:

``` shell
sudo su - dsmrreader
```

!!! abstract "Optional: Your first reading"

    You may skip this section as it's **not** required for the application to install. 
    However, if you have never read your meter's P1 telegram port before, it's recommended to perform an initial reading to make sure everything works as expected.

    Also, this will only work if your smart meter is connected via a serial-to-USB adapter or similar, and not via network or other API.

    - Test with ``cu`` for **DSMR 4/5** first (your meter will likely use this):
    
    ``` shell
    cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q
    ```
    
    - Or test with ``cu`` for **DSMR 2.2**:
    
    ``` shell
    cu -l /dev/ttyUSB0 -s 9600 --parity=none
    ```
    
    - You now should see something similar to ``Connected.`` and a wall of text and numbers *within 10 seconds*. 
    - Nothing? Try different BAUD rate, as mentioned above. Still nothing? Consider [asking for help](../../troubleshooting/help.md).
    
    - To exit ``cu`` if it worked, type "``q.``", hit `Enter` and wait for a few seconds. It should exit shortly with the message ``Disconnected.``

Continuing the setup:

- Create a "Compose" YAML file named `compose.yml` in the home directory. This will tell Podman *which* containers to run and *how* to run them (with which settings).

- Download container Compose template file by manually downloading it below or running the command under the button:

[View compose.yml on GitHub](https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/v6/provisioning/container/compose.prod.yml){ .md-button }

``` shell
wget https://raw.githubusercontent.com/dsmrreader/dsmr-reader/refs/heads/v6/provisioning/container/compose.prod.yml -O compose.yml
```

- Configure Compose file to your needs:

!!! tip

    You can remove all `# TODO for you:` lines from the `compose.yml` file after completing them. Or if you don't need them at all.

``` shell
vi compose.yml
# Or use "nano" instead of "vi" if you prefer another text editor.
```

- Configure the user and group IDs for the `dsmrreader` user created earlier.

``` yaml title="compose.yml" hl_lines="6-7 11-12"
# Simplified
services:
    dsmrdb:
        environment:
            ### TODO for you: Check whether the "1001" ID defaults below match the "dsmrreader" user on your system
            DUID=1001
            DGID=1001
    dsmr:
        environment:
            ### TODO for you: Check whether the "1001" ID defaults below match the "dsmrreader" user on your system
            DUID=1001
            DGID=1001
```

- If your smart meter is connected via a different port or device than `/dev/ttyUSB0`, change it accordingly.
  Or if you use the API to provide data, you can disable this line by adding a `#` at the start of the line:

``` yaml title="compose.yml" hl_lines="5-6"
# Simplified
services:
    dsmr:
        ### TODO for you: Enable these two lines below when you want to connect a physical smart meter to the container using USB.
        #devices:
          # - /dev/ttyUSB0:/dev/ttyUSB0
```

- Find a password generator (e.g. [LastPass Password Generator](https://www.lastpass.com/features/password-generator)) and generate a new `DJANGO_SECRET_KEY` (50 characters, no symbols).
- Configure the generated key in the Compose file as `DJANGO_SECRET_KEY` and **replace** the dummy `change_me_if_you_host_dsmr_reader_on_the_internet` value.

``` yaml title="compose.yml" hl_lines="7"
# Simplified
services:
    dsmr:
        environment:
            ### TODO for you: Change "change_me_if_you_host_dsmr_reader_on_the_internet" below to a truly random value if you host DSMR-reader publicly facing the Internet
            ### TODO for you: E.g. by using https://www.lastpass.com/features/password-generator - 50 characters and NO symbols
            - DJANGO_SECRET_KEY=change_me_if_you_host_dsmr_reader_on_the_internet
```

- Configure a password for the admin interface of DSMR-reader by setting `DSMRREADER_ADMIN_PASSWORD`:

``` yaml title="compose.yml" hl_lines="6"
# Simplified
services:
    dsmr:
        environment:
            ### TODO for you: Set an admin interface password to your liking - make it a strong one if you host DSMR-reader publicly facing the Internet
            - DSMRREADER_ADMIN_PASSWORD=
```

- The default admin username is `admin`. You can update it by setting `DSMRREADER_ADMIN_USERNAME` if you want to.

- If you are installing a new instance of DSMR-reader and you first want to dry-run it after database import, enable `DSMRREADER_ADMIN_PASSWORD`:

``` yaml title="compose.yml" hl_lines="6"
# Simplified
services:
    dsmr:
        environment:
            ### TODO for you: If you run DSMR-reader with an imported backup and first want to try it WITHOUT running background processes, enable this. Drop it otherwise.
            - DSMRREADER_BACKEND_HIBERNATE=True
```

- Omit the option if you don't need it.
- Continue to step 4 below.

!!! tip "Reminder"

    You can remove all `### TODO for you:` lines from the `compose.yml` file after completing them, or if you don't need them.

----

### Installation step 4: Optional import and first run

!!! abstract ""

    Note that we are using `podman-compose`, everywhere, and **not** `podman compose` (note the dash/whitespace difference). Using the latter will result in different behavior!

- Try running the DB container first:

``` shell
# This may take a few moments, mostly depending on the hardware and Internet connection available.
# Please wait patiently.
podman-compose up -d dsmrdb
```

- If there are any errors, try:

``` shell
podman-compose logs -f dsmrdb
# Press CTRL + C to stop following the logs
```

- Check folders created:

``` shell
ls -l
```

- It should now have created the `dsmr_database` folder.

!!! warning "Important if you have a backup to restore"

    The database should now be created and initialized. It's important to **not** start DSMR-reader before importing your backup.
    If you have no backup to restore, just skip this warning and continue further below.

    Make sure your backup is moved into the `dsmr_database/import/` folder. E.g.

    ``` shell
    logout
    sudo mv /home/pi/dsmrreader-postgresql-backup-Wednesday.sql.gz /home/dsmrreader/dsmr_database/import/
    ```

    Go back to the `dsmrreader` user and into the DB container:

    ``` shell
    sudo su - dsmrreader
    podman-compose exec dsmrdb sh
    ```

    - For `.sql` backups, run:

    ``` shell
    psql -U dsmrreader_user -d dsmrreader -f /run/database-import/dsmrreader-postgresql-backup-Wednesday.sql.gz
    ```

    - For `.sql.gz` backups, run:
    ``` shell
    zcat /run/database-import/dsmrreader-postgresql-backup-Wednesday.sql.gz | psql -U dsmrreader_user -d dsmrreader
    ```

    Exit with `CTRL + D`.

!!! abstract ""

    At this point we can start DSMR-reader. If you started it before importing your backup, the database would be initialized by DSMR-reader and you cannot import your backup.

- Start DSMR-reader container:

``` shell
podman-compose down dsmrdb

# This may take a few moments, mostly depending on the hardware and Internet connection available.
# Please wait patiently.
podman-compose up -d
```

- If there are any errors, try:

``` shell
podman-compose logs -f dsmr
# Press CTRL + C to stop following the logs
```

- Run this command to see the status of the containers:

``` shell
podman-compose ps
```

- Now the folders `dsmr_database` and `dsmr_backups` should both exist:

``` shell
ls -l
```

----

### Installation step 5: Testing DSMR-reader

If everything looks good, you should be able to access DSMR-reader at: `http://<hostname>:7777`

E.g. is your hardware is accessible at `123.456.78.90`, go to: http://123.456.78.90:7777

- Click around a bit to see if things work and whether you also can log in on the Configuration menu item.

----

### Installation step 6: Configure automatic startup
Now we will make sure DSMR-reader starts automatically on (re)boot. E.g. after system updates or a power outage.

- Stop the containers first:

``` shell
# Still as "dsmrreader" user
podman-compose down
```

- To have DSMR-reader start automatically on boot, create a systemd user service.

```shell
podman-compose systemd -a register
```

- Go back to root/sudo user (e.g. `pi` user) with:

``` shell
logout
# Or press CTRL + D
```

- Enable the service and start it:

```shell
sudo systemctl enable podman-compose@dsmrreader --user -M dsmrreader@
sudo systemctl start podman-compose@dsmrreader --user -M dsmrreader@
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

- Test the web interface again (see step 5 above).
- Everything should be working now!
