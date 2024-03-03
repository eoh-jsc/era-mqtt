# Build history

Release version (main).

Not include `Deploy production`, means 1m30s

[![Build history](https://buildstats.info/github/chart/eoh-jsc/era-mqtt?branch=main&&buildCount=30)](https://github.com/eoh-jsc/era-mqtt/actions)

# Usage

flask db init
flask db migrate -m "Initial migration."
flask db upgrade

When install new package, must making docker-copmpose up --build again
