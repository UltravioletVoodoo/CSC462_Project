var=$1;
if [ -z "$var" ]
then
    var="1234"
fi
echo "version: '3'
services:
  floating-database:
    build: .
    image: floating-database:latest
    command: "$var" -s 8080 -i redis
    links: [redis]
    ports: [8080:8080]
  redis:
    image: redis:latest" > docker-compose.yml;