#!/bin/bash

echo ""
echo ""
echo " --- You are currently running version: "
python -c 'import dsmrreader ; print(dsmrreader.__version__)'

if [ $? -ne 0 ]; then
    echo ""
    echo "     [!] FAILED to call Django (did you activate the 'dsmrreader' VirtualEnv before running?)"
    echo ""
    exit 1;
fi


echo ""
echo ""
echo " Please make sure you've read EACH release note BEFORE deploying, since some"
echo " changes might not always be backwards compatible or depend on your database!"
echo ""
echo "     >>>   https://github.com/dennissiemensma/dsmr-reader/releases   <<<"

echo ""
echo ""
echo " ~~~ Still want to deploy? (type Y + ENTER to continue or press CTRL + C to abort) "
user_input=""
read user_input

if [[ $user_input == 'y' || $user_input == 'Y' ]]; then
    exit 0
fi

exit 1
