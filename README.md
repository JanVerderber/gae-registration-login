# Multiple session and CSRF tokens registration and login app with GAE

A moderately simple registration and login with multiple sessions and CSRF tokens per user. 

## How is this app built?
This app is built with Python using Flask and it is made for use with Google App Engine.

## Which database system does it use?
It uses NoSQL database, Datastore, so it can work with Google App Engine for free.

## How to start the app?
Starting the app is pretty simple. You only need Python 3. The best way is to run the app is by using the app.py in the root of the app. If you are using PyCharm you can right click on the app.py file and select "Run".
When you first open the app in PyCharm it will notify you that you have to install all the packages from requirements.txt. Accept this message and wait for the install to complete. If you are not using PyCharm you will have
to manually install these packages using this command: pip install -r requirements.txt
If you are not using PyCharm to start the app, use this command: python main.py

## What does this app offer?
- Users can register with e-mail and password
- E-mail verification
- Users can login with e-mail and password
- When users login, they see all the users registered and their ID
- Users can change their password using /change-password
- Multiple sessions so users can have more sessions (Login from different clients)
- CSRF protection
- The app checks session and CSRF tokens for expiration
- CRON job that removes unverified users after 24 hours

## Where are enviroment variables?
- Google App Engine doesn't have environment variables. They should be stored inside Settings model in Datastore database. Simply deploy this app to GAE and use Datastore manager to insert your environment variables. Settings include variable "name" for example: "SECRET_KEY", and "value": "dhzaiz21z317bdhak9". By default this app needs 3 variables to work with GAE: PROD_ENV (this should be something like "production_GAE"), SendGrid-Mail (your SendGrid API key) and APP_EMAIL (the e-mail with which you will send app e-mails).
