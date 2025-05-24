#!/bin/bash
chmod 600 ~/.ssh/id_rsa
docker compose down
docker rm -f $(docker ps -a -q)
docker ps -a -f status=exited 
docker build -t simple_offer_bot .
docker build -t simple_offer_redis .
docker run -it -v ~/.ssh:/root/.ssh:ro simple_offer_bot
docker run -it simple_offer_redis
# docker compose up --build --remove-orphans