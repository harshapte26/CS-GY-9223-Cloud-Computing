
import json
import boto3
import requests

## Test comment for code pipeline test

s3_client = boto3.client(
    's3',
    aws_access_key_id="************",
    aws_secret_access_key="***************"
)

def detect_labels(photo, bucket):
    labels_res = []

    client=boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)

    print('Detected labels for ' + photo) 
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        labels_res.append(label['Name'])
    
    im_metadata = s3_client.head_object(Bucket='album-photo-store', Key=photo)
    
    if len(im_metadata['Metadata']) != 0:
        user_labels = im_metadata['Metadata']['customlabels'].split(",")
        labels_res.extend(user_labels)
    
    return labels_res

def lambda_handler(event, context):
    # TODO implement
    print(event)
    bucket = "album-photo-store"
    # awsauth = ('*****', '*****')
    elasticURL = "https://search-photos-******.us-east-1.es.amazonaws.com/"
    
    
    for record in event['Records']:
        image_name = record["s3"]["object"]["key"]
        print(image_name)
        labels_res=detect_labels(image_name, bucket)
        print("labels result =====>>", labels_res)
        print ("Testing OKAY")
        
        #header={"Content-Type":"application/json"}
        query={'objectKey':image_name,'bucket':'album-photo-store','labels':labels_res}
        index_into_es('photos','photo',json.dumps(query))
        #response = requests.put(elasticURL, auth=awsauth,  data = json.dumps(query) , headers = header)
        
        print ("Something")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def index_into_es(index, type_doc, new_doc):
    awsauth = ('****', '*****')
    endpoint = 'https://search-photos-*******.us-east-1.es.amazonaws.com/{}/{}'.format(index, type_doc)
    headers = {'Content-Type':'application/json'}
    res = requests.post(endpoint, auth = awsauth, data=new_doc, headers=headers)
    print(res.content)
    print("codebuild execution successfull!!")