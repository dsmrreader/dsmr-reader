#!/bin/bash
### Generates a new SECRET_KEY for the local installation

NOW=$(date)
CURRENT_DIR=$(cd `dirname $0` && pwd)
SETTINGS_FILE="$CURRENT_DIR/../dsmrreader/settings.py"

if [ ! -e $SETTINGS_FILE ]; then
    echo "[!] No dsmrreader/settings.py file found"
    exit;
fi

# Credits to: https://gist.github.com/earthgecko/3089509
echo "- Generating new secret"
NEW_SECRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)

# Remove existing line
if [ "$(grep '^SECRET_KEY=' $SETTINGS_FILE)" ]; then
    echo "- Removing existing SECRET_KEY value from settings.py"
    sed -i '/^SECRET_KEY=*/d' $SETTINGS_FILE
fi

# Add new line with new secret
echo "- Adding SECRET_KEY value to settings.py"
printf "\nSECRET_KEY='$NEW_SECRET'  # Generated @ $NOW\n" >> $SETTINGS_FILE
