flask db init
flask db migrate -m "Initial migration."
flask db upgrade

When install new package, must making docker-copmpose up --build again
