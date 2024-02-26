#!/bin/bash

echo [DEBUG] current environment $BUILD_ENV

if [ "$BUILD_ENV" = "production" ] ; then
    exec supervisord -c supervisor/supervisord.conf
else
#    echo [DEBUG] start EMQX
#    emqx start

    echo [DEBUG] start Flask
    exec python3 app.py
fi
