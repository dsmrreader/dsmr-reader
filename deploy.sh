#!/bin/bash

export GIT_PAGER=cat

./pre-deploy.sh


# Abort when user not sure.
if [ $? -ne 0 ]; then
    echo "[!] pre-deployment: user aborted or script failed"
    exit;
fi


echo ""
echo ""
echo " --- Pulling remote repository for new commits..."
git fetch


echo ""
echo ""
echo " --- The following changes will be applied (if any):"
echo ""
git log --pretty=format:'[%h] %s (%ar)' ..origin/master


echo ""
echo ""
echo " --- Merging/updating checkout."
git merge FETCH_HEAD

echo ""
echo ""
echo " >>> Running post-deployment script. <<<"
./post-deploy.sh


echo ""
echo ""
echo " --- Deployed version: "
python -c 'import dsmrreader ; print(dsmrreader.__version__)'


echo ""
echo ""
echo " >>> Deployment complete. <<<"
