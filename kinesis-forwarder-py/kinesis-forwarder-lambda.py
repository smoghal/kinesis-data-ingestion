from aws_kinesis_agg.deaggregator import deaggregate_records
import base64
import six
import boto3
import json
import os
import io
import avro.schema
import avro.io


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

    ## grab the partition key from payload
    # deagg_rec = json.loads(payload)
    # pkey = deagg_rec['uuid']
    # response = client.put_record(
    #     StreamName=forward_to_stream_name,
    #     Data=payload,
    #     PartitionKey=pkey
    # )

    # uuid is the partition key, so lets grab it from the payload
    pkey = avro_decode(payload)

    # forward the payload to a kinesis stream in different aws account
    response = client.put_record(
        StreamName=forward_to_stream_name,
        Data=payload,
        PartitionKey=pkey
    )
    print(response)

    return

def avro_decode(payload):
    """Convert binary payload into AVRO format given the AVRO schema
    """

    # setup AVRO schema
    avro_schema = avro.schema.Parse(json.dumps({
        "namespace": "example.avro",
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "uuid", "type": "string"},
            {"name": "firstName", "type": "string"},
            {"name": "lastName", "type": "string"},
            {"name": "age", "type": "int"},
            {"name": "gender", "type": "string"},
            {"name": "email", "type": "string"},
            {"name": "address", "type": "string"}
        ]
    }))

    # avro init
    bytes_reader = io.BytesIO(payload)
    avro_binary_decoder = avro.io.BinaryDecoder(bytes_reader)
    reader = avro.io.DatumReader(avro_schema)

    user = reader.read(avro_binary_decoder)
    return user['uuid']


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

        # dump the payload assuming it is string.  If payload contains
        # AVRO binary data, print statement below will show binary characters
        # refer to avro_decode() method to see how record is decoded
        #six.print_('%s' % payload)

        # Forward the decoded+deaggregated record to target kinesis stream
        check_and_forward(payload)
    
    resp = 'Successfully processed {} records.'.format(len(user_records))
    print(resp)

    return resp
