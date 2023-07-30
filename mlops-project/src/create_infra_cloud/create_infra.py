# -*- coding: utf-8 -*-
import os
import time
import logging

import boto3

PATH_AWS = "cloud/aws_cf"
PATH_K8S = "cloud/k8s"


def create_infra(ctx):
    client = boto3.client('cloudformation')
    files_aws = os.listdir(PATH_AWS)
    files_aws.sort()
    files_k8s = os.listdir(PATH_K8S)

    logging.debug(files_aws)
    logging.debug(files_k8s)
    create_pair()
    create_cloudformation(client, files_aws)


def create_cloudformation(client, files):
    for file in files:
        with open(os.path.join(PATH_AWS, file), 'r') as file_cf:
            cf = ''.join(file_cf.readlines())

        name = file.split('.')[0]
        name = name[3:]
        try:
            response = client.create_stack(
                StackName=name,
                TemplateBody=cf,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
            )
        except Exception as e:
            logging.warning("%s error: " % str(e))
            logging.warning("%s already exists" % name)
            continue
        logging.debug(response)
        id_stack = response['StackId']
        check_status_cf(client, id_stack)


def check_status_cf(client, stack_id):
    data = client.describe_stacks(StackName=stack_id)

    while True:
        status = data['Stacks'][0]['StackStatus']
        logging.warning(f"in status {status}")

        if status in ('CREATE_IN_PROGRESS', 'DELETE_IN_PROGRESS'):
            logging.warning("check every 10 seconds")
            time.sleep(10)
        elif status in ('CREATE_COMPLETE', 'DELETE_COMPLETE'):
            return
        elif status in ('CREATE_FAILED', 'DELETE_FAILED'):
            raise Exception("Failed to create or delete")
        else:
            raise Exception("?_? I don't understand the error")

        data = client.describe_stacks(StackName=stack_id)


def create_variables():
    print("hello")


def create_services_k8s():
    pass


def create_pair():
    client = boto3.client("ec2")
    response = client.create_key_pair(KeyName='dataneimv')
    logging.info("%s" % str(response))
