if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi
DB_CONNECTION_STRING=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}/${POSTGRES_DB}
CELERY_URL=redis://:${REDIS_PASSWORD}@localhost:6379/0
echo $CELERY_URL
echo $DB_CONNECTION_STRING

celery -A app.celery worker --concurrency=1
