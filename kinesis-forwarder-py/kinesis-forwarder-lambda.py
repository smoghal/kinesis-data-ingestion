from aws_kinesis_agg.deaggregator import deaggregate_records
import base64
import six
import boto3
import json
import os

kinesis_cross_account_role = ''
forward_to_stream_name = ''

def sts_assume_role():
    global kinesis_cross_account_role

    sts_connection = boto3.client('sts')
    assume_role_object = sts_connection.assume_role(
        RoleArn=kinesis_cross_account_role,
        RoleSessionName='KinesisTargetSession1',
        DurationSeconds=3600)
    credentials = assume_role_object['Credentials']

    return credentials

def get_boto3_session():
    tmp_credentials = sts_assume_role()

    tmp_access_key = tmp_credentials['AccessKeyId']
    tmp_secret_key = tmp_credentials['SecretAccessKey']
    security_token = tmp_credentials['SessionToken']

    boto3_session = boto3.Session(
        aws_access_key_id=tmp_access_key,
        aws_secret_access_key=tmp_secret_key,
        aws_session_token=security_token
    )
    return boto3_session

def check_and_forward(payload):
    """Check if incoming payload/record is complete and forward deaggregated
    record to the configured destination Kinesis stream."""
    global forward_to_stream_name

    # use a kinesis client (which does STSAssumeRole in another account)
    sess = get_boto3_session()
    client = sess.client(service_name='kinesis')

    # grab the partition key from payload
    deagg_rec = json.loads(payload)
    pkey = deagg_rec['uuid']

    response = client.put_record(
        StreamName=forward_to_stream_name,
        Data=payload,
        PartitionKey=pkey
    )
    print(response)

    return

def lambda_handler(event, context):
    """A Python AWS Lambda function to process Kinesis aggregated
    records in a bulk fashion."""
    global kinesis_cross_account_role
    global forward_to_stream_name

    ## pre-flight checks
    try:
        if not os.environ['cross_account_role']:
            errorMessage = 'cross_account_role is not defined in lambda environment'
            raise Exception(errorMessage)
        if not os.environ['forward_to_stream_name']:
            errorMessage = 'forward_to_stream_name is not defined in lambda environment'
            raise Exception(errorMessage)
    except Exception as details:
        errorMessage = 'error while accessing environment variables for lambda', details
        raise Exception(errorMessage)

    # initialize
    kinesis_cross_account_role = os.environ['cross_account_role']
    forward_to_stream_name = os.environ['forward_to_stream_name']
    raw_kinesis_records = event['Records']
    
    # Deaggregate all records in one call
    user_records = deaggregate_records(raw_kinesis_records)
    
    # Iterate through deaggregated records
    for record in user_records:
        
        # For Future Use - resharding!
        # 1. get record partition key and store
        # 2. generate a random explicit hash key
        # 3. create a new AggRecord from existing 'record' but
        #    but add the partition and explicit hash key from #1 and #2
        # 4. forward the record to another kinesis stream

        
        # Kinesis data in Python Lambdas is base64 encoded
        payload = base64.b64decode(record['kinesis']['data'])
        six.print_('%s' % payload)

        # Forward the decoded+deaggregated record to target kinesis stream
        check_and_forward(payload)
    
    resp = 'Successfully processed {} records.'.format(len(user_records))
    print(resp)

    return resp
