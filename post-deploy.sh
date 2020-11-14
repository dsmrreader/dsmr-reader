#!/usr/bin/env bash

echo ""
echo ""
echo " --- Checking Python version."
poetry run ./check_python_version.py

if [ $? -ne 0 ]; then
    echo "[!] Aborting post-deployment"
    exit 1;
fi


echo ""
echo ""
echo " --- Installing dependencies."
poetry install --no-dev


echo ""
echo ""
echo " --- Applying database migrations."
poetry run ./manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo " >>>>> [!] Executing database migrations failed! <<<<<"
    echo "       [i] Trying to automatically resolve with 'dsmr_sqlsequencereset'."

    # Try auto fix.
    poetry run ./manage.py dsmr_sqlsequencereset

    # Run migrations again.
    poetry run ./manage.py migrate --noinput

    if [ $? -ne 0 ]; then
        echo ">>>>> [!] Executing database migrations failed again! <<<<<"
        echo "        - Running dsmr_sqlsequencereset did not resolve the problem."
        echo "        - Create an issue on Github and attach the exeception trace listed above."
        exit 1;
    fi
fi


echo ""
echo ""
echo " --- Checking & synchronizing static file changes."
poetry run ./manage.py collectstatic --noinput


echo ""
echo ""
echo " --- Reloading running apps..."
./reload.sh


echo ""
echo ""
echo " --- Clearing cache..."
poetry run ./manage.py dsmr_frontend_clear_cache
