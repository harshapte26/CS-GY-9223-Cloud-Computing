import boto3
import json
import logging
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import random


host = 'search-dining-data-qfw4pvxyoa6fxcur6j7fdxoqfa.us-east-1.es.amazonaws.com' 

es = Elasticsearch(
    http_auth = ('test', 'Test@1234'),
    hosts = [{'host': host, 'port': 443}],
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)  

sqsQurl = "https://sqs.us-east-1.amazonaws.com/521424315900/DiningChatbotQueue"
SENDER = "cloudspring2022@gmail.com"
sqsclient = boto3.client('sqs',  region_name='us-east-1',aws_access_key_id='***************',aws_secret_access_key='******************')

def add_user_prefs(cuisinetype, recos):
    aws_access_key_id = 'AKIAXSZ2PUX6MSXMFKPF'
    aws_secret_access_key = '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'

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
    try:
        table = dynamodb.Table('user_preferences')
        new_data = {"user_name":"abc123", "cuisine":cuisinetype, "last_reco":recos}
        table.put_item(Item=new_data)
        return "Success"
    except Exception as e:
        print("exceptions in add_db", e)
        return "Failed"

def restaurants_data(index):
    
    aws_access_key_id = '***************'
    aws_secret_access_key = '***************'

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
    
    table = dynamodb.Table('yelp-restaurants')
    ans = ''
    i = 1
    for id in index:
        if i<6:
            response = table.get_item(
                Key={
                    'id': id
                }
            )
            print(response)
            response_item = response['Item']
            print(response_item)
            restaurant_name = response_item['name']
            restaurant_address = response_item['address']
            
            restaurant_zipcode = response_item['zip_code']
            restaurant_rating = str(response_item['rating'])
            ans += "{}. {}, located at {}\n".format(i, restaurant_name, restaurant_address)
           
            i += 1
        else:
            break
    print("db pass")
    return ans

def sendEmail(email,message):
    SUBJECT = "Restaurant Recommendations for you!"
    CHARSET = "UTF-8"
    
    print(email)
    client = boto3.client('ses')
    try:
        
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Message={
                'Body': {
                  
                    'Text': {
                        'Charset': CHARSET,
                        'Data': message,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
           
           
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
def findindex(cuisine):

    host = 'search-dining-data-qfw4pvxyoa6fxcur6j7fdxoqfa.us-east-1.es.amazonaws.com'
    index = 'restaurants'
    url = 'https://' + host + '/' + index + '/_search'

    query = {
            "size": 100,
            "query": {
                "multi_match": {
                    "query": cuisine,
                    "fields": ["categories"]
                }
            }
        }
        
    awsauth = ('test','Test@1234')
    headers = { "Content-Type": "application/json" }
    response = requests.get(url,auth=awsauth, headers=headers, data=json.dumps(query))
    res = response.json()
    noOfHits = res['hits']['total']
    hits = res['hits']['hits']
    buisinessIds = []

    for hit in hits:
        buisinessIds.append(str(hit['_source']['id']))

    ids = random.sample(buisinessIds, 3)
    print(ids)
    return ids
    
def lambda_handler(event, context):
    
    # print("event in Lambda 2", event)
    req_attributes = event['Records'][0]['messageAttributes']
    print("Current attributes", req_attributes)
    
    cuisine = req_attributes['CuisineType']['stringValue']
    print('cuisine', cuisine)
    location = req_attributes['Location']['stringValue']
    dining_date = req_attributes['Date']['stringValue']
    dining_time = req_attributes['Time']['stringValue']
    num_people = req_attributes['NoOfPeople']['stringValue']
    email = req_attributes['Email']['stringValue']
    # print(cuisine)
    
    index = findindex(cuisine)
    details = restaurants_data(index)
    new_db_add = add_user_prefs(req_attributes['CuisineType']['stringValue'], details)
    print("new db add status", new_db_add)
    print("details", details)
    print("type of", type(details))
    
    message = 'Hello! Here are my {cuisine} restaurant suggestions in {location} for {numPeople} people, for {diningDate} at {diningTime}:\n{details}Enjoy your meal :)'.format(
            cuisine=cuisine,
            location=location,
            numPeople=num_people,
            diningDate=dining_date,
            diningTime=dining_time,
            details = details,
        )
    print(message)
    
    sendEmail(email,message)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
