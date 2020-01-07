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

exit 0
