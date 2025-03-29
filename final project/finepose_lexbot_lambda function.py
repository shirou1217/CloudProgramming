import json
import boto3
import logging
import math
import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def prepareResponse(event, msgText):
    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": event['sessionState']['intent']['name'],
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": msgText
            }
        ]
    }

    return response
def statuscheck(event):
    name=event['sessionState']['intent']['slots']['firstname']['value']['interpretedValue']
    
    
    user_db = boto3.resource('dynamodb')
    user_table = user_db.Table('user_info')
    response = user_table.get_item(
        Key={
            'user': name
        }
    )
    if 'Item' in response:
        item = response['Item']
        # Access the item's attributes
        challenge_id = item['challengeid']
    
    
    
    
    dynamodb = boto3.resource('dynamodb')
    challenge_table = dynamodb.Table('exercise_test')
    response = challenge_table.get_item(
        Key={
            'challenge': challenge_id
        }
    )
    if 'Item' in response:
        item = response['Item']
        # Access the item's attributes
        time = item['time']
        version = item['version']
    
    msgText4=f"still have {time} minutes left for your {version} yoga training .keep going!"
    return prepareResponse(event, msgText4)
def emailconfirmation(event):
    firstName = event['sessionState']['intent']['slots']['name']['value']['interpretedValue']
    email =  event['sessionState']['intent']['slots']['email']['value']['interpretedValue']
    challenge_id = event['sessionState']['intent']['slots']['challengename']['value']['originalValue']
    whentodoyoga = event['sessionState']['intent']['slots']['whentodoyoga']['value']['interpretedValue']
    
    if whentodoyoga=="20:00":
        time="20"
    elif whentodoyoga=="10:00":
        time="10"
    elif whentodoyoga=="13:00":
        time="13"
    elif whentodoyoga=="19:00":
        time="19"
    elif whentodoyoga=="14:30":
        time="14"
        
    client = boto3.client("sns") 
    topic_name1 = str(time) + "Reminder"
    topic = client.create_topic(Name=topic_name1)
    topic_arn = topic['TopicArn']
    client.subscribe(
      TopicArn=topic_arn,
      Protocol='email',
      Endpoint=email
    )
    # store user information into database
    user_db = boto3.resource('dynamodb')
    user_table = user_db.Table('user_info')
    
    # Create the item in DynamoDB
    item = {
        'user': firstName,
        'email' : email,
        'challengeid' : challenge_id,
        'remind':whentodoyoga
    }
    user_table.put_item(Item=item)
    
    # use challenge id to create or join a challenge
    create = False
    if event['sessionState']['intent']['slots']['createorjoin']['value']['originalValue'] == "create":
        create = True

    
    if create:
        client = boto3.client("sns")
        topic = client.create_topic(Name=challenge_id)
        topic_arn = topic['TopicArn']
    else: 
        client = boto3.client("sns")
        response = client.list_topics()
        for topic in response['Topics']:
            if topic['TopicArn'].split(':')[-1] == challenge_id:
                topic_arn = topic['TopicArn']
    client.subscribe(
       TopicArn=topic_arn,
       Protocol='email',
       Endpoint=email
    )        

    
    
    msgText2 = ""
    dynamodb = boto3.resource('dynamodb')
    challenge_table = dynamodb.Table('exercise_test')
    
    print(create)
    if not create:
        try:
            response = challenge_table.get_item(
                Key={
                    'challenge': challenge_id
                }
            )
            if 'Item' in response:
                item = response['Item']
                # Access the item's attributes
                time = item['time']
                version = item['version']
                msgText3=f"{challenge_id} is in {version} version and there is {time} minutes left! we have sent two subscription confirmation email to you! please click subscribe in order to start your yoga training!"
                return prepareResponse(event, msgText3)
        except Exception as e:
            print('Error:', e)
    else:
        msgText2=f"we have sent two subscription confirmation emails to you! please click subscribe in order to start your yoga training!"
        return prepareResponse(event, msgText2)

    #return prepareResponse(event, msgText2)
    

def poseintent(event):
    firstName = event['sessionState']['intent']['slots']['Name']['value']['interpretedValue']
    daystoodoyoga = event['sessionState']['intent']['slots']['daystoodoyoga']['value']['interpretedValue']
    datetostart = event['sessionState']['intent']['slots']['datetostart']['value']['interpretedValue']
    difficulty=event['sessionState']['intent']['slots']['difficulty']['value']['interpretedValue']
    counts=event['sessionState']['intent']['slots']['counts']['value']['interpretedValue']
    

    #print(firstName, iceCreamFlavor, iceCreamSize)

    #discount = event['sessionState']['sessionAttributes']['discount']

    # print('Discount:', discount)
    #firstName = event['sessionState']['intent']['slots']['Name']['value']['interpretedValue']
    
    # get the whentodoyoga and challengeid from user database
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('user_info')
    try:
        response = table.get_item(
            Key={
                'user': firstName
            }
        )
        if 'Item' in response:
            item = response['Item']
            # Access the item's attributes
            whentodoyoga = item['remind']
            challenge_id = item['challengeid']
    
    except Exception as e:
        print('Error:', e)
      
    # create the challenge db    
    challenge_db = boto3.resource('dynamodb')
    challenge_table = challenge_db.Table('exercise_test')
    
    # Create the item in DynamoDB
    item = {
        'challenge': challenge_id,
        'version' : difficulty,
        'time': counts,
        'datetostart': datetostart,
        'daystoodoyoga': daystoodoyoga
    }
    challenge_table.put_item(Item=item)    
    
    msgText = f"your {daystoodoyoga} days {difficulty} yoga training will start at {datetostart} {whentodoyoga}! We'll remind you five minutes before yoga training start."
    
    # client = boto3.client("sns")
    # response = client.list_topics()
    # topic_name = str(challenge_id)
    # for topic in response['Topics']:
    #     if topic['TopicArn'].split(':')[-1] == topic_name:
    #         client.publish(Message=msgText, TopicArn=topic['TopicArn'])

    return prepareResponse(event, msgText)


def lambda_handler(event, context):
    intentName = event['sessionState']['intent']['name']
    print(json.dumps(event['sessionState']['intent']['name'], indent=2))
    response = None
    if intentName == 'poseintent':
        response = poseintent(event)
    elif intentName == 'emailconfirmation':
        response = emailconfirmation(event)
    elif intentName =='statuscheck':
        response=statuscheck(event)
        
    # else:
    #     raise Exception('The intent: ' + intentName + ' is not supported')

    return response
