Introduction
============

Usage
^^^^^
There are plenty of 'scripts' and websites available for performing DSMR readings. This project however is a full stack solution. This allows a decent implementation of most features, but requires a certain 'skill' as you will need to install several dependencies.

I advise to only use this tool when you have basic Linux knowledge or have any interest in the components used. I might create an installer script later, but I'll focus on the build of features first.


Dependencies & requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^
- **RaspberryPi 2 or 3**
 - RaspberryPi 1 should work decently, but I do not actively support it
- **Raspbian OS**
 - Recommended and tested, but any OS satisfying the requirements should do fine.
- **Python 3.3 / 3.4**
- **PostgreSQL 9+ or MySQL / MariaDB 5.5+**
 - I highly recommend *PostgreSQL*
- **Smart Meter** with support for **at least DSMR 4.0/4.2**
 - Tested so far with Landis+Gyr E350, Kaifa.
- **Minimal 100 MB of disk space on RaspberryPi (card)** (for application installation & virtualenv). 
 - More disk space is required for storing all reader data captured (optional). I generally advise to use a 8+ GB SD card. 
 - The readings will take 90+ % of the disk space. I plan however to add some kind of retention to it later, keeping the data (of many years) far below the 500 MB 
- **Smart meter P1 data cable** (can be purchased online and they cost around 20 Euro's).
- **Basic Linux knowledge for deployment, debugging and troubleshooting**
 - It just really helps if you know what you are doing.