# references for generating sample data:
#   https://github.com/lk-geimfari/mimesis/blob/master/docs/quickstart.rst
#   https://github.com/lk-geimfari/mimesis/blob/master/docs/advanced.rst

import boto3
import io
import json
import avro.schema
from avro.io import DatumWriter
from mimesis import Generic

# initialize mimesis
generic = Generic('en')

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


# create boto3 client to send data to kinesis data stream
client = boto3.client('kinesis')

for _ in range(0, 10):
    # create a dict to store randomly generated user data
    user = {}
    user['uuid'] = generic.cryptographic.uuid()
    user['firstName'] = generic.person.name()
    user['lastName'] = generic.person.surname()
    user['age'] = generic.person.age()
    user['gender'] = generic.person.gender()
    user['email'] = generic.person.email()
    user['address'] = generic.address.address()
    #user['hash'] = generic.cryptographic.hash()
    print(json.dumps(user))

    # avro init
    avro_writer = DatumWriter(avro_schema)
    bytes_writer = io.BytesIO()
    avro_binary_encoder = avro.io.BinaryEncoder(bytes_writer)

    # write binary data
    avro_writer.write(user, avro_binary_encoder)
    raw_bytes = bytes_writer.getvalue()

    # put data into kensis data stream
    response = client.put_record(
        StreamName='SourceStream',
        Data=raw_bytes,
        PartitionKey=user['uuid']
    )
    print(response)