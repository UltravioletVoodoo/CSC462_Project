var1=$1;
var2=$2;
if [ -z "$var1" ]
then
    var1="1234"
fi
if [ -z "$var2" ]
then
    var2="8080"
fi
echo "version: '3'
services:
  floating-database:
    build: .
    image: floating-database:latest
    command: "$var1" -s "$var2" -i redis
    links: [redis]
    ports: ["$var2":"$var2"]
  redis:
    image: redis:latest" > docker-compose.yml;