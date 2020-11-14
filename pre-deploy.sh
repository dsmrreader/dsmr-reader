#!/usr/bin/env bash

echo ""
echo ""
echo " --- You are currently running version: "
poetry run python -c 'import dsmrreader ; print(dsmrreader.__version__)'

if [ $? -ne 0 ]; then
    echo ""
    echo "     [!] FAILED to call Django (are Poetry and Django installed correctly?)"
    echo ""
    exit 1;
fi

exit 0
