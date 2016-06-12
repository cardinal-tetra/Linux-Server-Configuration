##Linux Server Configuration##

###Key Information###

This was the final project of Udacity's Full Stack Web Developer Nanodegree. Students were given the authentication key to a virtual server from Amazon Web Services with the objective of securely hosting a properly functioning catalog application. This included a number of tasks such as installing updates, securing the server from multiple attack vectors, installing/configuring web and database servers- the complete steps are outlined below. The virtual server ceased to host the project after completion of the nanodegree, however the entire point of the exercise was not to build an application but to demonstrate the knowledge and ability to configure a baseline Linux web server to a high standard of security and performance.


###Basic Configuration###

SSH into the virtual server as root user: `ssh -i ~/.ssh/udacity_key.rsa root@52.35.98.40`

For the purposes of assessment, create a new user named grader and input password when prompted: `adduser grader`

Set up key authentication for grader:
1. `mkdir /home/grader/.ssh`
2. `chown grader /home/grader/.ssh`
3. `chgrp grader /home/grader/.ssh`
4. `chmod 700 /home/grader/.ssh`
5. `cp /root/.ssh/authorized_keys /home/grader/.ssh/authorized_keys`
6. `chown grader /home/grader/.ssh/authorized_keys`
7. `chgrp grader /home/grader/.ssh/authorized_keys`
8. `chmod 644 /home/grader/.ssh/authorized_keys`

Give the grader sudo permissions ([askubuntu](http://askubuntu.com/questions/168280/how-do-i-grant-sudo-privileges-to-an-existing-user), [stackoverflow](http://stackoverflow.com/questions/33441873/aws-error-sudo-unable-to-resolve-host-ip-10-0-xx-xx)):
1. `nano /etc/sudoers.d/grader` add these lines and save: grader    ALL = (ALL:ALL) ALL
2. `nano /etc/hosts` add these lines and save: 127.0.0.1 ip-10-20-39-75

Remove root user access:
1. `nano /etc/ssh/sshd_config`
2. Add/edit the following line and save: PermitRootLogin no
3. `service ssh restart`

Upgrade all currently installed packages:
1. `apt-get update`
2. `apt-get upgrade`

Configure local timezone to UTC:
1. `date` shows setting already UTC.

###Secure the Server###
Change SSH port from 22 to 2200 ([digitalocean](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-12-04)):
1. `nano /etc/ssh/sshd_config`
2. Change 'Port' to 2200 and save.
3. `reload ssh`

`exit` and login as the grader with `ssh -i ~/.ssh/udacity_key.rsa -p 2200 grader@52.35.98.40`

Configure UFW ([askubuntu](http://askubuntu.com/questions/187071/how-do-i-restart-shutdown-from-a-terminal, https://help.ubuntu.com/community/UFW#Allow_Access)):
1. `sudo ufw default deny incoming`
2. `sudo ufw default allow outgoing`
3. `sudo ufw allow 2200`
4. `sudo ufw allow 80`
5. `sudo ufw allow 123`
6. `sudo ufw enable`
7. `sudo reboot`
8. Check with `sudo ufw status`

###Deploy Application###

Install Apache and mod_wsgi:
1. `sudo apt-get install apache2`
2. `sudo apt-get install libapache2-mod-wsgi`

Install and configure database ([digitalocean](https://www.digitalocean.com/community/tutorials/how-and-when-to-use-sqlite)):
1. sqlite3 with `sudo apt-get install sqlite3`
2. sqlite3 interface with `sudo apt-get install sqlite3 libsqlite3-dev`

Install dependencies ([digitalocean](https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu-14-04)):
1. pip with `sudo apt-get install python-pip`
2. sqlalchemy with `sudo pip install sqlalchemy`
3. flask with `sudo pip install Flask`
4. git  with `sudo apt-get install git`

Clone and setup the Catalog application ([digitalocean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)):
1. `sudo cd /var/www`
2. `sudo git clone https://github.com/cardinal-tetra/Westeros-Catalog.git`
3. Set up the database: `sudo python catalog/database_setup.py`
4. Populate the database: `sudo python catalog/populate_database.py`
5. Set permissions for database: `sudo chmod 666 catalog/catalog.db`
6. Set permissions for application directory: `sudo chmod 777 catalog`
7. `sudo nano /etc/apache2/sites-enabled/000-default.conf` and insert between the VirtualHost tags, WSGIScriptAlias / /var/www/start.wsgi
8. `sudo nano /var/www/start.wsgi` and write logic to run your application.
9. `sudo apache2ctl restart`

Configure OAuth2 ([python](https://pypi.python.org/pypi/oauth2client/)):
1. `sudo pip install --upgrade oauth2client`
2. Visit Google developer console and add application url to 'Javascript origins' and 'authorised redirect URI'