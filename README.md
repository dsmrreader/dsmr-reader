[![Build Status](https://travis-ci.org/dennissiemensma/dsmr-reader.svg?branch=master)](https://travis-ci.org/dennissiemensma/dsmr-reader)
[![Coverage](https://codecov.io/github/dennissiemensma/dsmr-reader/coverage.svg?branch=master)](https://codecov.io/github/dennissiemensma/dsmr-reader?branch=master)


# Table of content #
* Intro
    * Usage
    * Dependencies & requirements
* Installation guide
    * Application Installation
    * Data preservation & backups
    * Application updates (bug fixes & new features)
    * (Optional) Operating System Installation
* Contribution & feedback
    * P1 Telegram snaphot
    * Feedback
    * Sentry
* Licence
* Credits

# Intro #
Installation instructions are based on the Raspbian distro for RaspberryPi, but it should generally work on every Debian based system, as long as the dependencies & requirements are met.

## Usage ##
There are plenty of 'scripts' available online for performing DSMR readings. This project however is a full stack solution. This allows a decent implementation of most features, but requires a certain 'skill' as you will need to install several dependencies. 

I advise to only use this tool when you have basic Linux knowledge or have any interest in the components used. I might create an installer script later, but I'll focus on the build of features first.

## Dependencies & requirements ##
* RaspberryPi v2+ *(recommended)*.
* Raspbian *(or Debian based distro)*.
* Python 3.3 or 3.4 *(Included in the latest Raspbian named "Jessie")*.
* Smart Meter with support for at least DSMR 4.0/4.2 *(tested with Landis + Gyr E350 DSMR4, Kaifa)*.
* Minimal 100 MB of disk space on RaspberryPi *(for application installation & virtualenv)*. More disk space is required for storing all reader data captured *(optional)*. I generally advise to use a 8+ GB SD card.
* Smart meter P1 data cable *(can be purchased online and they cost around 20 Euro's)*.
* Basic Linux knowledge for deployment, debugging and troubleshooting. 

# Installation guide #
The installation guide may take about half an hour max, but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.

You should already have an OS running on your RaspberryPi. If not, somewhere near the end of the guide is a brief hint for getting things started ("(Optional) Operating System Installation"). 
Just continue directly to the "Application Installation" chapter when you already have your RaspberryPi up and running.


## Application Installation ##

### Database backend ###
The application stores by default all readings taken from the serial cable. Depending on your needs, you can choose for either (Option A.) **PostgreSQL** (Option B.) **MySQL/MariaDB**. If you have no idea what to choose, **I generally advise to pick PostgreSQL**, as it has better support for timezone handling (needed for DST transitions). 



#### (Option A.) PostgreSQL ###

Install PostgreSQL. **postgresql-server-dev-all** is required for the virtualenv installation later in this guide.

`sudo apt-get install -y postgresql postgresql-server-dev-all`

Postgres does not start due to locales? Try: `dpkg-reconfigure locales`

No luck? Try editing `/etc/environment`, add `LC\_ALL="en_US.utf-8"` and `reboot`

Ignore any *'could not change directory to "/root": Permission denied'* errors for the following three commands.

Create user:

`sudo sudo -u postgres createuser -DSR dsmrreader`

Create database, owned by the user we just created:

`sudo sudo -u postgres createdb -O dsmrreader dsmrreader`

Set password for user:

`sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"`


#### (Option B.) MySQL/MariaDB ###
Install MariaDB. You can also choose to install the closed source MySQL, as they should be interchangeable anyway. **libmysqlclient-dev** is required for the virtualenv installation later in this guide..

`sudo apt-get install -y mariadb-server-10.0 libmysqlclient-dev` 

Create database:

`sudo mysqladmin create dsmrreader`

Create user:

`echo "CREATE USER 'dsmrreader'@'localhost' IDENTIFIED BY 'dsmrreader';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v`

Set privileges for user:

`echo "GRANT ALL ON dsmrreader.* TO 'dsmrreader'@'localhost';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v`

Flush privileges to activate them:

`mysqladmin reload`


### Dependencies ###
Misc utils, required for webserver, application server and cloning the application code from the repository.

`sudo apt-get install -y nginx supervisor git python3 python3-pip python3-virtualenv virtualenvwrapper`

Install `cu`. The CU program allows easy testing for your DSMR serial connection. It's basic but very effective to test whether your serial cable setup works properly.

`sudo apt-get install -y cu`


### Application user ###
The application runs as `dsmr` user by default. This way we do not have to run the application as `root`, which is a bad practice anyway. 

Create user with homedir. The application code and virtualenv resides in this directory as well:

`sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash`

Our user also requires dialout permissions. So allow the user to perform a dialout by adding it to the group.

`sudo usermod -a -G dialout dsmr`


### Webserver (Nginx), part 1 ###
We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy application requests to the backend, Gunicorn controlled by Supervisor, which we will configure later on.

Django will copy all static files to a separate directory, used by Nginx to serve statics. 

`sudo mkdir -p /var/www/dsmrreader/static`

`sudo chown -R dsmr:dsmr /var/www/dsmrreader/`

The reason for splitting the webserver chapter in two steps, is because the application requires the directory created above to exist. And Nginx requires the application to exist (cloned) before running (and to copy its virtual hosts file), resulting in an dependency loop... :]


### Your first reading ###

Now login as the user we just created, to perform our very first reading!

`sudo su - dsmr`

Test with **cu** (BAUD rate settings for *DSMR v4* is **115200**, for older verions it should be **9600**). 

`cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q`

You now should see something similar to `Connected.` and a wall of text and numbers within 10 seconds. Nothing? Try different BAUD rate, as mentioned above. You might also check out a useful blog, such as [this one (Dutch)](http://gejanssen.com/howto/Slimme-meter-uitlezen/).

To exit **cu**, input `q.`, hit Enter and wait for a few seconds. It should exit with the message `Disconnected`.


### Application code clone ###
Now is the time to clone the code from the repository and check it out on your device. Make sure you are still logged in as our **dsmr** user (if not so, then enter `sudo su - dsmr` again):

`git clone https://github.com/dennissiemensma/dsmr-reader.git`


### Virtualenv ###

The dependencies our application uses are stored in a separate environment, also called **VirtualEnv**. Although it's just a folder inside our user's homedir, it's very effective as it allows us to keep dependencies isolated or to run different versions of the same package on the same machine. More info can be found [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

(Make sure you are still `dsmr` user)
`sudo su - dsmr`

Create folder for the virtualenvs of this user:

`mkdir ~/.virtualenvs`

Create a new virtualenv, we usually use the same name for it as the application or project. Note that it's important to specify python3 as the default interpreter: 

`virtualenv ~/.virtualenvs/dsmrreader --no-site-packages --python python3`

Now 'activate' the environment. It effectively directs all aliases for software installed in the virtualenv to the binaries inside the virtualenv. I.e. the Python binary inside `/usr/bin/python` won't be used when the virtualenv is activated, but `/home/dsmr/.virtualenvs/dsmrreader/bin/python` will be instead.

Activate virtualenv & cd to project:

```
source ~/.virtualenvs/dsmrreader/bin/activate

cd ~/dsmr-reader
```

You might want to put the `source ~/.virtualenvs/dsmrreader/bin/activate` command above in the user's `~/.bashrc` (logout and login to test). I also advice to put the `cd ~/dsmr-reader` in there as well, which will cd you directly inside the project folder on login.


### Application configuration & setup ###
Earlier in this guide you had to choose for either **(A.) PostgreSQL** or **(B.) MySQL/MariaDB**. Our applications needs to know what backend to talk to. Therefor I created two default configuration files you can copy, one for each backend. 
The application will also need the appropiate database client, which is not installed by default. For this I also created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework. The `base.txt` contains requirements which the application needs anyway, no matter the backend you've choosen. 

**Note:** Installation might take a while, depending on your Internet connection, RaspberryPi version and resources (generally CPU) available. Nothing to worry about. :]

**A.** Did you choose PostgreSQL? Then execute these two lines:

```
cp dsmrreader/provisioning/django/postgresql.py dsmrreader/settings.py

pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/postgresql.txt
```

**B.** Or did you choose MySQL/MariaDB? Execute these two commands:

```
cp dsmrreader/provisioning/django/mysql.py dsmrreader/settings.py

pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/mysql.txt
```


Did every go as planned? When either of the database clients refuses to install due to missing files/configs, make sure you installed `libmysqlclient-dev` (**MySQL**) or `postgresql-server-dev-all` (**PostgreSQL**) earlier in the process, when you installed the database server itself.

Now it's time to bootstrap the application and check whether all settings are good and requirements are met. Execute this to init the database:
 
`./manage.py migrate`

Prepare static files for webinterface. This will copy all static files to the directory we created for Nginx earlier in the process. It allows us to have Nginx serve static files outside our project/code root:

`./manage.py collectstatic --noinput`

Create an application superuser. Django will prompt you for a password. Alter username and email when you prefer other credentials, but email is not (yet) used in the application anyway. Besides, you have shell access so you may generate another user at any time (in case you lock yourself out of the application). The credentials generated can be used to access the administration panel inside the application, which requires authentication.

`./manage.py createsuperuser --username admin --email root@localhost`

**OPTIONAL**: The application will run without your energy prices, but if you want some sensible defaults (actually my own energy prices for a brief period), you may run the command below to import them (fixtures). Note that altering prices later won't affect your reading data, because prices are calculated retroactive anyway. 

`./manage.py loaddata dsmr_stats/fixtures/dsmr_stats/EnergySupplierPrice.json` 

### Webserver (Nginx), part 2 ###
Now to back to root/sudo-user to config webserver. Remove the default vhost (if you didn't use it yourself anyway!).

`sudo rm /etc/nginx/sites-enabled/default` (optional)

Copy application vhost, it will listen to **any** hostname (wildcard), but you may change that if you feel like you need to. It won't affect the application anyway.

`sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-enabled/`

Let Nginx verify vhost syntax and reload Nginx when configtest passes.

```
sudo service nginx configtest

sudo service nginx reload
```


### Supervisor ###
Now we configure [Supervisor](http://supervisord.org/), which is used to run our application and also all background jobs used. It's also configured to bring the entire applciation up again after a shutdown or reboot. Each job has it's own configuration file, so make sure to copy them all:  

`sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_*.conf /etc/supervisor/conf.d/`

Login to supervisor management console:

`sudo supervisorctl`

Enter these commands (after the >). It will ask Supervisor to recheck its config directory and use/reload the files.

> supervisor> `reread`

> supervisor> `update`

Three processed should be started or running. Make sure they don't end up in **ERROR** state, so refresh with 'status' a few times. `dsmr_backend` and `dsmr_datalogger` will restart every time. This is intended behaviour. `dsmr_webinterface` however should keep running.  
> supervisor> `status`

Example of everything running well:

    dsmr_backend                     STARTING
    dsmr_datalogger                  RUNNING
    dsmr_webinterface                RUNNING
 
Want to check whether data logger works? Just tail log in supervisor with:

> supervisor> `tail -f dsmr_datalogger`

You should see similar output as the CU-command used earlier on the command line.
Want to quit supervisor? `CTRL + C` to stop tail and `CTRL + D` once to exit supervisor command line.

### Opening the application ###
Now it's time to view the application in your browser to check whether the GUI works as well. Just enter the ip address or hostname of your RaspberryPi in your browser, for example . Don't know what address your device has? Just type `ifconfig | grep addr` and it should display an ip address, for example:

    eth0      Link encap:Ethernet  HWaddr b8:27:eb:f4:24:de  
              inet addr:192.168.178.150  Bcast:192.168.178.255  Mask:255.255.255.0
              inet addr:127.0.0.1  Mask:255.0.0.0

In this example the ip address is `192.168.178.150`.

Everything OK? Congratulations, this was the hardest part and now the fun begins by monitoring your electricity (and possible gas) consumption! :]

### Reboot test ###

You might want to `reboot` and check whether everything comes up automatically again with `sudo supervisorctl status`. This will make sure your data logger 'survives' any power surges.

### Public webinterface warning ###
**NOTE**: If you expose your application to the outside world or a public network, you might want to take additional steps: 

* Please make sure to ALTER the `SECRET_KEY` setting in your `settings.py`. Don't forget to run `reload.sh` in the project root, which will force the application to gracefully reload itself and apply the new settings instantly.

* Install a firewall, such as `ufw` [UncomplicatedFirewall](https://wiki.ubuntu.com/UncomplicatedFirewall) and restrict traffic to port 22 (only for yourself) and port 80.

* You should **also** have Nginx restrict application access when exposing it to the Internet. Simply generate an htpasswd string using one of the [many generators found online](http://www.htaccesstools.com/htpasswd-generator/). It's safe to use them, just make sure to **NEVER** enter personal credentials there **used for other applications** or personal accounts.
Paste the htpasswd string in `/etc/nginx/htpasswd`, open the site's vhost in `/etc/nginx/sites-enabled/dsmr-webinterface` and **uncomment** the following lines:

```
##    auth_basic "Restricted application";
##    auth_basic_user_file /etc/nginx/htpasswd;
``` 

Now make sure you didn't insert any typo's by running `sudo service nginx configtest` and then reload with `sudo service nginx reload`. You should be prompted for login credentials the next time your browser accesses the application. For more information about this topic, see [the Nginx docs](https://www.nginx.com/resources/admin-guide/restricting-access/).


## Data preservation & backups ##
You **should (or must)** make sure to periodically BACKUP your data! It's one of the most common mistakes to skip or ignore this. Actually, it happened to myself quite recently as I somehow managed to corrupt my SD storage card, losing all my data on it. It luckily happened only a month after running my own readings, but imagine all the data you lose when it contained readings for several years.
The application will by default create a backup every night. However, as the data is still stored locally on your vulnerable SD card, you should export it off your RaspberryPi. There is an builtin option to have backups synced to your Dropbox, without exposing your Dropbox account and your private files in it. Please either use this service or manage offloading backups on your own.

You may also decide to run backups outside the application. There are example backup scripts available in `dsmrreader/provisioning/postgresql/psql-backup.sh` for PostgreSQL, which I dump to a separately mounted USB stick on my RaspberryPi. For MySQL/MariaDB you can use `dsmrreader/provisioning/mysql/mysql-backup.sh`. Make sure to schedule the backup script as cronjob and also verify that it actually works. ;-)

Also, check your free disk space once in a while. I will implement automatic cleanup settings (#12, #13) later, allowing you to choose your own retention (for all the source readings).


## Application updates (bug fixes & new features) ##
The current setup is based on the 'latest' version of the application, called the `master` branch. I will add versions/releases later, possibly by using PIP. For now you can always update your application to the latest version by executing `deploy.sh`, located in the root of the project. Make sure to execute it while logged in as the `dsmr` user. It will make sure to check, fetch and apply any changes released.

Summary of deployment script:
* GIT pull (codebase update)
* PIP update requirements
* Apply any database migrations
* Sync static files to Nginx folder
* Reload Gunicorn application server
* Clear any cache


## (Optional) Operating System Installation ##
Only required when you didn't have your RaspberryPi installed at all.

### Raspbian ###
Either use the headless version of Raspbian, [netinstall](https://github.com/debian-pi/raspbian-ua-netinst), or the [full Raspbian image](https://www.raspbian.org/RaspbianImages), with graphics stack. You don't need the latter when you intend to only use your decive for DSMR readings.

### Init ###
Power on RaspberryPi and connect using SSH:

`ssh pi@IP-address` (full image)

or

`ssh root@IP-address` (headless)


#### IPv6 ####
Disable IPv6 if you get timeouts or other weird networking stuff related to IPv6.

```
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf

sysctl -p /etc/sysctl.conf
```

#### Sudo ####
This will allow you to use sudo: `apt-get install -y sudo`  *(headless only)*

#### Text editor ####
My favorite is VIM, but just choose your own: `sudo apt-get install -y vim`

#### Updates ####
Make sure you are up to date:

```
sudo apt-get update

sudo apt-get upgrade
```


#### raspi-config ####
Install this RaspberryPi utility: `sudo apt-get install -y raspi-config`

Now run it: `raspi-config`

You should see a menu containing around ten options to choose from. Make sure to enter the menu **5. Internationalisation Options** and set timezone *(I2)* to `UTC`. The option can be found in the sub menu of "None of the above". This is required to prevent any bugs resulting from the DST transition twice every year. It's also best practice for your database backend anyway.

You should also install any locales you require. Go to **5. Internationalisation Options** and select *I1*. You probably need at least English and Dutch locales: `en_US.UTF-8 UTF-8` + `nl_NL.UTF-8 UTF-8`. You can select multiple locales by pressing the spacebar for each item and finish with TAB + Enter.

* If your sdcard/disk space is not yet fully utilized, select **1. Expand Filesystem**.
* If you do not have a RaspberryPi 2, you might want to select **8. Overclock** -> `setting MODEST, 0 overvolt`! 

If the utility prompts you to reboot, choose yes to reflect the changes you made.

#### Extra's ####
Running the headless Raspbian netinstall? You might like Bash completion. Check [this article](https://www.howtoforge.com/how-to-add-bash-completion-in-debian) how to do this.

Running the full Rasbian install? You should check whether you require the [Wolfram Engine](http://www.wolfram.com/raspberry-pi/), which is installed by default, but takes about a whopping 500 MB disk space! Run `sudo apt-get purge wolfram-engine` if you don't need it.


# Contribution & feedback #
Would you like to contribute? 

## P1 Telegram snaphot ##
Please start by creating an issue with a snapshot of a DSMR telegram. You can find it by executing `sudo supervisorctl tail -n 100 dsmr_datalogger` on your DSMR-reader system. You may omit your unique meter identification, which are lines starting with `0-0:96.1.1` or `0-1:96.1.0`, followed by the meter ID.

## Feedback ##
Also all feedback and input is, as always, very much appreciated! Please create an issue. It doesn't matter whether you run into problems getting started in this guide or just want to get in touch, just fire away. 

## Sentry ##
Another way of contributing is reporting any errors your reader encounters. You can install [Sentry](https://docs.getsentry.com/hosted/), which will log any unhandled errors, even the ones you do not see.

Create separate user for sentry:

`sudo useradd sentry --home-dir /home/sentry --create-home --shell /bin/bash`

`sudo apt-get install -y python-dev python-libxml2 libxml2-dev libxslt1-dev libffi-dev`

Create database & user (postgres is recommended):

```
sudo sudo -u postgres createuser -DSR sentry
sudo sudo -u postgres createdb -O sentry sentry
sudo sudo -u postgres psql -c "alter user sentry with password 'sentry';"

OR

sudo mysqladmin create sentry
echo "CREATE USER 'sentry'@'localhost' IDENTIFIED BY 'sentry';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v
echo "GRANT ALL ON sentry.* TO 'sentry'@'localhost';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v
mysqladmin reload
```

Login and create virtualenv (Python 2x):

`su - sentry`

`mkdir ~/.virtualenvs`

`virtualenv ~/.virtualenvs/sentry --no-site-packages`

Add this to your `~/.bashrc` and logout / login to load your virtualenv:

`source ~/.virtualenvs/sentry/bin/activate`

Install Sentry (8.2.1 or higher):

`pip install sentry==8.2.1`

Create config:

`sentry init`

Edit config and set database settings (user `sentry`, password `sentry`)
`vi .sentry/sentry.conf.py`



# Licence #
The official licence for using this project can be found in the **LICENCE.txt** file. In short, only non-commercial use is allowed for personal usage.


# Credits #
Software and thanks listed below. Please note and respect their licences as well, if any.


* OS: [Raspbian](https://www.raspbian.org/)

* [Raspbian (minimal) unattended netinstaller](https://github.com/debian-pi/raspbian-ua-netinst)

* [Django Project](https://www.djangoproject.com/)

* [Django Solo (plugin)](https://github.com/lazybird/django-solo)

* [Supervisor](http://supervisord.org/)

* [MySQL](https://www.mysql.com/)

* [MariaDB](https://mariadb.org/)

* [PostgreSQL](http://www.postgresql.org/)

* Template: [Director Responsive Admin](http://web-apps.ninja/director-free-responsive-admin-template/)

* [Favicon](http://www.flaticon.com/free-icon/eco-energy_25013)

* [Date Range Picker](http://www.daterangepicker.com/)

Dutch Smart Meter reading specifications, data cables, examples and hints:

* [Gé Janssen](http://gejanssen.com/howto/Slimme-meter-uitlezen/)

* [Joost van der Linde](https://sites.google.com/site/nta8130p1smartmeter/home)

* [SOS Solutions](https://www.sossolutions.nl/)

* [MW](http://bettermotherfuckingwebsite.com/)

Pull requests, forking & testing:

* [Jeroen Peters](https://www.linkedin.com/in/jeroenpeters1986)
* [Daniel ter Horst](https://www.linkedin.com/in/danielterhorst)
