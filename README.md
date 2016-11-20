<p align="center">
  <img src="https://github.com/prisconapoli/mercury/blob/master/app/static/images/logo.png" width="15%"/>
</p>

# M3rcury Email Service

The M3rcury project presents a solution for the [Uber© Email Service](https://github.com/uber/coding-challenge-tools/blob/master/coding_challenge.md) coding challenge. The challenge consists in design and develop a email service that accepts the necessary information from the users and sends emails.
To provide service availability, the service uses internally two email service providers.


Live on [Heroku](https://m3rcury.herokuapp.com).

Check my [profile](http://ie.linkedin.com/in/prisconapoli)

## Overview

M3rcury is a back-end application. The service is exposed through a RESTful API compliant with the Internet protocols HTTP and JSON.
There is also a minimal front-end, to make easy for the average users send a mail filling a form in the [live site](https://m3rcury.herokuapp.com).

The backend validates and dispatch the email received throught the RESTful API, keeps track of the status of every message processed and implements a retry policy in case of failures. [Mailgun](https://sendgrid.com) and [Sendgrid](https://sendgrid.com) are the email service providers.
In order to increase th eresponse time and the scalability of the system, the application can be configured to use a task queue to distribute the load across the workers.

The frontend is minimal, it consists of two web pages, respectively to submit a new email, and get the links to explore the status information. The next step will be add real-time views and a better CSS.

#### Installation/deployment
- Checkout the git repository
```
git clone https://github.com/prisconapoli/mercury
```
- Activate the virtual environment
```
cd mercury
virtualenv venv
source venv/bin/activate
```
- Update the environment, or edit the configuration files:
*config.py*
```
SECRET_KEY
CSRF_SESSION_KEY
```
**mail_config.py**
```
SENDGRID_API_KEY
MAILGUN_URL_API
MAILGUN_DOMAIN_NAME
MAILGUN_API_KEY
```

- Install the modules and create the database
```
pip install -r requirements.txt
python manage.py createdb
```
- Open a separate windows, activate the virtual environment and run the script to download and install Redis
```
source venv/bin/activate
./run_redis.h
```


- Open a separate windows, activate the virtual environment and run the script to start Celery
```
source venv/bin/activate
./run_celery.h
```

- Start the server
```
python manage.py runserver
```

By default, the server run on http://localhost:5000


To stop, hit ```CTRL+C```

Exit the virtual environment
```
deactivate
```

To force the creation of a new database, run
```
python manage.py createdb --force
```

#### Usage
The fastest way is use the [live site](https://m3rcury.herokuapp.com). Fill the form and click on *send* button.

<p align="center">
  <img src="https://github.com/prisconapoli/mercury/blob/master/images/homepage.jpg" width="50%"/>
</p>

If the mail is accepted, the user will be redirect through a new page that contains the links to track your request and the processing status:

<p align="center">
  <img src="https://github.com/prisconapoli/mercury/blob/master/images/accepted.jpg" width="50%"/>
</p>

M3rcury can accept request throught the RESTful API. The examples below use **httpie** as HTTP client( note: the output of the responses have been  truncated, only the relevant content for the discsussion is present):

```


```
Server response
```
HTTP/1.1 202 ACCEPTED
Location: https://m3rcury.herokuapp.com/api/v1.0/mails/36
{}

```
In the HTTP header, **Location** contains the url to get the details of the original request
```
user$ http --json GET https://m3rcury.herokuapp.com/api/v1.0/mails/36

```

Server response
```
HTTP/1.1 200 OK
{
    "content": "Hi Prisco,\\r\\nm3rcury saved my life\\!\\r\\nI use deliver ...", 
    "events": "https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/", 
    "recipient": "prisco.napoli@gmail.com", 
    "sender": "mercury@olimpus.com", 
    "subject": "You made my day\\!", 
    "url": "https://m3rcury.herokuapp.com/api/v1.0/mails/36"
}
```

The response contains an url to check the processing status of the request.

```
http --json GET https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/
```
Server response
```
HTTP/1.1 200 OK
{
    "events": [
        "https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/198", 
        "https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/199", 
        "https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/200", 
        "https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/201", 
        "https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/202"
    ], 
    ...
}
```

Checking the last event (id=202), we see the email has been delivered with success (status_code = 202) by *Sendgrid* on *06 Nov 2016 11:39:41 GMT* (created_at=1478432381838607104)

```
user$ http --json GET https://m3rcury.herokuapp.com/api/v1.0/mails/36/events/202
```

Server response
```
HTTP/1.1 200 OK
{
    "blob": "{\"status_code\": 202}", 
    "created_at": 1478432381838607104, 
    "created_by": "Sendgrid:ae2a2271-beb0-4b52-9c8c-4d007a2cd4c4", 
    "event": "DONE", 
    "mail_id": 36
}
```

#### Testing
Make sure that http server is running (```python manage.py runserver```), then open a separate window and run *test_api.py*
```python test_api.py```

#### Coverage test
The application uses the module *coverage* to run coverage test and generate a report

```
coverage run test_api.py
coverage report -m --omit='venv/*,*config.py,test*.py'
```

#### Profiling
Run manage.py with the option *profile* to find bottlenecks in the application

```
python manage.py profile
```

#### Shell
Run manage.py with the option *shell* to have access to a Python shell. Is useful to set up the database, cronjobs, and other command-line tasks that belong outside the web application itself.

```
python manage.py shell
```

#### Improvements
If I had more time, I wish to do the following improvements:

- **email**: add support for cc,bcc, html content, small attachment (e.g. up to 5 MB), jumbo mail (e.g. with dropbox or google drive integration)
- **real-time views**: track the mail status in real-time, monitor the average load of the system, arrival rate, average processing time, spending time in the queue
- **event-driven system**: replace SQLAlchemy and the task queue with a complete publish subscribe solution, e.g. kafka or AWS Kinesis
- **dynamic dispatching**: introduce different classes of requests (e.g.  text only message, with html, small or large attachment,  multiple recipients) and have different pool of workers dedicated to each class
- **retry policy**: define a strategy to allow the user to reprocess a messages accepted by the system but not delivered due a failure of all the mail providers, e.g. bad recipient address

#### Things left out
Due lack of time I didn't create the web pages to track the progress of every request in real time. The idea is collect all the events related to a mail, and show them along with time information and delivery status. It can be done in AJAX and the flask extension Flask-SocketIO.

Moreover, I was unable to add a command in *manage.py* to exectue the test, e.g. 
```
python manage.py test 
python manage.py test coverage
```
This is a limitation of Flask-Scripts which can't run the test with multithread mode enabled.

#### Service limitation
**Mailgun** requires a list of *Authorized Recipients*. All the emails to Unknown address will be discarded.
**Celery + Redis**: the task queue is disabled on Heroku. It was necessary update to a billable plan. User can test it in the development environment running the scripts in two separate windows:
```
    ./run_redis.sh
    ./run_celery.sh
```


##Architecture
I have designed M3rcury with the following goals:
- availability: the service should be accessible across Internet, e.g. RESTful API, HTTP + JSON
- scalability:  should be easy take advantage of additional computational/storage resources, or have many teams of developers that works on different parts of the application
- reliablility: define a retry policy in case of failures, handle graceful degradation
- devops friendly: should be easy deploy and monitoring the status of the application
- security: allows connections over https, don't expose private keys

The first step was define a **mail sending model**, where the process of send an email has been split in a series of steps(or events). Look at the image below:

![alt text][mail_sending_model]

[mail_sending_model]: https://github.com/prisconapoli/mercury/blob/master/images/mail_model.jpg

With this model, I've started to investigate what kind of components were required to perform these steps:
- validation can be done in the RESTFul API
- a dispatcher can select the mail provider and retry in case of failures
- a task queue can be used to distribute the load, but we need guarantee the built-in persistance
- is better to have indipendent workers for every mail service providers, hopefully with many accounts

An important goal was design an *observable* system. Basically, it should be possible keep track of every decision taken inside the application, and answer questions like:
- when this email entered the system? How much time it taken to delivery it?
- why the email has not been delivered to the recipient? Was a validation failure? Maybe the task queue was down?
- what are the mail providers choosen by the dispatcher to serve a particular message?
- what is the average time spent in the queue?
- what is the fastest mail provider?
- what are the failure rates of the mail providers?

So my decision was include in the API interface also the functionalities to store and retrieve the events for a particular message.

#### RESTful API

| HTTP Method | URI                                                             | ACTION                 |
|-------------|-----------------------------------------------------------------|------------------------|
| GET         | http[s]://[hostname]/api/v1.0/                                  | Retrieve API version and endpoints   |
| GET         | http[s]://[hostname]/api/v1.0/mails/                            | Retrieve list of mails |
| POST        | http[s]://[hostname]/api/v1.0/mails/                            | Create a new mail      |
| GET         | http[s]://[hostname]/api/v1.0/mails/[mail_id]                   | Retrieve a mail        |
| POST        | http[s]://[hostname]/api/v1.0/mails/[mail_id]/events/           | Create a new event     |
| GET         | http[s]://[hostname]/api/v1.0/mails/[mail_id]/events/[event_id] | Retrieve an event      |


Below the models used in SQLAlchemy to track informartion about an email and the correlated events:

#### Mail Model
| field     | description            |
|-----------|------------------------|
| id        | unique identifier      |
| sender    | sender address         |
| recipient | recipient address      |
| subject   | subject of the message |
| content   | message content        |
| events    | link to events         |

#### Event Model
| field      | description                       |
|------------|-----------------------------------|
| id         | unique identifier                 |
| created_at | creation time                     |
| created_by | creator of the event              |
| event      | event description                 |
| mail       | the mail the event refers to      |
| blob       | additional information, e.g. JSON |


### Dispatcher and retry policy
The dispatching mechanism is straightforward. Every request carries a list (called attempts) containing the name of previous failed attempts to send the message. An empty list identifies a new request, while a no-empty list identifies a message that has not been dispatched for some reason.
If is a new message, the mail providers is selected it randomly and the value is added in attempts . However, if the list is not empty, the dispatcher will try to select a new providers that has not been used in the past.

If no providers are available, the dispatcher log a new event 'DISCARDED' and no more attempts are done. 

The choice to store the attempts can seem unusual, but it allows to have many stateless dispatcher in the application. When something goes wrong, the only thing that a dispatcher has to do is check the 'history' of the request to figure out what was wrong.

### Technology Stack
As last step, I have investigated the best technologies to develop what I had in mind. I ended up to choose Python and the Flask microframework to build this initial version of M3rcury. Flask has the advantage to be easy to learn and largely adopted to build web applications. It is well documented (tons of tutorials, books and videos on-line) and well integrated with a large number of extensions to support typical use cases, e.g. web forms, databases, working queue, caching, test automation.

Below is described the final technology stack:

###### Front-end
- Flask-WTF + Bootstrap + Font Awesome for the web pages
- Flask-Cache for view and function caching

###### Back-end: 
- Flask Microframework
- SQLAlchemy (SQLite for development and testing, Postgres in production) to store mails and events
- Celery + Redis for asynchronous task queue and built-in persistence
- SendGrid + Mailgun as service providers

###### Testing and Automation:
- Flask-Script extension for automated tasks: database creation, start the service, profiling
- Test automation, coverage tests, reports

###### Deployment
- gunicorn as HTPP Server
- Heroku as public cloud environment

### Additional note
If you wish to have a new feauture, collaborate on this project,  or just report a bug, please drop me a message with [LinkedIn](http://ie.linkedin.com/in/prisconapoli)