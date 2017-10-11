Troubleshooting
===============
If the application happens to stall unexpectedly, you can perform some debugging on your end.

Status page
-----------
The first place to look at is the Status page in the application.
Does it display any error or is it lagging data processing?



Supervisor
----------
You can also view the Supervisor logfiles, depending on whether your datalogger, webinterface or the data processing is broken.
The logfiles are located by default in ``/var/log/supervisor/``. 
You should find logs here regarding the ``dsmr_datalogger``, ``dsmr_backend`` and ``dsmr_webinterface`` processes.

Another option is to tail the (recent) logs in Supervisor.
Enter the control panel with ``sudo supervisorctl`` and type ``tail -f PROCESSNAME`` to follow one. 
The process names are the ones you see when you started the control panel, or you can just enter ``status`` to see them.
You can also use ``start``, ``stop`` or ``restart`` on the processes to give control them.



Appplication / Django
---------------------
The application has it's own logfiles as well.
You can find them in the ``logs`` directory inside the project folder. 
The ``django.log`` will list any internal errors regarding the Django framework it's using.
The other logfile ``dsmrreader.log`` contains application logging, if enabled.

You can log all telegrams received, in base64 format, by adding ``DSMRREADER_LOG_TELEGRAMS = True`` to your ``dsmrreader/settings.py`` config. 
Make sure that you execute ``./reload.sh`` after changing the settings. It should now log the telegrams into ``dsmrreader.log``.



Contact
-------
Are you unable to resolve your problem or do you need any help?
:doc:`More information can be found here<contributing>`.
