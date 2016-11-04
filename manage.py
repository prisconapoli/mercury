#!/usr/bin/env python
import os
from app import create_app, db
from app.api_1_0.models import Mail
from app.api_1_0.models import Event
from flask_script import Manager,Server
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
manager.add_command("runserver", Server(threaded=True))

@manager.command
def createdb(force=False):
    """ Creates the database if not exist.
    
    Args:
        force: set True to create a new database. Default is false
    """
    if force:
        db.drop_all()
    db.create_all()

if __name__ == '__main__':
    manager.run()