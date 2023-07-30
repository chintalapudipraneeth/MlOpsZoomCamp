#!/bin/sh
echo "Init localstack s3"
awslocal s3 mb s3://mlflow
awslocal s3 mb s3://prefect
