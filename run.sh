#!/bin/sh
set -e

if [ "$OPENWEATHERMAPORG_API_KEY" = "set_me_when_you_run_the_container" ]; then

    echo
    echo "*** ** *"
    echo "* You need to set the OPENWEATHERMAPORG_API_KEY environment variable"
    echo "* when running the docker image."
    echo "* (current value: \"$OPENWEATHERMAPORG_API_KEY\")"
    echo "*** ** *"
    echo

else

    echo
    echo "*** ** *"
    echo "* Launching tox in the background..."
    echo "* (this will take a while, be patient)"
    echo "*** ** *"
    echo

    tox &

    echo
    echo "*** ** *"
    echo "* Launching django server..."
    echo "*** ** *"
    echo

    python manage.py runserver 0.0.0.0:8000

fi