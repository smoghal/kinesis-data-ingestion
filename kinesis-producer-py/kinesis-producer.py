# references for generating sample data:
#   https://github.com/lk-geimfari/mimesis/blob/master/docs/quickstart.rst
#   https://github.com/lk-geimfari/mimesis/blob/master/docs/advanced.rst

import boto3
import json

from mimesis import Generic
generic = Generic('en')

# create boto3 client to send data to kinesis data stream
client = boto3.client('kinesis')

for _ in range(0, 10):
    # create a dict to store randomly generated user data
    user = {}
    user['firstName'] = generic.person.name()
    user['lastName'] = generic.person.surname()
    user['age'] = generic.person.age()
    user['gender'] = generic.person.gender()
    user['email'] = generic.person.email()
    user['address'] = generic.address.address()
    user['uuid'] = generic.cryptographic.uuid()
    #user['hash'] = generic.cryptographic.hash()
    print(json.dumps(user))

    # put data into kensis data stream
    response = client.put_record(
        StreamName='SourceStream',
        Data=json.dumps(user),
        PartitionKey=user['uuid']
    )
    print(response)