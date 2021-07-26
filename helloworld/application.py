#!flask/bin/python
import json
from flask import Flask, Response ,request
from helloworld.flaskrun import flaskrun
import requests
from flask import Flask, Response, request
from flask_cors import CORS
import boto3
import datetime
from datetime import datetime

application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})
@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)
@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)
@application.route('/calc/bit', methods=['GET'])
def post_currency_bit():
    return Response(json.dumps(get_bitcoin_index()), mimetype='application/json', status=200)
def get_bitcoin_index():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(url).json()['bpi']['USD']['rate']
    return response
# return generic data
@application.route('/get_generic', methods=['GET'])
def get_generic_data():
    return Response(json.dumps(generic_data), mimetype='application/json', status=200)
# mock data
currency_rate = {
    'usd' : 3.3,
    'pound' : 4.5,
    'euro' : 4.8
}
#generic data
generic_data = [
    {
    "id":1,
    "title": "wtf",
    "body": "good will"
    },
    {
    "id":2,
    "title": "wtf2",
    "body": "good will2"
    }
   ]
   
# get example for multiplication
# test get  
# curl -i http://"localhost:8000/v1/multiply?first_num=12.1&second_num=12"
@application.route('/v1/multiply', methods=['GET', 'POST'])
def get_mult_res():
    first_num = request.args.get('first_num')
    second_num = request.args.get('second_num')
    res = float(first_num) * float(second_num) 
    return Response(json.dumps({'multiplication result': res}), mimetype='application/json', status=200)
    
# get example for multiplication
# test get  
# curl -i http://"localhost:8000/v1/calcbit?first_num=5"
@application.route('/v1/calcbit', methods=['GET', 'POST'])
def get_mult_calc():
    first_num = request.args.get('first_num')
    second_num = get_bitcoin_index().replace(",", "")
    res = round(float(first_num) * float(second_num)) 
    return Response(json.dumps({'Bit Cost result': res}), mimetype='application/json', status=200)
    
@application.route('/get_forms', methods=['GET'])
def get_frm():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # replace table scan
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), mimetype='application/json', status=200)
    
# curl -i -X POST -d'{"form_title":"form title1", "form_body":"where is it?","form_type":"finance"}' -H "Content-Type: application/json" http://localhost:8000/set_form/frm4
# curl -i -X POST -d'{"form_title":"form title1", "form_body":"where is it?","form_type":"finance"}' -H "Content-Type: application/json" http://ec2-34-207-127-59.compute-1.amazonaws.com/set_form/frm5
@application.route('/set_form/<frm_id>', methods=['POST'])
def set_doc(frm_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # get post data  
    data = request.data
    # convert the json to dictionary
    data_dict = json.loads(data)
    # retreive the parameters
    form_body = data_dict.get('form_body','default')
    form_title = data_dict.get('form_title','defualt')
    form_type = data_dict.get('form_type','defualt')
    item={
    'form_id': frm_id,
    'form_body': form_body,
    'form_title': form_title,
    'form_type':form_type
     }
     
    table.put_item(Item=item)
    return Response(json.dumps(item), mimetype='application/json', status=200)
# curl -i http://"localhost:8000/del_form?formId=fx01&formType=finance"
@application.route('/del_form', methods=['GET'])
def del_item():
    formId = request.args.get('formId')
    formType = request.args.get('formType')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    table.delete_item(
    Key={
        'form_id': formId,
        'form_type': formType
    }
    )
    # replace table scan
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), mimetype='application/json', status=200)
    
# curl -i http://"localhost:8000/get_form?formId=fx01&formType=finance"
@application.route('/get_form', methods=['GET'])
def get_item():
    formId = request.args.get('formId')
    formType = request.args.get('formType')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    resp = table.get_item(
    Key={
        'form_id': formId,
        'form_type': formType
    }
    )
    # replace table scan
    
    print(str(resp))
    return Response(json.dumps(str(resp['Item'])), mimetype='application/json', status=200) 
    
@application.route('/upload_file', methods=['GET'])
def upload_file():
    time = str(datetime.now())
    file_name = 'myUpload' + time
    bucket = 'my-upload-bucket-nivbn'
    client = boto3.client('s3')
    return client.put_object(Body='', Bucket=bucket, Key=file_name)
    
@application.route('/analyze/<bucket>/<image>', methods=['GET'])
def analyze(bucket='nivbn-my-upload-bucket-01', image='person.jpg'):
    return detect_labels(bucket, image)

# curl localhost:8000/analyze/nivbn-my-upload-bucket-01/person.jpg
def detect_labels(bucket, key, max_labels=10, min_confidence=50, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    s3 = boto3.resource('s3', region_name = 'us-east-1')

    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image

    response = rekognition.detect_labels(
        Image={
            'Bytes': img_data
        },
        MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    return json.dumps(response['Labels'])

    '''
	response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
	'''

@application.route('/comp_face/<source_image>/<target_image>', methods=['GET'])
def compare_face(source_image, target_image):
    # change region and bucket accordingly
    region = 'us-east-1'
    bucket_name = 'nivbn-my-upload-bucket-01'
	
    rekognition = boto3.client("rekognition", region)
    response = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": target_image,
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=50,
    )
    # return 0 if below similarity threshold
    return json.dumps(response['FaceMatches'] if response['FaceMatches'] != [] else [{"Similarity": 0.0}])
    
###########################################################################################################################################################
@application.route('/get_managers', methods=['GET'])
def get_mngr():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('managers')
    # replace table scan
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(resp['Items']), mimetype='application/json', status=200)
    
# curl -i http://"localhost:8000/get_manager?managerId=1"
@application.route('/get_manager', methods=['GET'])
def get_mng(managerId):
    #managerId = request.args.get('managerId')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('managers')
    resp = table.get_item(
    Key={
        'manager_id': managerId,
    }
    )
    # replace table scan
    
    
    return Response(json.dumps(resp['Item']), mimetype='application/json', status=200) 
    
@application.route('/compare_face/<source_image>', methods=['GET'])
def comp_face(source_image):
    managerId=0
    # change region and bucket accordingly
    region = 'us-east-1'
    bucket_name = 'nivbn-my-upload-bucket-01'
	
    rekognition = boto3.client("rekognition", region)
    response = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": 'niv.jpeg',
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=90,
    )
    if response['FaceMatches']:
        managerId='1'
        
    response1 = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": 'adi.jpeg',
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=90,
    )
    if response1['FaceMatches']:
        managerId='2'
    
    response1 = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": 'gal.jpeg',
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=90,
    )
    if response1['FaceMatches']:
        managerId='4'
        
    response1 = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": 'nitzan.jpeg',
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=90,
    )
    if response1['FaceMatches']:
        managerId='3'
    
    if managerId != 0:
        res = get_mng(managerId)
    else:
        res = json.dumps({'result': "no match"})
    
    # return 0 if below similarity threshold
    
    return res
    
    
    
if __name__ == '__main__':
    flaskrun(application)