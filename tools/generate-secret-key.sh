#!/usr/bin/env bash
### Generates a new DJANGO_SECRET_KEY for the local installation

CURRENT_DIR=$(cd `dirname $0` && pwd)
SETTINGS_FILE="$CURRENT_DIR/../.env"

if [ ! -e $SETTINGS_FILE ]; then
    echo "[!] No .env file found"
    exit;
fi

# Credits to: https://gist.github.com/earthgecko/3089509
echo "- Generating new secret"
NEW_SECRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)

# Remove existing line
if [ "$(grep '^DJANGO_SECRET_KEY=' $SETTINGS_FILE)" ]; then
    echo "- Removing existing DJANGO_SECRET_KEY value from .env"
    sed -i '/^DJANGO_SECRET_KEY=*/d' $SETTINGS_FILE
fi

# Add new line with new secret
echo "- Adding DJANGO_SECRET_KEY value to .env"
printf "\nDJANGO_SECRET_KEY=$NEW_SECRET\n" >> $SETTINGS_FILE
