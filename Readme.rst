**ShareJockey Website**

Requires >python 3.4.3
Use pyenv to easily manage python versions, other requirements are listed in
*requirements.txt*

check **manage.py** if you aren't familiar with using envdir to manage settings
There are no hardcoded paths, so you should be ready to go by now.

**Other**
There are background tasks (they live in communication/managment/commands):
-python manage.py send_emails
-python manage.py send_texts
that need to be in a cron schedule - celery
additionally there needs to be a background task (written in a similar
way) to create the emails and texts from notifications.


requires Gulp
sudo apt-get update
sudo apt-get install nodejs
sudo apt-get install npm
sudo npm install gulp -g

sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo npm install gulp
sudo npm install gulp-connect gulp-filter gulp-load-plugins gulp-plumber gulp-rename gulp-sass process run-sequence --save-dev
