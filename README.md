# Build history

Release version (main).

Not include `Deploy production`, means 1m30s

[![Build history](https://buildstats.info/github/chart/eoh-jsc/era-mqtt?branch=main&&buildCount=30)](https://github.com/eoh-jsc/era-mqtt/actions)

# Note
When install new package, must making docker-copmpose up --build again

# Run local

### Add .env file
```
BUILD_ENV=dev 
SQLALCHEMY_DATABASE_URI=postgresql://root:password@postgres/emqx 
API_KEY=Token 123456789
DD_API_KEY=DD_API_KEY 
DD_ENV=dev
DD_HOSTNAME=local-mqtt1
```

### Add certs folder with empty file

certs/ 

└── chain.pem 

└── private-key.pem

### Run web, emqx
```
docker-compose up
```
### Open another tab, run migration
```
docker-compose exec app poetry run flask db upgrade 
```

### Testing MQTT api
http://localhost:8001/ 

### Testing MQTT broker
Create user
```
$ curl --location 'http://localhost:8001/api/user' --header 'Content-Type: application/json' --header 'Authorization: Basic OlRva2VuIDEyMzQ1Njc4OQ==' --data '{"username": "admin", "password": "canopi#1"}' 
```

Create acl
```
$ curl --location 'http://localhost:8001/api/acl' --header 'Content-Type: application/json' --header 'Authorization: Basic OlRva2VuIDEyMzQ1Njc4OQ==' --data '{"username": "admin", "pattern": "#", "read": true, "write": true}'
```

Connect mqtt
- localhost:1883
- admin / canopi#1
- subscribe #

Done.
