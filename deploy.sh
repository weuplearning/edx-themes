#!/bin/bash

source /edx/app/edxapp/edxapp_env
cd /edx/app/edxapp/edx-platform
sudo chown -R edxapp:edxapp ./*
sudo chown -R edxapp:edxapp ./.*
sudo -E -H -u edxapp env "PATH=$PATH" git stash
sudo -E -H -u edxapp env "PATH=$PATH" git checkout weup_master
sudo -E -H -u edxapp env "PATH=$PATH" git pull upstream weup_master

cd /edx/app/edxapp/edx-themes/amazon
sudo chown -R edxapp:edxapp ./*
sudo chown -R edxapp:edxapp ./.*
sudo -E -H -u edxapp env "PATH=$PATH" git stash
sudo -E -H -u edxapp env "PATH=$PATH" git checkout amazon
sudo -E -H -u edxapp env "PATH=$PATH" git pull origin amazon

echo "Compile translations"
sudo -E -H -u edxapp env "PATH=$PATH" /edx/app/edxapp/venvs/edxapp/bin/paver i18n_fastgenerate
sudo -E -H -u edxapp env "PATH=$PATH" /edx/app/edxapp/venvs/edxapp/bin/python manage.py lms compilejsi18n
sudo -E -H -u edxapp env "PATH=$PATH" /edx/app/edxapp/venvs/edxapp/bin/python manage.py cms compilejsi18n

echo "Paver update"
sudo -E -H -u edxapp env "PATH=$PATH" /edx/app/edxapp/venvs/edxapp/bin/paver update_assets lms --settings=production --themes=amazon
sudo -E -H -u edxapp env "PATH=$PATH" /edx/app/edxapp/venvs/edxapp/bin/paver update_assets cms --settings=production

echo "## Restart ##"
sudo /edx/bin/supervisorctl restart lms: cms: edxapp_worker:
