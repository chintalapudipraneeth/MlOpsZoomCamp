#!/bin/bash

echo "trying to stop docker $1"
docker ps -a >> docker_services
if grep -w $1 docker_services
then
    docker stop $1
    docker rm $1
    echo "deleted and stoped"
else
    echo "dockes does not exists"
fi

rm -f docker_services
