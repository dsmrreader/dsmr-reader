# Upgrading v4.x to v5.x

!!! danger "Heads up"

    This is a guide for upgrading a very old version of DSMR-reader. It's only preserved for historical reference and unlikely to be needed by anyone.

DSMR-reader `v5.x` is backwards incompatible with `4.x`. You will have to manually upgrade to make sure it will run properly.

## Contents
(see headings below)

### List of changes

> **Danger:** See the changelog for `v5.x releases` and higher. Check them before updating!
>
> - Do not upgrade if you run **PostgreSQL 9.x or below**. Upgrade PostgreSQL first.
> - Do not upgrade if you run **InfluxDB 1.x**. Upgrade to InfluxDB 2.x first.
> - Do not upgrade if you run **MySQL 5.6 or below**. Upgrade MySQL first.
> - This upgrade will require you to run (or upgrade to) **Python 3.7 or higher**.

---

## Docker

> **Attention:** Docker users, see the changelog for env var changes!
>
> If you're using Docker, you can probably just install the `v5.x` version of the Docker container without having to perform any of the steps below.

---

## 1. Update to the latest `v4.x` version

Update to `v4.20` to ensure you have the latest `v4.x` version.

## 2. Relocate to github.com/dsmrreader/

Over a year ago the DSMR-reader project was moved to `https://github.com/dsmrreader`.

Execute the following:

```shell
sudo su - dsmr
git remote -v
```

It should point to:

```
origin	https://github.com/dsmrreader/dsmr-reader.git (fetch)
origin	https://github.com/dsmrreader/dsmr-reader.git (push)
```

**If not**, update it and check again:

```shell
git remote set-url origin https://github.com/dsmrreader/dsmr-reader.git
git remote -v
```

Execute the following:

```shell
logout
```

## 3. Python version check

DSMR-reader `5.x` requires `Python 3.7` or higher.

Execute the following:

```shell
sudo su - dsmr
python3 --version
```

If you're already running `Python 3.7` (or higher), you can ignore the next section.

Execute the following:

```shell
logout
```

## 4. Python version upgrade (when running `Python 3.6` or lower)

> **Warning:** Only execute this section if you're running DSMR-reader with `Python 3.6` or lower!

There are several guides, depending on your OS. We assume Raspbian OS here.

> Tip: You may consider upgrading to a higher Python version, e.g. `Python 3.11`, if possible for your OS.

Execute the following:

```shell
# Credits to Jeroen Peters @ issue #624
sudo apt-get install python3-dev libffi-dev libssl-dev -y
wget https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tar.xz
tar xJf Python-3.11.2.tar.xz
cd Python-3.11.2
./configure --enable-optimizations --with-lto
make
sudo make install
sudo pip3 install --upgrade pip
```

> Attention: Try running `python3 --version` to see if things worked out. If you're getting any errors, do not continue with the upgrade.

---

The next thing you'll absolutely need to do, is create a fresh database backup and store it somewhere safe.

Execute the following:

```shell
sudo su - dsmr
./manage.py dsmr_backup_create --full
```

If things went well, you should see a message like:

```
Created full backup: /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz
```

Execute the following (your file name may differ):

```shell
ls -lh /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz
```

Make sure the file is of some (reasonable) size.

Execute the following (your file name may differ):

```shell
zcat /home/dsmr/dsmr-reader/backups/manually/dsmrreader-postgresql-backup-Wednesday.sql.gz | tail
```

Make sure the output ends with:

```
--
-- PostgreSQL database dump complete
--
```

Execute the following:

```shell
logout
```

## 5. Upgrade to DSMR-reader v5

> **Danger — Reminder:** See the changelog for `v5.x releases` and higher. Check them before updating!
>
> - Do not upgrade if you run **PostgreSQL 9.x or below**. Upgrade PostgreSQL first.
> - Do not upgrade if you run **InfluxDB 1.x**. Upgrade to InfluxDB 2.x first.
> - Do not upgrade if you run **MySQL 5.6 or below**. Upgrade MySQL first.

---

Install Python venv:

```shell
sudo apt-get install python3-venv
```

Install `libopenjp2-7-dev` as well, to prevent a possible error later:

```shell
# "ImportError: libopenjp2.so.7: cannot open shared object file: No such file or directory"
sudo apt-get install libopenjp2-7-dev
```

Stop DSMR-reader:

```shell
sudo supervisorctl stop all
```

Disable `v4.x` virtualenv:

```shell
sudo su - dsmr
deactivate
mv ~/.virtualenvs/ ~/.old-v4-virtualenvs
```

Create new `v5.x` virtualenv:

```shell
python3 -m venv ~/dsmr-reader/.venv/
```

Remove the following line from `/home/dsmr/.bashrc` (edit the file):

