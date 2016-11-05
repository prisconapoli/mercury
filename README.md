# M3rcury Email Service

![alt text][logo]

[logo]: https://github.com/prisconapoli/mercury/blob/master/app/static/images/logo.png

The M3rcury project presents a solution for the [Uber© Email Service](https://github.com/uber/coding-challenge-tools/blob/master/coding_challenge.md) coding challenge. The challenge consists in design and develop a mail service that accepts the necessary information from the users and sends emails.
To provide service availability, the service uses internally two email services.

## Overview

M3rcury is a full stack application. The service is exposed through a RESTful API compliant with the standard Internet protocols HTTP and JSON. Users can optionally send requests filling a form available at homepage. Live on [Heroku](https://m3rcury.herokuapp.com).

The backend validates and dispatch the email received throught the RESTful API, keeps track of the status of every message processedn and retry in case of failures. [Mailgun](https://sendgrid.com) and [Sendgrid](https://sendgrid.com) are the email service providers.
In order to increase response time and scalability, the application can be configured to use a task queue to distribute the load across the workers.

The front-end consists of two web pages, respectively to submit a new email, and get the links to explore the status information.

##### Note 
Due lack of time, it was not possible develop also the pages to track the progress of every request in real time.

**Mailgun** requires a list of *Authorized Recipients*. All the emails to Unknown address will be discarded.

## Tech Stack
The application has been developed using Python and Flask. Flask is a largely adopted microframework to build web applications. It is well documented (tons of tutorials, book and videos onlines) and well integrated with a large number of extensions to support typical use cases, e.g. web forms, databases, working queue, caching, test automation. 
###### Front-end
- WTF Flask + Bootstrap + Font Awesome for the web pages
- Flask-Cache for view and function caching

###### Back-end: 
- Flask Microframework
- SQLAlchemy (SQLite for development and testing, Postgres in production)
- Celery + Redis for asynchronous task queue and built-in persistence
- SendGrid + Mailgun as service providers

###### Testing and Automation:
- Flask-Script extension for automated tasks: database creation, start the service, profiling
- Test automation, coverage tests, reports

###### Deployment
- gunicorn as HTPP Server
- Heroku as public cloud environment

## Improvements
Spending more time, the application can be improved in different ways:

- **mail**: cc/bcc, html content, small attachment (e.g. up to 5 MB), jumbo mail (e.g. with dropbox or google drive integrtion)
- **real-time views**: report the status of every request in real-time, monitor the average load of the system

- **event-driven system**: replace SQLAlchemy and the task queue with a publish subscribe system, e.g. kafka or kinesis
- **dynamic dispatching**: specify different classes of requests (e.g.  text only message, with html, small or large attachment,  multiple recipients) and use an indipendent pool of workers for every class
- **retry**: define a strategy to analyze and eventually reprocess the messages accepted by the system but not delivered due a failure of all the mail providers. 


##Architecture

![alt text][event_model]

[event_model]: https://github.com/prisconapoli/mercury/blob/master/mail_model.jpg
