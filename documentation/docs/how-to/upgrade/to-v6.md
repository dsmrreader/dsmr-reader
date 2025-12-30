---
hide:
  - toc
---

# Upgrading v5.x to v6.x

!!! warning "Target audience"

    This guide is only required for users upgrading from DSMR-reader v5.x to v6.x that were using the **native** installation method (**non-containerized**).

!!! abstract "Before you start"

    Read the [v6 changelog](../../reference/changelog.md) for all changes. You will likely need to upgrade your database version as well.

----

### Upgrade step 1: Backup your DSMR-reader v5.x data

```shell
sudo su - dsmr

# This may take a few minutes, depending on the size of your database and your hardware.
./manage.py dsmr_backup_create --full

# Note the created backup filename in the output, e.g.:
# Created full backup: /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz
```

- If you are installing DSMR-reader on a new device, make sure to export the created backup file to your new device.
- If the new DSMR-reader installation will be on the same device, you may want to relocate it to the home directory of a sudo user, e.g. `pi`:

```shell
# Or press CTRL+D
logout

sudo mv /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz ~
```

----

### Upgrade step 2: Install DSMR-reader v6.x using the containerized method

!!! abstract ""

    - If you first want to **dry run** the new installation without triggering all background processes, consider enabling ``DSMRREADER_BACKEND_HIBERNATE`` in the Compose file during **installation step 3**.
    - At **installation step 4** of that guide you should import the backup you've created above.

- Follow the [containerized installation guide](../installation/container-setup.md) to set up DSMR-reader v6.x.

----

### Upgrade step 3: Decide what to do with your old DSMR-reader v5.x installation
Depending on if you want to switch to DSMR-reader v6.x permanently, or just want to have it run parallel for a while, you can either:

- Option 1: Remove the old DSMR-reader v5.x installation entirely.
- Option 2: Keep the old DSMR-reader v5.x installation.


#### Option 1: Remove the old DSMR-reader v5.x installation entirely
- To remove DSMR-reader v5 from your system, execute the following commands:

```shell
# Nginx.
sudo rm /etc/nginx/sites-enabled/dsmr-webinterface
sudo service nginx reload
sudo rm -rf /var/www/dsmrreader

# Supervisor.
sudo supervisorctl stop all
sudo rm /etc/supervisor/conf.d/dsmr*.conf
sudo supervisorctl reread
sudo supervisorctl update

# Homedir & user.
sudo rm -rf /home/dsmr/
sudo userdel dsmr
To delete your data (the database) as well:

sudo -u postgres dropdb dsmrreader
```

- Optionally, you can remove these packages:

```shell
sudo apt-get remove postgresql postgresql-server-dev-all python3-psycopg2 nginx supervisor git python3-pip python3-virtualenv virtualenvwrapper
```

#### Option 2: Keep the old DSMR-reader v5.x installation
- Just stop the processes and prevent them from automatically starting:

```shell
sudo supervisorctl stop all
sudo mv /etc/supervisor/conf.d/dsmr_backend.conf /etc/supervisor/conf.d/dsmr_backend.conf.DISABLED
sudo mv /etc/supervisor/conf.d/dsmr_datalogger.conf /etc/supervisor/conf.d/dsmr_datalogger.conf.DISABLED
sudo mv /etc/supervisor/conf.d/dsmr_webinterface.conf /etc/supervisor/conf.d/dsmr_webinterface.conf.DISABLED
sudo supervisorctl reread
sudo supervisorctl update
```

!!! abstract ""

    If you want to revert it later:
    
    ```shell
    sudo mv /etc/supervisor/conf.d/dsmr_backend.conf.DISABLED /etc/supervisor/conf.d/dsmr_backend.conf
    sudo mv /etc/supervisor/conf.d/dsmr_datalogger.conf.DISABLED /etc/supervisor/conf.d/dsmr_datalogger.conf
    sudo mv /etc/supervisor/conf.d/dsmr_webinterface.conf.DISABLED /etc/supervisor/conf.d/dsmr_webinterface.conf
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start all
    ```

---

### Visual overview of the differences between DSMR-reader v5.x and v6.x

You are done! If you want to know more about the differences between the native setup of DSMR-reader v5.x and the containerized setup of DSMR-reader v6.x, see the diagrams below. Or just skip it entirely.


## Visual: Native setup for DSMR-reader v5.x
*All dependencies reside on the OS and required end-user to manually install/upgrade.*

``` mermaid
sequenceDiagram
    participant OS as Server (host)
    Note over OS: E.g. RaspberryPi OS
    
    create participant DSMRReader@{ "type" : "entity" }

    rect rgb(200, 150, 255)
    OS-->>DSMRReader: Hosts Supervisor to run
    Note over OS: Python
    Note over OS: Packages
    Note over DSMRReader: DSMR-reader code
    end

    create participant Database@{ "type" : "database" }
    DSMRReader->>Database: Communicates with
    
    rect rgb(191, 223, 255)
    OS-->>Database: Hosts
    Note over Database: PostgreSQL
    end
```


## Visual: New setup for DSMR-reader v6.x
*All dependencies are moved into containers and do no longer require end-user installation or upgrades.*

``` mermaid
sequenceDiagram
    participant OS as Server (host)
    Note over OS: E.g. RaspberryPi OS
    rect rgb(200, 150, 255)
    create participant REGISTRY as Docker/Podman
    OS->>REGISTRY: Runs
    end
        
    create participant DSMRReader@{ "type" : "entity" }

    rect rgb(200, 150, 255)
    REGISTRY-->>DSMRReader: Hosts DSMRReader Docker container
    Note over DSMRReader: Python
    Note over DSMRReader: Packages
    Note over DSMRReader: DSMR-reader code
    end
     
    rect rgb(200, 150, 255)
    OS<<-->>DSMRReader: Mounted volume
    Note over OS: /home/dsmrreader/dsmr_backups
    Note over DSMRReader: /app/backups
    end
    
    create participant Database@{ "type" : "database" }
    DSMRReader->>Database: Communicates with
    
    rect rgb(191, 223, 255)
    REGISTRY-->>Database: Hosts PostgreSQL container
    Note over Database: E.g. PostgreSQL
    end
    
    rect rgb(200, 150, 255)
    OS<<-->>Database: Mounted volume
    Note over OS: /home/dsmrreader/dsmr_database
    Note over Database: /var/lib/postgresql
    end
```
