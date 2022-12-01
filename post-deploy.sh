#!/usr/bin/env bash

echo ""
echo ""
echo " --- Checking whether '.venv' VirtualEnv is activated."
python -c 'import sys; exit_code = 0 if hasattr(sys, "real_prefix") else 1; sys.exit(exit_code);'

if [ $? -ne 0 ]; then
    echo "     [i] ----- Activating '.venv' VirtualEnv..."
    source ~/dsmr-reader/.venv/bin/activate

    if [ $? -ne 0 ]; then
        echo ""
        echo "     [!] Aborting, failure switching to '.venv' VirtualEnv (is it installed properly?)"
        echo ""
        exit 1;
    fi
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
echo " --- Checking & synchronizing base requirements for changes."
pip3 install -r dsmrreader/provisioning/requirements/base.txt --upgrade

if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Aborting, failure RUNNING PIP INSTALL"
    echo ""
    exit 1;
fi


echo ""
echo ""
echo " --- Applying database migrations."
./manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo ""
    echo " >>>>> [!] Executing database migrations failed! <<<<<"
    echo "       [i] Trying to automatically resolve with 'dsmr_sqlsequencereset'."

    # Try auto fix.
    ./manage.py dsmr_sqlsequencereset

    # Run migrations again.
    ./manage.py migrate --noinput

    if [ $? -ne 0 ]; then
        echo ">>>>> [!] Executing database migrations failed again! <<<<<"
        echo "        - Running dsmr_sqlsequencereset did not resolve the problem."
        echo "        - Create an issue on GitHub and attach the exception trace listed above."
        exit 1;
    fi
fi


echo ""
echo ""
echo " --- Checking & synchronizing static file changes."
./manage.py collectstatic --noinput

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
./manage.py dsmr_frontend_clear_cache
