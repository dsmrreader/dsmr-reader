#!/bin/bash

export GIT_PAGER=cat


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
echo " >>> Deployment complete. <<<"
