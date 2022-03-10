import json
import boto3
import json
import re
import os
import datetime
import time
import logging
import dateutil
from botocore.exceptions import ClientError


sqsClient = boto3.client('sqs')
sqsQurl = "https://sqs.us-east-1.amazonaws.com/521424315900/DiningChatbotQueue"
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    print('next slot to elicit', slot_to_elicit)
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

def date_time_validator(date, time):
    return (dateutil.parser.parse(date).date() > datetime.date.today()) or (
            dateutil.parser.parse(date).date() == datetime.date.today() and dateutil.parser.parse(
        time).time() > datetime.datetime.now().time())
        
def date_checker(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
    
def ret_result(valid_flag, invalid_slot, message_):
    return {
        'valid_flag':valid_flag,
        'invalid_slot':invalid_slot,
        'message' : {'contentType': 'PlainText', 'content': message_}
    }


def push_to_sqs(QueueURL, msg_body):
    """
    :param QueueName: String name of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    
    print("here in SQS func")
    
    sqs = boto3.client('sqs')

    queue_url = QueueURL
    try:
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=0,
            MessageAttributes={
                'Location': {
                    'DataType': 'String',
                    'StringValue': "Manhattan"
                },
                'CuisineType': {
                    'DataType': 'String',
                    'StringValue': msg_body['CuisineType']
                },
                'NoOfPeople': {
                    'DataType': 'Number',
                    'StringValue': msg_body['NoOfPeople']
                },
                'Date': {
                    'DataType': 'String',
                    'StringValue': msg_body['Date']
                },
                'Time': {
                    'DataType': 'String',
                    'StringValue': msg_body['Time']
                },
                'Email':{
                    'DataType':'String',
                    'StringValue' : msg_body['Email']
                }
            },
            MessageBody=(
                'Information about the diner'
            )
        )
    
    except ClientError as e:
        logging.error(e) 
        return None
    
    return response


def validate_values(loc, cuisine, people, date, time, email):
    print("cuisine in validated ===>", cuisine)
    locations = ['manhattan', 'nyc', 'ny']
    cuisine_types = ['indian', 'mexican', 'chinese', 'japanese', 'thai', 'continental']
    no_of_people = [str(i) for i in range(1,21)]
    no_ = ["one", "two", "three",
                     "four", "five", "six", "seven",
                     "eight", "nine", "ten", "eleven", "twelve",
                  "thirteen", "fourteen", "fifteen",
                  "sixteen", "seventeen", "eighteen",
                  "nineteen", "twenty"]
                  
    no_of_people.extend(no_)
    
    if not loc:
        return ret_result(False, 'Location', "Where are you looking to eat?")
    elif loc.lower() not in locations:
        return ret_result(False, 'Location', "Sorry, but we are currently serving only New York City area!")


    if not cuisine:
        return ret_result(False, 'CuisineType', "Great, What type of cuisine you're looking for?")
    elif cuisine.lower() not in cuisine_types:
        return ret_result(False, 'CuisineType', "Currently available cuisine options are - "+"["+", ".join(cuisine_types)+"]"+"\nPlease choose one of these!")


    if not people:
        return ret_result(False, 'NoOfPeople', "Got it, how many people will be there?")
    elif str(people) not in no_of_people:
        return ret_result(False, 'NoOfPeople', "We can accept booking for upto 20 people only, please enter the valid number")
        

    if not date:
        return ret_result(False, 'Date', "Please tell me the date you are looking for the restaurant suggestions")
    elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
        return ret_result(False, 'Date', "Oh snap, I can't book in the past as I don't have a timestone. You can look for the suggestions for any date from today onwards")
        

    if not time:
        return ret_result(False, 'Time', "Ok, what time you are looking to dine out on " +str(datetime.datetime.strptime(date, '%Y-%m-%d').date())+" ?")
    elif not date_time_validator (date, time):
        return ret_result(False, 'Time', "Unfortunately, I'm not a Dr. Strange, so can't book for time in the past. Please enter any time in the future!")
        

    if not email:
        return ret_result(False, 'Email', "Perfect!, just type in your E-mail address here so that I can send you the suggestions over there!")
    elif '@' not in email.lower():
        return ret_result(False, 'Email', "Please enter valid email address!")
            
    return ret_result(True, None, None)
            


def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    if event["currentIntent"]["name"] == "GreetingIntent":
        answer = "Hi there, how can I help?"
        response = {
        "sessionAttributes":{},
        "dialogAction":
            {
            "type": "Close",
            "fulfillmentState":"Fulfilled",
            "message":
                {
                    "contentType":"PlainText",
                    "content":answer
                }
            }
        }
   
        return response
        
    if event["currentIntent"]["name"] == "ThankYouIntent":
        answer = "You are Welcome, See you soon!"
        response = {
        "sessionAttributes":{},
        "dialogAction":
            {
            "type": "Close",
            "fulfillmentState":"Fulfilled",
            "message":
                {
                    "contentType":"PlainText",
                    "content":answer
                }
            }
        }
   
        return response
    
    
    if event['currentIntent']['name'] == 'DiningSuggestionIntent':
        event_slots = event['currentIntent']['slots']
        source = event['invocationSource']
        
        if source == 'DialogCodeHook':
            event_slots = event['currentIntent']['slots']
            slot_dict = {'Location' : event_slots["Location"],
            'CuisineType': event_slots["CuisineType"], 
            'NoOfPeople': event_slots['NoOfPeople'],
            'Date': event_slots['Date'],
            'Time': event_slots['Time'],
            'Email': event_slots['Email']}
            
        
            validated_result = validate_values(event_slots["Location"], event_slots["CuisineType"], event_slots['NoOfPeople'], event_slots['Date'], event_slots['Time'], event_slots['Email'])
            print("curren validated result", validated_result)
            if not validated_result['valid_flag']:
                event_slots[validated_result['invalid_slot']] = None
                print("event_slots in LF 1", event_slots)
                return elicit_slot(event['sessionAttributes'], event['currentIntent']['name'], event_slots, validated_result['invalid_slot'], validated_result['message'])
                
        broadcast = push_to_sqs(sqsQurl, slot_dict)
        
        if broadcast:
            response = {
                        "dialogAction":
                            {
                             "fulfillmentState":"Fulfilled",
                             "type":"Close",
                             "message":
                                {
                                  "contentType":"PlainText",
                                  "content": "That's great!! I have received your request of restaurant suggestions for {} cuisine. You will shortly receieve an E-mail at {} with the suggestions as per your preferences!".format(
                                      event_slots["CuisineType"], event_slots['Email']),
                                }
                            }
            }
        else:
            response = {
                        "dialogAction":
                            {
                             "fulfillmentState":"Fulfilled",
                             "type":"Close",
                             "message":
                                {
                                  "contentType":"PlainText",
                                  "content": "Sorry, come back after some time!",
                                }
                            }
                        }
        return response