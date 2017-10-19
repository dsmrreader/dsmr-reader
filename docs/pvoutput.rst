Integration: PVOutput
=====================


.. contents::
    :depth: 2


PVOutput.org: Automated electricity consumption export
------------------------------------------------------
*How can I link my PVOutput.org account?*

Make sure you have a PVOutput.org account, or `signup for an account <https://pvoutput.org/>`_.
You will have to configure your account and PV system(s). For any support doing that, please `see this page <https://pvoutput.org/help.html#overview-getting-started>`_ for more information.

In order to link DSMR-reader to your account, please write down the "API Key" and "System ID" from your PVOutput account. You can find them near the bottom of the "Settings" page in PVOutput.


.. image:: _static/faq/external_pvoutput_settings.png
    :target: _static/faq/external_pvoutput_settings.png
    :alt: PVOutput account settings


Enter those values in DSMR-reader's admin pages, at "PVOutput: API configuration". Make sure to enter both:

    * API Key
    * System ID


.. image:: _static/faq/pvoutput_api.png
    :target: _static/faq/pvoutput_api.png
    :alt: API settings
    
    
Now navigate to another settings page in DSMR-reader: "PVOutput: "Add Status" configuration". 

    * Enable uploading the consumption.
    * Choose an interval between the uploads. You can configure this as well on the PVOutput's end, in Device Settings.
    * Optionally, choose an upload delay X (in minutes). If set, DSMR-reader will not use data of the past X minutes. 
    * Optionally, you can choose to enter a **processing delay in minutes** for PVOutput. Please note that PVOutput will only allow this when you have a **"Donation" account** on their website. If you do not have one, they will reject each API call you make, until you disable (clear) this option in DSMR-reader. 
    
    
.. image:: _static/faq/pvoutput_add_status.png
    :target: _static/faq/pvoutput_add_status.png
    :alt: Add Status settings

If you configured everything correctly, you should see some addional data in PVOutput listed under "Your Outputs" momentarily.
