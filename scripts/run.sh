#!/bin/bash
chmod 600 ~/.ssh/id_rsa
docker compose down
docker compose up -d