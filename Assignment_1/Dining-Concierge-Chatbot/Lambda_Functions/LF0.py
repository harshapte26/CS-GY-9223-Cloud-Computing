import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

aws_access_key_id = 'AKIAXSZ2PUX6MSXMFKPF'
aws_secret_access_key = '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'
dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')

def db_name_check(name):
    table = dynamodb.Table('user_preferences')

    response = table.query(
        KeyConditionExpression=Key('user_name').eq(name)
    )
    print("response iterms in db_name_check_func", response)
    return response['Items'][0]

def lambda_handler(event, context):
  print("context in LF0", context)
  
  if str(event['messages'][0]['unstructured']['text']).lower() == "hi":
    last_reco = db_name_check("abc123")
    text_response = "Hey, as per our last interaction, my suggestions for {cuisine} cuisine are --> \n {prev_res}".format(cuisine = last_reco["cuisine"], prev_res = last_reco["last_reco"])
    response = {
    "messages": [
      {
        "type": "unstructured",
        "unstructured": {
          "id": 1,
          "text": text_response,
          # 'text' : "abc"
          "timestamp": "03-03-2022"
        }
      }
    ]
  }
    return response
  
  else:
    lexClient = boto3.client('lex-runtime')
    lexResponse = lexClient.post_text(
        botName='Dining_Bot',
        botAlias='testdiningbot',
        userId='user123',
        inputText=event['messages'][0]['unstructured']['text']
        # inputText = "hi"
      )
      
    print("Session Attributes in LFO", lexResponse["sessionAttributes"])
      
    response = {
      "messages": [
        {
          "type": "unstructured",
          "unstructured": {
            "id": 1,
            "text": lexResponse['message'],
            # 'text' : "abc"
            "timestamp": "03-03-2022"
          }
        }
      ]
    }
    return response