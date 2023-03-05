#!/bin/bash

echo [DEBUG] environment $BUILD_ENV

if [ "$BUILD_ENV" = "production" ] ; then
    exec supervisord -c supervisor/supervisord.conf
else
    exec python app.py
fi
