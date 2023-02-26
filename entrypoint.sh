#!/bin/bash
#service nginx start
exec supervisord -c supervisor/supervisord.conf
