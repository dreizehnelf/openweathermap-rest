FROM python:3.6

WORKDIR /app

ENV OPENWEATHERMAPORG_API_KEY set_me_when_you_run_the_container

COPY ["api/", "/app/api/"]
COPY ["openweathermap_rest/", "/app/openweathermap_rest/"]
COPY ["create_admin.sh", "manage.py", "requirements.txt", "run.sh", "tox.ini", "/app/"]

RUN pip install --trusted-host pypi.python.org \
        --no-cache-dir -r requirements.txt

RUN python manage.py migrate
RUN ./create_admin.sh

EXPOSE 8000

CMD ["/app/run.sh"]