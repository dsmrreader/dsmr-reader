#!/usr/bin/env bash

# Keep pip in sync with reqs
pip3 install -r dsmrreader/provisioning/requirements/base.txt -r dsmrreader/provisioning/requirements/dev.txt

# List outdated packages
pip list --outdated --local --format freeze | tr '[:upper:]' '[:lower:]' | cut -d'=' -f1 | sort > /tmp/outdated.txt

# List packages from requirements
cat dsmrreader/provisioning/requirements/*.txt | tr '[:upper:]' '[:lower:]' | grep -v '#' | grep -v '.txt' | cut -d'=' -f1 | sort > /tmp/reqs.txt

# Find outdated packages from requirements
comm -1 -2 /tmp/outdated.txt /tmp/reqs.txt > /tmp/outdated-reqs.txt

# Check outdated requirements
[ -s /tmp/outdated-reqs.txt ] || exit 0

echo ""
echo "The following project requirements are outdated:"
echo "------------------------------------------------"
cat /tmp/outdated-reqs.txt
echo ""

exit 1
