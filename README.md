# Betfair_bot

Bot to make bets to betfair ;)
Work in progress

# Requirements
**Python 3.5.1**
betfair.py

# Setup
* Get your virtual environment up and running (if thats yo thing)
* Install in the requirements (make sure you're doing it for the right python version) ```pip install -r requirements.txt```
* Now Betfair stuff time
* Create your application key. Click [here](https://developer.betfair.com/get-started/#exchange-api) for more information
* Generate your certificates (can do that [here](http://www.bespokebots.com/betfair-ssl-certs.php)
* Combine .crt and .key file to build .pem file `cat client-2048.cert client-2048.key > client-2048.pem`
* Place pem file into certs folder
* Run python main.py
