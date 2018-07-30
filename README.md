## OpenWeatherMap.org REST API

This repository contains a django REST API service that allows to query weather forecasts by using the [OpenWeatherMap.org API](https://openweathermap.org/api).

## Features
- Uses [Python 3](https://www.python.org/)
- Based on [django REST Framework](http://www.django-rest-framework.org/) to simplify further extension
- Showcases a couple of more advanced customizations regarding definition of URL schemas (instead of using just the generic ones)
- Uses automatic generation of documentation
- Uses [tox](https://tox.readthedocs.io/en/latest/) in conjunction with [pytest](https://docs.pytest.org/en/latest/) for testing
- Provides a .travis.yml file for automated testing via [Travis CI](https://travis-ci.org/)
- Includes [flake8](http://flake8.pycqa.org/en/latest/) during testing to enforce proper code formatting
- Includes [coverage.py](https://coverage.readthedocs.io/) during testing to collect and display code coverage statistics

## Prerequisites

You will need to [signup @ OpenWeatherMap.org](https://home.openweathermap.org/users/sign_up) to get an API key.

## Installation

### Via Docker

1. Install [Docker](https://www.docker.io/).

2. Download the [build](https://index.docker.io/u/dreizehnelf/openweathermap-rest/) from the public [Docker Registry](https://index.docker.io/):
   `docker pull dreizehnelf/openweathermap-rest`

   (alternatively, you can build an image from Dockerfile:
   `docker build -t="dreizehnelf/openweathermap-rest" github.com/dreizehnelf/openweathermap-rest`)

#### Usage

##### Environment variables

- `OPENWEATHERMAPORG_API_KEY`: The OpenWeatherMap.org API key to use for queries.

##### Run `openweathermap-rest`

    `docker run -it -p 8000:8000 -e OPENWEATHERMAPORG_API_KEY='<insert-your-key-here>' dreizehnelf/openweathermap_rest:latest`

This will spin up the container, share the django server running in the container on port 8000 to your local port 8000 and launch the test suite via tox in the background.

- API documentation is available at: [http://localhost:8000/weather/docs/](http://localhost:8000/weather/docs/)
- django Admin interface is available at: [http://localhost:8000/admin/](http://localhost:8000/admin/)

The default username is `admin` and the default password is `adminpass`.

### Manual installation

Since you will need the API key to run the REST API service, you either have to:

1. Create a `local_settings.py` in the repository root after cloning and set the `OPENWEATHERMAPORG_API_KEY` variable to your API key, i.e. `OPENWEATHERMAPORG_API_KEY = "<insert-your-key-here>"`
2. Prefix the commands in steps 4 and 5 below with the environment, i.e. `OPENWEATHERMAPORG_API_KEY=<insert-your-key-here> python manage.py runserver`

#### Steps

0. Prepare a Python 3 environment to use (I recommend [pyenv](https://github.com/pyenv/pyenv)) and use it for the next steps
1. Checkout the repository, i.e. `git clone https://github.com/dreizehnelf/openweathermap-rest.git`
2. Change into the repositories directory, i.e. `cd openweathermap-rest`
3. Install the requirements, i.e. `pip install -r requirements.txt`
4. Fire up the django dev server, i.e. `python manage.py runserver
5. (optional) Start another terminal, change into the same folder, activate the env again and launch `tox` to run the tests


