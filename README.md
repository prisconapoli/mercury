# m3rcury
Mail web service

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py createdb
./run_redis.h
./run_celery.h
python manage.py runserver

Test
coverage run test_api.py
coverage report -m --omit='venv/*'

Deployed
m3rcury.herokuapp.compgrade: python db_
