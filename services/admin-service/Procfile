release: python manage.py migrate --noinput
web: daphne -b 0.0.0.0 -p $PORT Handcrafts.asgi:application
# ---- Celery Workers (DISABLED to reduce Railway costs) ----
# Celery tasks run in eager/synchronous mode via CELERY_TASK_ALWAYS_EAGER=True
# To re-enable, uncomment the lines below AND set CELERY_TASK_ALWAYS_EAGER=False
# in Railway environment variables. This will require a separate Redis service.
# worker: celery -A Handcrafts worker -l info
# beat: celery -A Handcrafts beat -l info