```text
# remove this line if present:
source ~/.virtualenvs/dsmrreader/bin/activate
```

Add this line instead:

```text
source ~/dsmr-reader/.venv/bin/activate
```

Update DSMR-reader codebase:

```shell
git fetch
git checkout -b v5 origin/v5

# Make sure you're at v5 now:
git branch

git pull
```

Install dependencies:

```shell
source ~/dsmr-reader/.venv/bin/activate

pip3 install pip --upgrade
pip3 install -r ~/dsmr-reader/dsmrreader/provisioning/requirements/base.txt
```

> Tip: If installation fails with Pillow/jpeg header errors, try installing `libjpeg-dev`:
>
> ```shell
> logout
> sudo apt-get install libjpeg-dev
>
> sudo su - dsmr
> pip3 install -r ~/dsmr-reader/dsmrreader/provisioning/requirements/base.txt
> ```

Rename any legacy setting names in `.env` you find (edit `~/dsmr-reader/.env`):

If you find any variables on the left, rename them to the right:

- SECRET_KEY ➡️ DJANGO_SECRET_KEY
- DB_ENGINE ➡️ DJANGO_DATABASE_ENGINE
- DB_NAME ➡️ DJANGO_DATABASE_NAME
- DB_USER ➡️ DJANGO_DATABASE_USER
- DB_PASS ➡️ DJANGO_DATABASE_PASSWORD
- DB_HOST ➡️ DJANGO_DATABASE_HOST
- DB_PORT ➡️ DJANGO_DATABASE_PORT
- CONN_MAX_AGE ➡️ DJANGO_DATABASE_CONN_MAX_AGE
- TZ ➡️ DJANGO_TIME_ZONE
- DSMR_USER ➡️ DSMRREADER_ADMIN_USER
- DSMR_PASSWORD ➡️ DSMRREADER_ADMIN_PASSWORD

Check DSMR-reader:

```shell
./manage.py check
```

It should output something similar to: "System check identified no issues (0 silenced)."

> Tip: If it fails with:
>
> ```
> ImportError: libopenjp2.so.7: cannot open shared object file: No such file or directory
> ```
>
> Make sure you've installed `libopenjp2-7-dev` and re-run:
>
> ```shell
> logout
> sudo apt-get install libopenjp2-7-dev
>
> sudo su - dsmr
> ./manage.py check
> ```

Execute:

```shell
./manage.py migrate
```

Execute:

```shell
logout
```

> Attention: This may revert any customizations you've done yourself, such as HTTP Basic Auth configuration.

Update Nginx config:

```shell
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
sudo ln -s -f /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/
```

Reload Nginx:

```shell
sudo nginx -t
sudo systemctl reload nginx.service
```

Update Supervisor configs:

```shell
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/
```

Reload Supervisor configs:

```shell
sudo supervisorctl reread
sudo supervisorctl update
```

Start DSMR-reader:

```shell
sudo supervisorctl start all
```

## 6. Deploy

Finally, execute the deploy script:

```shell
sudo su - dsmr
./deploy.sh
```

Great. You should now be on `v5.x`!

## 7. Situational: Reconfigure InfluxDB

If you used DSMR-reader export to InfluxDB previously, you must reconfigure it accordingly. It has been disabled automatically as well.

Hint: Where the previous version utilized usernames, passwords and databases, it now connects using organizations, API tokens and buckets.

## 8. Situational: Reconfigure Dropbox

If you used DSMR-reader's Dropbox sync for backups, you must reconfigure it accordingly.

## 9. Situational: Remote datalogger env vars

The following remote datalogger script settings were renamed; change them if you use/update the remote datalogger script (e.g. in Docker):

- DATALOGGER_INPUT_METHOD ➡️ DSMRREADER_REMOTE_DATALOGGER_INPUT_METHOD
- DATALOGGER_SERIAL_PORT ➡️ DSMRREADER_REMOTE_DATALOGGER_SERIAL_PORT
- DATALOGGER_SERIAL_BAUDRATE ➡️ DSMRREADER_REMOTE_DATALOGGER_SERIAL_BAUDRATE
- DATALOGGER_API_HOSTS ➡️ DSMRREADER_REMOTE_DATALOGGER_API_HOSTS
- DATALOGGER_API_KEYS ➡️ DSMRREADER_REMOTE_DATALOGGER_API_KEYS
- DATALOGGER_TIMEOUT ➡️ DSMRREADER_REMOTE_DATALOGGER_TIMEOUT
- DATALOGGER_SLEEP ➡️ DSMRREADER_REMOTE_DATALOGGER_SLEEP
- DATALOGGER_MIN_SLEEP_FOR_RECONNECT ➡️ DSMRREADER_REMOTE_DATALOGGER_MIN_SLEEP_FOR_RECONNECT
