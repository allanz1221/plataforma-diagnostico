FROM python:3.7.3

WORKDIR /tmp
COPY requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir
RUN rm /tmp/requirements.txt

WORKDIR /app/diagnostico_project

CMD python manage.py migrate --no-input && \
    python manage.py collectstatic --no-input && \
    gunicorn --bind 0.0.0.0:8000 diagnostico_project.wsgi
