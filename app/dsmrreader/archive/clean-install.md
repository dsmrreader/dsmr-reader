## (Optional) Operating System Installation ##
Only required when you didn't have your RaspberryPi installed at all.

### Raspbian ###
Either use the headless version of Raspbian, [netinstall](https://github.com/debian-pi/raspbian-ua-netinst), or the [full Raspbian image](https://www.raspbian.org/RaspbianImages), with graphics stack. You don't need the latter when you intend to only use your device for DSMR readings.

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
