Installation: Explained
=======================

.. note::

    The installation guide may take about *15 to 30 minutes* (for RaspberryPi 3), but it greatly depends on your Linux skills and whether you need to understand every step described in this guide.


.. contents::
    :depth: 2


1. Database backend (PostgreSQL)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The application stores by default all readings taken from the serial cable.

- Install database::

    sudo apt-get install -y postgresql

.. note::
    
    Does PostgreSQL not start/create the cluster due to locales? E.g.::
    
      Error: The locale requested by the environment is invalid.
      Error: could not create default cluster. Please create it manually with
    
      pg_createcluster 9.4 main --start

    Try: ``dpkg-reconfigure locales``. 
    
    Still no luck? Try editing ``/etc/environment``, add ``LC_ALL="en_US.utf-8"`` and reboot.
    Then try ``pg_createcluster 9.4 main --start`` again (or whatever version you are using).

(!) Ignore any '*could not change directory to "/root": Permission denied*' errors for the following three commands.

- Create database user::

    sudo -u postgres createuser -DSR dsmrreader

- Create database, owned by the database user we just created::

    sudo -u postgres createdb -O dsmrreader dsmrreader

- Set password for database user::

    sudo -u postgres psql -c "alter user dsmrreader with password 'dsmrreader';"


2. Dependencies
^^^^^^^^^^^^^^^
Now you'll have to install several utilities, required for the Nginx webserver, Gunicorn application server and cloning the application code from the Github repository::

    sudo apt-get install -y nginx supervisor git python3 python3-psycopg2 python3-pip python3-virtualenv virtualenvwrapper

Install ``cu``. The CU program allows easy testing for your DSMR serial connection. 
It's very basic but also very effective to simply test whether your serial cable setup works properly::

    sudo apt-get install -y cu

    
3. Application user
^^^^^^^^^^^^^^^^^^^
The application runs as ``dsmr`` user by default. This way we do not have to run the application as ``root``, which is a bad practice anyway.

Create user with homedir. The application code and virtualenv will reside in this directory as well::

    sudo useradd dsmr --home-dir /home/dsmr --create-home --shell /bin/bash

Our user also requires dialout permissions. So allow the user to perform a dialout by adding it to the ``dialout`` group::

    sudo usermod -a -G dialout dsmr

Either proceed to the next heading **for a test reading** or continue at chapter 4.


