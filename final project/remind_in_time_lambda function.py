import json
import boto3

def lambda_handler(event, context):
    topic_name ="20Reminder"
    msgText = f"it's time to start your yoga training!"
    
    client = boto3.client("sns")
    response = client.list_topics()
    for topic in response['Topics']:
        if topic['TopicArn'].split(':')[-1] == topic_name:
            client.publish(Message=msgText, TopicArn=topic['TopicArn'])
            print(topic['TopicArn'])
    
