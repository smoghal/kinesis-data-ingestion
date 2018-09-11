"""
This is the receiver lambda that receives forwarded records and simply
dumps the output
"""
from aws_kinesis_agg.deaggregator import deaggregate_records
import base64
import six
import json

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

        # Just display the payload and return.  This is where
        # your custom code will go
        six.print_('%s' % payload)

    
    resp = 'Successfully processed {} records.'.format(len(user_records))
    print(resp)

    return resp
