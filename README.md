# WeatherStatus
Taking the temperature of ten cities every minutes

1_ start redis

2_ run celery and celery beat with use:

celery -A weather_status beat --loglevel=info

celery -A weather_status worker --loglevel=info
