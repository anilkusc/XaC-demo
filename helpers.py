import boto3
import os
from dotenv import load_dotenv
from loguru import logger
def ec2controller(imageId,replicas,instanceType):
    load_dotenv()
    client = boto3.client('ec2',aws_access_key_id=os.getenv('AWSAccessKeyId'),aws_secret_access_key=os.getenv('AWSSecretKey'),region_name='eu-west-1')
    instances = getInstances(client)["Reservations"]
    currentInstances = []
    for instance in instances:
        if isInstanceTerminated(instance["Instances"]) == False:
            currentInstances.append(instance)
    if len(currentInstances) == replicas:
        logger.info("state is equal")
    elif len(currentInstances) > replicas:
        logger.info("some instances will be deleted")
        deleteInstances(client,instances,replicas)
    elif len(currentInstances) < replicas:
        logger.info("some instances will be created")
        createInstance(client,imageId,replicas,instanceType)
    else:
        logger.error(currentInstances)

def getInstances(client):
    return client.describe_instances()

def createInstance(client,imageId,replicas,instanceType):
    response = client.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': 8,
                    'VolumeType': 'gp2'
                },
            },
        ],
        ImageId= imageId, #'ami-6cd6f714',
        InstanceType= instanceType, #'t3.micro',
        MaxCount= replicas, #1,
        MinCount= replicas, #1,
        Monitoring={
            'Enabled': False
        },
    )
    return response

def isInstanceTerminated(instance):
    if instance[0]["State"]["Name"] == "terminated":
        return True
    else:
        return False

def deleteInstances(client,instances,desiredReplicas):
    currentReplicas=len(instances)
    for instance in instances:
        if currentReplicas == desiredReplicas:
            break
        client.terminate_instances(InstanceIds=[instance["Instances"][0]["InstanceId"]],DryRun=False)
        currentReplicas = currentReplicas - 1 
