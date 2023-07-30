#!/bin/bash
set -x

cd integration_test/
docker compose up -d
cd ..

echo "waiting one minute"
sleep 60
docker build --network integration_test_integration-backend -t prefect-submit-integration-test -f ci-integration.dockerfile .
docker run --network integration_test_integration-backend -e RUN_EXPERIMENT=0 prefect-submit-integration-test

cd infra/ml-service-fungus
docker build -t neimv/ml-service:testing .
docker run --name ml-fungus -p 8100:8000 --network integration_test_integration-backend -e INTEGRATION_TEST=1 --env-file exp.env -d neimv/ml-service:testing
cd ../..

echo "Waiting two minutes"
sleep 120
docker run --network integration_test_integration-backend -e RUN_EXPERIMENT=1 prefect-submit-integration-test
docker stop ml-fungus && docker rm ml-fungus
cd integration_test/
docker compose down --volumes
cd ..
