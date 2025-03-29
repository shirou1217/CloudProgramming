
import math
import dateutil.parser
import datetime
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def validate_order_bodytype(bodytype):
    body_parts = ['arm', 'waist', 'calf','thigh','chest']
    if bodytype is not None and bodytype.lower() not in body_parts:
        return build_validation_result(False,
                                       'bodytype',
                                       'We do not have {}, would you like to train different body part?  '
                                       'we have training tutorial for these body parts: {}.'.format(bodytype, ', '.join(body_parts)))
    return build_validation_result(True, None, None)

    


""" --- Functions that control the bot's behavior --- """

def yoga_recommendation(intent_request):
    body_part = intent_request['currentIntent']['slots']['bodytype']
    yoga_url = ''
    
    if body_part == 'arm':
        yoga_url = 'https://www.youtube.com/watch?v=C8oSs8qf_7g'
    elif body_part == 'waist':
        yoga_url = 'https://www.youtube.com/watch?v=jQ4_0eG4i6Q'
    elif body_part == 'calf':
        yoga_url = 'https://www.youtube.com/watch?v=kwfnaNxVJ2g'
    elif body_part == 'thigh':
        yoga_url = 'https://www.youtube.com/watch?v=BjUGjXfwKaY'
    elif body_part == 'chest':
        yoga_url = 'https://www.youtube.com/watch?v=SbyWIRmUohQ'
    else:
        return {
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Failed',
                'message': {
                    'contentType': 'PlainText',
                    'content': f"Sorry, we don't have yoga for {body_part}."
                }
            }
        }
    
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': f"You can try this yoga for {body_part}: {yoga_url}"
            }
        }
    }


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'fineposeconsultation':
        return  yoga_recommendation(intent_request)(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
