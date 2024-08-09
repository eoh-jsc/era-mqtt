# Canopi-mqtt

### Run local

1. Add `.env` file

   ```
   BUILD_ENV=dev
   SQLALCHEMY_DATABASE_URI=postgresql://root:password@postgres/emqx
   API_KEY=Token 123456789
   DD_API_KEY=DD_API_KEY
   DD_ENV=dev
   DD_HOSTNAME=local-mqtt1
   ```

2. Add `certs` folder with empty file

   certs/

   └── chain.pem

   └── private-key.pem

3. Add `mqtt/default_api_key.conf`

   ```
   username:password
   ```

4. Run web, emqx `docker-compose up`

5. Open another tab, run migration `docker compose exec app poetry run flask db upgrade`

6. Done, test MQTT backend api http://localhost:8001/

7. Testing MQTT broker

- Create user
  ```
  $ curl --location 'http://localhost:8001/api/user' --header 'Content-Type: application/json' --header 'Authorization: Basic OlRva2VuIDEyMzQ1Njc4OQ==' --data '{"username": "admin", "password": "canopi#1"}'
  ```
- Create acl
  ```
  $ curl --location 'http://localhost:8001/api/acl' --header 'Content-Type: application/json' --header 'Authorization: Basic OlRva2VuIDEyMzQ1Njc4OQ==' --data '{"username": "admin", "pattern": "#", "read": true, "write": true}'
  ```
- Connect mqtt
    - localhost:1883
    - admin / canopi#1
    - subscribe #
      ![Alt text](mqtt-connect.png)

### Deployment

> Note: The setup almost the same locally, the difference is run on an EC2 instance.

#### AWS

Go to AWS Console, create `EC2 ubuntu` instance

- CPU: t2.medium
- Storage: 40Gb

#### Deploy

1. SSH into EC2

- Go to AWS console, connect into EC2 and `add your ssh key`.
- Go to local computer, ssh into your EC2, `ssh ubuntu@13.250.125.47`

2. Clone project

```
git clone git@github.com:canopi-jsc/canopi-mqtt.git
cd canopi-mqtt
```

3. Adding `.env` file

```
BUILD_ENV=production
SQLALCHEMY_DATABASE_URI=postgresql://root:password@postgres/emqx
API_KEY=Token 123456789
DD_API_KEY=DD_API_KEY
DD_ENV=production
DD_HOSTNAME=mqtt1
```

- API_KEY: a random string. Format: `Token random_string`

  is used for backend when calling api to create user/acl mqtt

- DD_API_KEY: create one from datadog

  is used for collecting request and send to datadog

  https://docs.datadoghq.com/account_management/api-app-keys/#add-an-api-key-or-client-token

4. Buying SSL and add to `certs` folder

5. Running web, emqx `docker-compose up`

6. Opening another cli tab, ssh into EC2, run migration
   `docker-compose run app poetry run flask db upgrade`

7. Creating cloudflare `record`

#### Done, you can now access this link.

API: https://mqtt1.eraiot.online

MQTT: mqtt1.eraiot.online:1883

WSS: mqtt1.eraiot.online:8084

### Build history

Release version (main).

Not include `Deploy production`, means 1m30s

[![Build history](https://buildstats.info/github/chart/eoh-jsc/era-mqtt?branch=main&&buildCount=30)](https://github.com/eoh-jsc/era-mqtt/actions)

### Note

```
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

When install new package, must making docker-copmpose up --build again
