<p align="center">
  <img src="https://github.com/prisconapoli/mercury/blob/master/app/static/images/logo.png" width="15%"/>
</p>

# M3rcury Email Service

The M3rcury project presents a solution for the [Uber© Email Service](https://github.com/uber/coding-challenge-tools/blob/master/coding_challenge.md) coding challenge. The challenge consists in design and develop a mail service that accepts the necessary information from the users and sends emails.
To provide service availability, the service uses internally two email services.


Live on [Heroku](https://m3rcury.herokuapp.com).

Check my LinkedIn [profile](http://ie.linkedin.com/in/prisconapoli)

## Overview

M3rcury is a full stack application. The service is exposed through a RESTful API compliant with the standard Internet protocols HTTP and JSON. Users can also send requests filling a web form in the [live site](https://m3rcury.herokuapp.com).

The backend validates and dispatch the email received throught the RESTful API, keeps track of the status of every message processedn and retry in case of failures. [Mailgun](https://sendgrid.com) and [Sendgrid](https://sendgrid.com) are the email service providers.
In order to increase response time and scalability, the application can be configured to use a task queue to distribute the load across the workers.

The front-end consists of two web pages, respectively to submit a new email, and get the links to explore the status information.

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
- Specify environment variables or edit configuration files:
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

- Install the module required and create the database
```
pip install -r requirements.txt
python manage.py createdb
```
- Open a separate windows to start Redis
```
run_redis.h
```
- Open a separate windows to start Celery
```
run_celery.h
```

- Start the server
```
python manage.py runserver
```

To stop the service hit ```CTRL+C```

Exit the virtual environment
```
deactivate
```

To force the creation of a new database
```
python manage.py createdb --force
```

#### Usage
The fastest way is use the [live site](https://m3rcury.herokuapp.com). Fill the form and click on *send* button.

<p align="center">
  <img src="https://github.com/prisconapoli/mercury/blob/master/images/homepage.jpg" width="50%"/>
</p>

If everything is fine, you will be redirect through a new page that contains the links to see your request and the processing status:

<p align="center">
  <img src="https://github.com/prisconapoli/mercury/blob/master/images/accepted.jpg" width="50%"/>
</p>

You can also use the API (in this example I use httpie as HTTP client. Moreover, in the responses I have reported only the relevant content to keep the response short):

```
user$  http --json POST https://m3rcury.herokuapp.com/api/v1.0/mails/ sender=mercury@olimpus.com recipient=prisco.napoli@gmail.com subject="You made my day\!" content="Hi Prisco,\r\nm3rcury saved my life\!\r\nI use deliver ..."

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

Now you can check what is the status of the request using the events url
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

Checking the last event (id=202), you can see the email has been delivered with success (status_code = 202) by *Sendgrid* on *06 Nov 2016 11:39:41 GMT* (created_at=1478432381838607104)

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
Make sure that the service is running, then open a separate window and run *test_api.py*
```python test_api.py```

Coverage test

```
coverage run test_apy.py
coverage report -m --omit='venv/*'
```

#### Improvements
If I had more time, I wish to do the following improvements:

- **email**: add support for cc,bcc, html content, small attachment (e.g. up to 5 MB), jumbo mail (e.g. with dropbox or google drive integrtion)
- **real-time views**: track the mail status in real-time, monitor the average load of the system, arrival rate, average processing time
- **event-driven system**: replace SQLAlchemy and the task queue with a complete publish subscribe solution, e.g. kafka or kinesis
- **dynamic dispatching**: introduce different classes of requests (e.g.  text only message, with html, small or large attachment,  multiple recipients) and use separate workers for every class
- **retry policy**: define a strategy to reprocess or notify the sender the messages accepted by the system but not delivered due a failure of all the mail providers

##### Things left out
I had no time to create web pages to track the progress of every request in real time. The idea is collect all the events related to a mail, and show them along with time information and delivery status.

Moreover, I was unable to add a command in *manage.py* to run test, e.g. 
```
python manage.py test 
python manage.py test coverage
```
This is a limitation of Flask-Scripts which can't run test with multithread mode enabled.

##### Service limitation
**Mailgun** requires a list of *Authorized Recipients*. All the emails to Unknown address will be discarded.
**Celery + Redis**: the task queue is disabled on Heroku. It was necessary update to a billable plan. User can test it in the development environment running the scripts in two separate windows:
```
    ./run_resis.sh
    ./run_celery.sh
```


##Architecture
I have designed M3rcury with the following goals:
- availability: the service should be accessible across Internet, e.g. RESTful API, HTTP + JSON
- scalability:  should be easy take advantage of additional computational/storage resources, or have many teams of developers that works on different parts of the application
- reliablility: define a retry policy in case of failures, handle graceful degradation
- devops friendly: should be easy deploy and monitoring the status of the application
- security: allows connections over https, don't expose private keys

The first step was define a **mail model**, where the process of send an email has been split in a series of steps(or events). Look at the image below:

![alt text][event_model]

[event_model]: https://github.com/prisconapoli/mercury/blob/master/images/mail_model.jpg

With this model, I've started to investigate what kind of components were required to perform these steps.
- validation can be done in the RESTFul API
- a dispatcher can choose the mail provider and retry in case of failures
- a task queue will distribute the load, with the guarantee of built-in persistance
- separate workers for every mail service providers

An important goal for me was design an *observable* system. Basically, it should be possible keep track of every decision taken inside the application, and answer questions:
- when this email entered the system? How much time taken to delivery it?
- why the email has not been delivered to the recipient? Was a validation failure? Maybe the task queue was down?
- what are the mail providers choosen by the dispatcher to serve a particular message?
- how much time a message stays in the queue?
- what is the fastest mail provider?
- what are the failure rates of the mail providers?

As a consequence, I have decided to provides through the API the methods to store and retrieve all the events related to a particular mail.

With the considerations reported before, I have defined the API endpoints and the information to store for mails and events:

#### RESTful API

| HTTP Method | URI                                                             | ACTION                 |
|-------------|-----------------------------------------------------------------|------------------------|
| GET         | http[s]://[hostname]/api/v1.0/                                  | Retrieve API version and endpoints   |
| GET         | http[s]://[hostname]/api/v1.0/mails/                            | Retrieve list of mails |
| POST        | http[s]://[hostname]/api/v1.0/mails/                            | Create a new mail      |
| GET         | http[s]://[hostname]/api/v1.0/mails/[mail_id]                   | Retrieve a mail        |
| POST        | http[s]://[hostname]/api/v1.0/mails/[mail_id]/events/           | Create a new event     |
| GET         | http[s]://[hostname]/api/v1.0/mails/[mail_id]/events/[event_id] | Retrieve an event      |


#### Mail
| field     | description            |
|-----------|------------------------|
| id        | unique identifier      |
| sender    | sender address         |
| recipient | recipient address      |
| subject   | subject of the message |
| content   | message content        |
| events    | link to events         |

#### Event
| field      | description                       |
|------------|-----------------------------------|
| id         | unique identifier                 |
| created_at | creation time                     |
| created_by | creator of the event              |
| event      | event description                 |
| mail       | the mail the event refers to      |
| blob       | additional information, e.g. JSON |


### Technology Stack
As last step, I have investigated the best Technology to develop what I had in mind. I ended up to develop M3rcury with Python and Flask. Flask is a largely adopted microframework to build web applications. It is well documented (tons of tutorials, book and videos onlines) and well integrated with a large number of extensions to support typical use cases, e.g. web forms, databases, working queue, caching, test automation. Below the technology stack used in the application.

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