Your first reading (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    **OPTIONAL**: You may skip this section as it's not required for the application to install. However, if you have never read your meter's P1 telegram port before, I recommend to perform an initial reading to make sure everything works as expected.

- Now login as the user we have just created, to perform our very first reading! ::

    sudo su - dsmr

- Test with ``cu`` for **DSMR 4+**::

    cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q

- Or test with ``cu`` for **DSMR 2.2** (untested)::

    cu -l /dev/ttyUSB0 -s 9600 --parity=none

You now should see something similar to ``Connected.`` and a wall of text and numbers *within 10 seconds*. Nothing? Try different BAUD rate, as mentioned above. You might also check out a useful blog, `such as this one (Dutch) <http://gejanssen.com/howto/Slimme-meter-uitlezen/>`_.

- To exit cu, type "``q.``", hit Enter and wait for a few seconds. It should exit with the message ``Disconnected.``.


4. Webserver/Nginx (part 1)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

*We will now prepare the webserver, Nginx. It will serve all application's static files directly and proxy any application requests to the backend, Gunicorn controlled by Supervisor, which we will configure later on.*

- Make sure you are acting here as ``root`` or ``sudo`` user. If not, press CTRL + D to log out of the ``dsmr`` user.

Django will later copy all static files to the directory below, used by Nginx to serve statics. Therefor it requires (write) access to it::

    sudo mkdir -p /var/www/dsmrreader/static
    
    sudo chown -R dsmr:dsmr /var/www/dsmrreader/


5. Clone project code from Github
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now is the time to clone the code from the repository into the homedir we created. 

- Make sure you are now acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

- Clone the repository::

    git clone https://github.com/dennissiemensma/dsmr-reader.git

This may take a few seconds. When finished, you should see a new folder called ``dsmr-reader``, containing a clone of the Github repository.    


6. Virtualenv
^^^^^^^^^^^^^

The dependencies our application uses are stored in a separate environment, also called **VirtualEnv**. 

Although it's just a folder inside our user's homedir, it's very effective as it allows us to keep dependencies isolated or to run different versions of the same package on the same machine. 
`More information about this subject can be found here <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

- Make sure you are still acting as ``dsmr`` user (if not then enter: ``sudo su - dsmr``)

- Create folder for the virtualenv(s) of this user::

    mkdir ~/.virtualenvs

- Create a new virtualenv, we usually use the same name for it as the application or project::

    virtualenv ~/.virtualenvs/dsmrreader --system-site-packages --python python3

.. note::

    Note that it's important to specify **Python 3** as the default interpreter.

- Each time you work as ``dsmr`` user, you will have to switch to the virtualenv with these commands::

    source ~/.virtualenvs/dsmrreader/bin/activate
    cd ~/dsmr-reader

- Let's have both commands executed **automatically** every time we login as ``dsmr`` user, by adding them ``~/.bashrc`` file::

    sh -c 'echo "source ~/.virtualenvs/dsmrreader/bin/activate" >> ~/.bashrc'
    sh -c 'echo "cd ~/dsmr-reader" >> ~/.bashrc'

This will both activate the virtual environment and cd you into the right directory on your **next login** as ``dsmr`` user.

.. note::
    
    You can easily test whether you've configured this correctly by logging out the ``dsmr`` user (CTRL + D) and login again using ``sudo su - dsmr``.

    You should see the terminal have a ``(dsmrreader)`` prefix now, for example: ``(dsmrreader)dsmr@rasp:~/dsmr-reader $``

Make sure you've read and executed the note above, because you'll need it for the next chapter. 


7. Application configuration & setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The application will also need the appropriate database client, which is not installed by default. 
For this I created two ready-to-use requirements files, which will also install all other dependencies required, such as the Django framework. 


Setup local config::

    cp dsmrreader/provisioning/django/settings.py.template dsmrreader/settings.py

    cp .env.template .env
    ./tools/generate-secret-key.sh

.. note::

    **Installation of the requirements below might take a while**, depending on your Internet connection, RaspberryPi speed and resources (generally CPU) available. Nothing to worry about. :]

Install dependencies::

    pip3 install -r dsmrreader/provisioning/requirements/base.txt


Optional: Restore a database backup
-----------------------------------

.. warning::

    If you need to restore a database backup with your existing data, this is the moment to do it.

Restoring a database backup? :doc:`See for instructions here <restore>`.


8. Bootstrapping
^^^^^^^^^^^^^^^^
Now it's time to bootstrap the application and check whether all settings are good and requirements are met.
 
- Execute this to initialize the database we've created earlier::

    ./manage.py migrate

Prepare static files for webinterface. This will copy all static files to the directory we created for Nginx earlier in the process. 
It allows us to have Nginx serve static files outside our project/code root.

- Sync static files::

    ./manage.py collectstatic --noinput

Create an application superuser with the following command.
The ``DSMR_USER`` and ``DSMR_PASSWORD`` :doc:`as defined in Env Settings<../env_settings>` will be used for the credentials.

Execute::

    ./manage.py dsmr_superuser

You've almost completed the installation now.

    
9. Webserver/Nginx (part 2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    This installation guide asumes you run the Nginx webserver for this application only.
    
    It's possible to have other applications use Nginx as well, but that requires you to remove the wildcard in the ``dsmr-webinterface`` vhost, which you will copy below.

- Make sure you are acting here as ``root`` or ``sudo`` user. If not, press CTRL + D to log out of the ``dsmr`` user.

Remove the default Nginx vhost (**only when you do not use it yourself, see the note above**)::

        sudo rm /etc/nginx/sites-enabled/default

- Copy application vhost, **it will listen to any hostname** (wildcard), but you may change that if you feel like you need to. It won't affect the application anyway::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/nginx/dsmr-webinterface /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/dsmr-webinterface /etc/nginx/sites-enabled/

- Let Nginx verify vhost syntax and reload Nginx when ``configtest`` passes::

    sudo service nginx configtest

    sudo service nginx reload


10. Supervisor
^^^^^^^^^^^^^^
Now we configure `Supervisor <http://supervisord.org/>`_, which is used to run our application's web interface and background jobs used. 
It's also configured to bring the entire application up again after a shutdown or reboot.

- Copy the configuration files for Supervisor::

    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_datalogger.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_backend.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_client.conf /etc/supervisor/conf.d/
    sudo cp /home/dsmr/dsmr-reader/dsmrreader/provisioning/supervisor/dsmr_webinterface.conf /etc/supervisor/conf.d/

- Login to ``supervisorctl`` management console::

    sudo supervisorctl

- Enter these commands (**listed after the** ``>``). It will ask Supervisor to recheck its config directory and use/reload the files::

    supervisor> reread

    supervisor> update
    
Three processes should be started or running. Make sure they don't end up in ``ERROR`` or ``BACKOFF`` state, so refresh with the ``status`` command a few times.

- When still in ``supervisorctl``'s console, type::

    supervisor> status

Example of everything running well::

    dsmr_backend                     RUNNING    pid 123, uptime 0:00:06
    dsmr_datalogger                  RUNNING    pid 456, uptime 0:00:07
    dsmr_webinterface                RUNNING    pid 789, uptime 0:00:07
    dsmr_client                      RUNNING    pid 982, uptime 0:00:08

Want to quit supervisor? Press ``CTRL + D`` to exit supervisor command line.


----


:doc:`Finished? Go to setting up the application<../application>`.

