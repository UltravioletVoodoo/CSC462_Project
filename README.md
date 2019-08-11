# The Floating Database
*This is a proof-of-concept development repository. Do not run this on a production server without properly configuring flask.*

## Instructions
1. Make a virtual environment, then install dependencies with `python -m pip install -r requirements.txt`.
2. Start Redis database server.
3. Run project with `python project.py node_port [partner1_ip:partner1_port partner2_ip:partner2_port ...]`. A console interface is also available with the `--no-flask` flag. `-i` and `-p` can be used to specify the the Redis database's ip and port respectively. `-s` can be used to specify the port of the flask server.
4. (If not running `--no-flask`) Connect to any node's flask server at `node_ip:[flask_port]`.

## Instructions - Docker
*Notes: You may manually have to modify `docker-compose.yml` to pass ports for your specific deployment.*

1. From the project directory, run `docker image build -t floating-database:latest .`.
2. Then, run `./docker-generate.sh "node_port [partner1_ip:partner1_port partner2_ip:partner2_port ...]"; docker-compose up`. Optionally, a second parameter can be passed to `./docker-generate.sh` to change the flask port.

## Future Work
In the future, a load balancing server could provide the web client, which would contain a templated address to the user's geographically closest node. This allows the node server to run in `--api-mode`, and a more user-friendly, asynchronous web application could be more easily developed.