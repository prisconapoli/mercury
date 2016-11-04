#!/bin/bash
celery worker -A celery_worker.queue --loglevel=info