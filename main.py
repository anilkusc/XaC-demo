from helpers import ec2controller
import yaml
import time
while True:
    with open("configs.yaml", "r") as configFile:
        config = yaml.safe_load(configFile)
    ec2controller(config["imageID"],config["replicas"],config["instanceType"])
    time.sleep(30)