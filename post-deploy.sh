#!/usr/bin/env bash

echo ""
echo ""
echo " --- Checking whether Poetry env exists."
poetry env info

if [ $? -ne 0 ]; then
    echo ""
    echo "     [!] Aborting, failure RUNNING POETRY ENV INFO"
    echo "     [i] Does the command 'poetry about' error as well? If not, there may be an issue regarding your current working dir used while executing this deploy script."
    echo ""
    exit 1;
fi


echo ""
echo ""
echo " --- Checking (minimum) Python version."
./check_python_version.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Aborting, failure CHECKING PYTHON VERSION"
    echo ""
    exit 1;
fi


echo ""
echo ""
echo " --- Checking & synchronizing dependencies for changes."
poetry install --no-dev

if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Aborting, failure RUNNING POETRY INSTALL"
    echo ""
    exit 1;
fi


echo ""
echo ""
echo " --- Applying database migrations."
poetry ./manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo ""
    echo " >>>>> [!] Executing database migrations failed! <<<<<"
    echo "       [i] Trying to automatically resolve with 'dsmr_sqlsequencereset'."

    # Try auto fix.
    poetry ./manage.py dsmr_sqlsequencereset

    # Run migrations again.
    poetry ./manage.py migrate --noinput

    if [ $? -ne 0 ]; then
        echo ">>>>> [!] Executing database migrations failed again! <<<<<"
        echo "        - Running dsmr_sqlsequencereset did not resolve the problem."
        echo "        - Create an issue on GitHub and attach the exeception trace listed above."
        exit 1;
    fi
fi


echo ""
echo ""
echo " --- Checking & synchronizing static file changes."
poetry ./manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Aborting, failure COPYING STATIC FILES"
    echo ""
    exit 1;
fi


echo ""
echo ""
echo " --- Reloading running apps..."
./reload.sh


echo ""
echo ""
echo " --- Clearing cache..."
poetry ./manage.py dsmr_frontend_clear_cache
