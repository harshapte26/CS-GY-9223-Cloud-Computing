import json
import boto3
import time
#from botocore.vendored import requests
import requests

def lambda_handler(event, context):
    # TODO implement
    print('event event event.    ',event)
  
    inputText = event["params"]["querystring"]["q"]
    print('event', event)
    #inputText = "show dogs"
    keywords = get_keywords(inputText)
    print('keywors ', keywords)
    # image_array = get_image_locations(keywords)
    
    if len(keywords) == 1:
        if keywords[0][-1] == 's':
            image_array = get_image_locations([str(keywords[0][0:-1])])[:2]
            # image_array = image_array[:3]
        elif keywords[0][-1] != 's':
            image_array = get_image_locations(keywords)[0:1]
            # image_array = image_array[0]
    
    if len(keywords) == 2:
        if keywords[0][-1] == 's' and keywords[1][-1] == 's':
            image_array = get_image_locations([str(keywords[0][0:-1])])[:2]
            image_array_2 = get_image_locations([str(keywords[1][0:-1])])[:2]
            image_array.extend(image_array_2)
        
        elif keywords[0][-1] == 's' and keywords[1][-1] != 's':
            image_array = get_image_locations([str(keywords[0][0:-1])])[:2]
            image_array_2 = get_image_locations([keywords[1]])[0:1]
            image_array.extend(image_array_2)
        
        elif keywords[0][-1] != 's' and keywords[1][-1] == 's':
            image_array = get_image_locations([keywords[0]])[0:1]
            image_array_2 = get_image_locations([str(keywords[1][0:-1])])[:2]
            image_array.extend(image_array_2)
        
        elif keywords[0][-1] != 's' and keywords[1][-1] != 's':
            image_array = get_image_locations([keywords[0]])[0:1]
            image_array_2 = get_image_locations([keywords[1]])[0:1]
            image_array.extend(image_array_2)
    
    
    return {
        # 'check': event,
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True
        },
        'body': {"results": image_array} 
            # json.dumps(
            # # {"results":image_array}
            # )
        # 'body': json.dumps({"results":keywords})
    }


def get_keywords(inputstr):
    print("before lex")
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName = 'search',
        botAlias = 'searchobject',
        userId = 'searchPhotosLambda',
        inputText = inputstr
    )
    print(response['slots'])
    print("after lex")
    keywords = []
    slots = response['slots']
    keywords = [v for _, v in slots.items() if v]
    print("lex returned keywords",keywords)
    return keywords
    
def get_image_locations(keywords):
    endpoint = 'https://search-photos-********.us-east-1.es.amazonaws.com/_search'
    headers = {'Content-Type': 'application/json'}
    awsauth = ('*****', '*****')
    prepared_q = []
    for k in keywords:
        prepared_q.append({"match": {"labels": k}})
    q = {"query": {"bool": {"should": prepared_q}}}
    r = requests.post(endpoint, auth = awsauth, headers=headers, data=json.dumps(q))
    print(r.json())
    # r = {"took": 7, "timed_out": False, "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0}, "hits": {"total": {"value": 4, "relation": "eq"}, "max_score": 1.0, "hits": [{"_index": "photos", "_type": "photo", "_id": "5uWzhW4B9mNrwci-n6la", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/gettyimages-91495990-170667a.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220611", "labels": ["Plant", "Tree", "Person", "Human", "Tree Trunk", "Outdoors"]}}, {"_index": "photos", "_type": "photo", "_id": "6OW5hW4B9mNrwci-Yqk8", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/scott-eastwood.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-221229", "labels": ["Person", "Human", "Canine", "Dog", "Pet", "Animal", "Mammal"]}}, {"_index": "photos", "_type": "photo", "_id": "5-W0hW4B9mNrwci-ZqlW", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/pjimage-43-2.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220702", "labels": ["Tree", "Christmas Tree", "Ornament", "Plant", "Human", "Person"]}}, {"_index": "photos", "_type": "photo", "_id": "5eWzhW4B9mNrwci-V6mF", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/pjimage-43-2.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220553", "labels": ["Tree", "Ornament", "Christmas Tree", "Plant", "Person", "Human"]}}]}}
    
    image_array = []
    for each in r.json()['hits']['hits']:
        objectKey = each['_source']['objectKey']
        bucket = each['_source']['bucket']
        image_url = "https://" + bucket + ".s3.amazonaws.com/" + objectKey
        image_array.append(image_url)
        print(each['_source']['labels'])
    print(image_array)
    return image_array