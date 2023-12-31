# Flask-UFW

A simple UI for Uncomplicated Firewall (UFW) built with Flask & Bootstrap.

![screenshot](templates/preview.gif)


### Features

- View IPv4 rules
- View IPv6 rules
- Add, delete, search rules
- View UFW status, restart/stop service
- View UFD log file


### Install

1. Install JC:
```
apt-get -qqinstall jc -y
```
2. Install Flask and PIP if not already installed..
```
apt-get install python3-flask -y
apt-get install python3-pip -y 
```
3. Git clone:
```
git clone https://github.com/stefanpejcic/Flask-UFW.git
```
4. Enter the folder and install requirements
```
cd Flask-UFW && install requirements.txt
```
5. run the app:
```
flask run
```
