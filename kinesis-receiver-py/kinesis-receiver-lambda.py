"""
This is the receiver lambda that receives forwarded records and simply
dumps the output
"""
from aws_kinesis_agg.deaggregator import deaggregate_records
import base64
import six
import json
import io
import avro.schema
import avro.io

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
    print(user)

def lambda_handler(event, context):
    """A Python AWS Lambda function to process Kinesis aggregated
    records in a bulk fashion."""
    
    raw_kinesis_records = event['Records']
    
    # Deaggregate all records in one call
    user_records = deaggregate_records(raw_kinesis_records)
    
    # Iterate through deaggregated records
    for record in user_records:
        
        # Kinesis data in Python Lambdas is base64 encoded
        payload = base64.b64decode(record['kinesis']['data'])

        # dump the payload assuming it is string.  If payload contains
        # AVRO binary data, print statement below will show binary characters
        # refer to avro_decode() method to see how record is decoded
        #six.print_('%s' % payload)

        # decode the binary AVRO data and show records
        avro_decode(payload)

        # This is where your custom code will go

    
    resp = 'Successfully processed {} records.'.format(len(user_records))
    print(resp)

    return resp
