# DSMR Reader #

Installation instructions are based on the Raspbian distro for RaspberryPi, but it should generally work on every Debian based system, as long as the dependencies & requirements are met.

## Usage ##
There are plenty of 'scripts' available online for performing DSMR readings. This project however is a full stack solution. This allows a decent implementation of most features, but requires a certain 'skill' as you will need to install several dependencies. 

I advise to only use this tool when you have basic Linux knowledge or have any interest in the components used. I might create an installer script later, but I'll focus on the build of features first.

## Dependencies & requirements ##
* RaspberryPi 2 *(minimal v1 B required but v2 is recommended)*.
* Raspbian *(or Debian based distro)*.
* Python 3.4 *(Included in the latest Raspbian named "Jessie")*.
* Smart Meter with support for at least DSMR 4.0 *(tested with Landis + Gyr E350 DSMR4)*.
* Minimal 100 MB of disk space on RaspberryPi *(for application installation & virtualenv)*. More disk space is required for storing all reader data captured *(optional)*. I generally advise to use a 8+ GB SD card.
* Smart meter P1 data cable *(can be purchased online and they cost around 20 Euro's each)*.
* Basic Linux knowledge for deployment, debugging and troubleshooting. 

## Installation guide #
The installation guide may take about half an hour, but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.

You should already have an OS running on your RaspberryPi. If not, below is a brief hint for getting things started. Skip the OS chapter below if you already have your RaspberryPi up and running. Just continue directly to the "Application Installation" chapter.

### (Optional) Operating System Installation ###
#### Raspbian ####
Either use the headless version of Raspbian, [netinstall](https://github.com/debian-pi/raspbian-ua-netinst), or the [full Raspbian image](https://www.raspbian.org/RaspbianImages), with graphics stack. You don't need the latter when you intend to only use your decive for DSMR readings.

#### Init ####
Power on RaspberryPi and connect using SSH:

`ssh pi@IP-address` (full image)

or

`ssh root@IP-address` (headless)


##### IPv6 #####
Disable IPv6 if you get timeouts or other weird networking stuff related to IPv6.

```
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf

sysctl -p /etc/sysctl.conf
```

##### Sudo #####
This will allow you to use sudo: `apt-get install sudo`  *(headless only)*

##### Updates #####
Make sure you are up to date:

```
sudo apt-get update

sudo apt-get upgrade
```


##### raspi-config #####
Install this RaspberryPi utility: `sudo apt-get install raspi-config`
Now run it: `raspi-config`. 

You should see a menu containing around ten options to choose from. Make sure to enter the menu **5. Internationalisation Options** and set timezone *(I2)* to `UTC`. This is required to prevent any bugs resulting from the DST transition twice every year. It's also best practice for your database backend anyway.

You should also install any locales you require. Go to **5. Internationalisation Options** and select *I1*. You probably need at least English and Dutch locales: `en_US.UTF-8 UTF-8` + `nl_NL.UTF-8 UTF-8`. You can select multiple locales by pressing the spacebar for each item and finish with TAB + Enter.

* If your sdcard/disk space is not yet fully utilized, select **1. Expand Filesystem**.
* If you do not have a RaspberryPi 2, you might want to select **8. Overclock** -> `setting MODEST, 0 overvolt`! 

If the utility prompts you to reboot, choose yes to reflect the changes you made.

##### Extra's #####
Running the headless Raspbian netinstall? You might like Bash completion. Check [this article](https://www.howtoforge.com/how-to-add-bash-completion-in-debian) how to do this.

Running the full Rasbian install? You should check whether you require the [Wolfram Engine](http://www.wolfram.com/raspberry-pi/), which is installed by default, but takes about a whopping 500 MB disk space! Run `sudo apt-get purge wolfram-engine` if you don't need it.

----


### Application Installation ###
Make sure you have your system running in UTC timezone to prevent weird DST bugs.

#### Database backend ####
The application stores by default all readings taken from the serial cable. Depending on your needs, you can choose for either (option A.) **MySQL/MariaDB** or (option B.) **PostgreSQL**. If you have no idea what to choose, I generally advise to pick MySQL/MariaDB, as it's less complex as PostgreSQL and is easier to learn. For a project of this size and complexity it doesn't matter anyway. :]


##### (Option A.) MySQL/MariaDB ####
Install MariaDB. You can also choose to install the closed source MySQL, as they should be interchangeable anyway. **libmysqlclient-dev** is required for the virtualenv installation later in this guide..

`sudo apt-get install mariadb-server-10.0 libmysqlclient-dev` 

Create database:

`sudo mysqladmin create dsmrreader`

Create user:

`echo "CREATE USER 'dsmrreader'@'localhost' IDENTIFIED BY 'dsmrreader';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v`

Set privileges for user:

`echo "GRANT ALL ON dsmrreader.* TO 'dsmrreader'@'localhost';" | sudo mysql --defaults-file=/etc/mysql/debian.cnf -v`

Flush privileges to activate them:

`mysqladmin reload`

##### (Option B.) PostgreSQL

Install PostgreSQL. **postgresql-server-dev-all** is required for the virtualenv installation later in this guide.

`sudo apt-get install postgresql postgresql-server-dev-all`

Postgres does not start due to locales? Try: `dpkg-reconfigure locales`

No luck? Try editing `/etc/environment`, add `LC\_ALL="en_US.utf-8"` and `reboot`

Ignore any *'could not change directory to "/root": Permission denied'* errors for the following three commands.

Create user:

`sudo sudo -u postgres createuser -DSR dsmrreader`

Create database, owned by the user we just created:

`sudo sudo -u postgres createdb -O dsmrreader dsmrreader`

Set password for user:

`sudo sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"`


#### Dependencies ####
Misc utils, required for webserver, application server and cloning the application code from the repository.

`sudo apt-get install nginx supervisor mercurial python3 python3-pip python3-virtualenv virtualenvwrapper`

Install `cu`. The CU program allows easy testing for your DSMR serial connection. It's very basic but very effective to test whether your serial cable setup works properly.

`sudo apt-get install cu`


#### Application user ####
The application runs as `dsmr` user by default. This way we do not have to run the application as `root`, which is a bad practice anyway. Our user also requires dialout permissions.

Create user with homedir. The application code and virtualenv resides in this directory as well:

`sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash`

Allow the user to perform a dialout.

`sudo usermod -a -G dialout dsmr`


### Webserver (Nginx), part 1 ###
We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy application requests to the backend, Supervisor, which we will configure later on.

Django will copy all static files to a separate directory, used by Nginx to serve statics. 

`sudo mkdir -p /var/www/dsmrreader/static`

`sudo chown -R dsmr:dsmr /var/www/dsmrreader/`

### This first reading ###

Now login as the user we just created, to perform our very first reading!

`sudo su - dsmr`

Test with **cu** (BAUD rate settings for *DSMR v4* is **115200**, for older verions it should be **9600**). 

`cu -l /dev/ttyUSB0 -s 115200 --parity=none`

You now should see something similar to `Connected.` and a wall of text and numbers within 10 seconds. Nothing? Try different BAUD rate, as mentioned above. You might also check out a useful blog, such as [this one (Dutch)](http://gejanssen.com/howto/Slimme-meter-uitlezen/).


### Application code clone ###
Now is the time to clone the code from the repository and check it out on your device. Make sure you are still logged in as our **dsmr** user (if not then enter `sudo su - dsmr` again):

`hg clone https://bitbucket.org/dennissiemensma/dsmr-reader`


### Virtualenv ###

The dependencies our application uses are stored in a separate environment, also called **VirtualEnv**. Although it's just a folder inside our user's homedir, it's very effective as it allows us to keep dependencies isolated or to run different versions of the same package on the same machine. More info can be found [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

`sudo su - dsmr`

Create folder for the virtualenvs of this user:

`mkdir ~/.virtualenvs`

Create a new virtualenv, we usually use the same name for it as the application or project. Note that it's important to specify python3 as the default interpreter: 

`virtualenv ~/.virtualenvs/dsmrreader --no-site-packages --python python3`

Now 'activate' the environment. It effectively direct all aliases for software installed in the virtualenv to the binaries inside the virtualenv. I.e. the Python binary inside `/usr/bin/python` won't be used when the virtualenv is activated, but `/home/dsmr/.virtualenvs/dsmrreader/bin/python` will be instead.

Activate virtualenv & cd to project:

```
source ~/.virtualenvs/dsmrreader/bin/activate

cd ~/dsmr-reader
```

You might want to put the `source ~/.virtualenvs/dsmrreader/bin/activate` command above in the user's `~/.bashrc` (logout and login to test). I also advice to put the `cd ~/dsmr-reader` in there as well, which will cd you directly inside the project folder on login.


### Application configuration & setup ###
Earlier in this guide you had to choose for either **(A.) MySQL/MariaDB** or **(B.) PostgreSQL**. Our applications needs to know what backend to talk to. Therefor I created two default configuration files you can copy, one for each backend. 
The application will also need the appropiate database client, which is not installed by default. For this I also created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework. The `base.txt` contains requirements which the application needs, no matter the backend you choose. 

**Note:** Installation might take a while, depending on your Internet connection, RaspberryPi version and resources. Nothing to worry about. :]

**A.** Did you choose MySQL/MariaDB? Execute these two commands:

```
cp dsmrreader/provisioning/django/mysql.py dsmrreader/settings.py

pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/mysql.txt
```

**B.** Or did you choose MySQL/MariaDB? Then execute these two lines:

```
cp dsmrreader/provisioning/django/postgresql.py dsmrreader/settings.py

pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/postgresql.txt
```

Did every go as planned? When either of the database clients refuses to install due to missing files/configs, make sure you installed `libmysqlclient-dev` (**MySQL**) or `postgresql-server-dev-all` (**PostgreSQL**) earlier in the process, when you installed the database server itself.

Now it's time to bootstrap the application and check whether all settings are good and requirements are met. Execute this to init the database:
 
`./manage.py migrate`

Prepare static files for webinterface. This will copy all statis to the directory we created for Nginx earlier. It allows us to have Nginx serve static files outside our project/code root:

`./manage.py collectstatic --noinput`

Create an application superuser. Django will prompt you for a password. Alter username and email when you prefer other credentials, but email is not (yet) used in the application anyway. The credentials generated can be used to access the administration panel inside the application, which requires authentication.

`./manage.py createsuperuser --username admin --email root@localhost`

**OPTIONAL**: The application will run without your energy prices, but if you want some sensible defaults (actually my own energy prices for a brief period), you may run the command below to import them (fixtures). Note that altering prices later won't affect your reading data, because prices are calculated retroactive anyway. 

`./manage.py loaddata dsmr_stats/fixtures/EnergySupplierPrice.json` 

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


### Supervisor. ###
Now we configure [Supervisor](http://supervisord.org/), which is used to run our application and also all background jobs used. It's also configured to bring the entire applciation up again after a shutdown or reboot. Each job has it's own configuration file, so make sure to copy them all:  

`sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_*.conf /etc/supervisor/conf.d/`

**NOTE**: `dsmr_stats_poller.conf` is LEGACY and should be skipped/removed!

`rm /etc/supervisor/conf.d/dsmr_stats_poller.conf`

Login to supervisor management console:

`sudo supervisorctl`

Enter these commands (after the >). It will ask Supervisor to recheck its config directory and use/reload the files.

> supervisor> `reread`

> supervisor> `update`

Three processed should be started or running. Make sure they don't end up in **ERROR** state, so refresh with 'status' a few times. `dsmr_stats_compactor` and `dsmr_stats_datalogger` will restart every time. This is intended behaviour. `dsmr_webinterface` however should keep running.  
> supervisor> `status`

Example of everything running well:

    dsmr_stats_compactor             STARTING
    dsmr_stats_datalogger            RUNNING
    dsmr_webinterface                RUNNING
 
Want to check whether data logger works? Just tail log in supervisor with:

> supervisor> `tail -f dsmr_stats_datalogger`

You should see similar output as the CU-command used earlier on the command line.
Want to quit supervisor? `CTRL + C` to stop tail and `CTRL + D` once to exit supervisor command line.

### Opening the application ###
Now it's time to view the application in your browser to check whether the GUI works as well. Just enter the ip address or hostname of your RaspberryPi in your browser, for example . Don't know what address your device has? Just type `ifconfig | grep addr` and it should display an ip address, for example:

    eth0      Link encap:Ethernet  HWaddr b8:27:eb:f4:24:de  
              inet addr:192.168.178.150  Bcast:192.168.178.255  Mask:255.255.255.0
              inet addr:127.0.0.1  Mask:255.0.0.0

In this example the ip address is `192.168.178.150`.

Everything OK? Congratulations, this was the hardest part and now the fun begins by monitoring your electricity (and possible gas) consumption! :]

## Reboot test

You might want to `reboot` and check whether everything comes up automatically again with `sudo supervisorctl status`. This will make sure your data logger 'survives' any power surges.

### Public webinterface warning ###
**NOTE**: If you expose your application to the outside world or a public network, you might want to take additional steps: 

* Please make sure to ALTER the `SECRET_KEY` setting in your `settings.py`. Don't forget to run `reload.sh` in the project root, which will force the application to gracefully kill itself and take the new settings into account.

* You should **also** have Nginx restrict application access when exposing it to the Internet. Simply generate an htpasswd string using one of the [many generators found online](http://www.htaccesstools.com/htpasswd-generator/). It's safe to use them, just make sure to **NEVER** enter personal credentials there used for other applications or personal accounts.
paste the htpasswd string in `/etc/nginx/htpasswd`, open the site's vhost in `/etc/nginx/sites-enabled/dsmr-webinterface` and **uncomment** the following lines:

```
##    auth_basic "Restricted application";
##    auth_basic_user_file /etc/nginx/htpasswd;
``` 

Now make sure you didn't insert any typo's by running `sudo service nginx configtest` and then reload with `sudo service nginx reload`. You should be prompted for login on the next application view in your browser.


## Data preservation & backups
You **should (or must)** make sure to periodically BACKUP your data! It's one of the most common mistakes to skip of ignore this. Actually, it happened to myself quite recently as I somehow managed to get my storage SD card corrupt, losing all my data on it. It luckily happened only a month after running my own readings, but imagine all the data you lose when it contained readings for several years. I plan to implement external data exports (#9, #10) in the future, but those will not be compatible for data recovery after a crash. The best advice I can give you is to make sure your database gets dumped daily on a 'safe' location (NOT the SD card self!). You can find an example in `dsmrreader/provisioning/postgresql/backup.sh` for PostgreSQL, which I dump to a separately mounted USB stick on my RaspberryPi.

Also, check your free disk space once in a while. I will implement automatic cleanup settings (#12, #13) allowing you to choose your own retention (for all the source readings).


## Feedback ##
All feedback and input is, as always, very much appreciated! Please send an e-mail to dsmr (at) dennissiemensma (dot) nl. It doesn't matter whether you run into problems getting started in this guide or just want to get in touch, just fire away. 


##  Licence ##
Also included in the **LICENCE** file:

> The MIT License (MIT)
> 
> Copyright (c) [2015] [Dennis Siemensma]
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Credits ##
Software listed below. Please note and respect their licences as well, if any.


* OS: [Raspbian](https://www.raspbian.org/)

* [Raspbian (minimal) unattended netinstaller](https://github.com/debian-pi/raspbian-ua-netinst)

* [Django Project](https://www.djangoproject.com/)

* [Supervisor](http://supervisord.org/)

* [MySQL](https://www.mysql.com/)

* [MariaDB](https://mariadb.org/)

* [PostgreSQL](http://www.postgresql.org/)

* Template: [Director Responsive Admin](http://web-apps.ninja/director-free-responsive-admin-template/)

* [Favicon](http://www.flaticon.com/free-icon/eco-energy_25013)

Dutch Smart Meter reading specifications, data cables, examples and hints:

* [Gé Janssen](http://gejanssen.com/howto/Slimme-meter-uitlezen/)

* [Joost van der Linde](https://sites.google.com/site/nta8130p1smartmeter/home)

* [SOS Solutions](https://www.sossolutions.nl/)

Pull requests & forking:

* [Jeroen Peters](https://www.linkedin.com/in/jeroenpeters1986)