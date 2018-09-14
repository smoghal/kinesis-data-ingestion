import uuid
import json
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

################ Write AVRO File
write_schema = avro.schema.Parse(json.dumps({
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
         {"name": "name", "type": "string"},
         {"name": "favorite_number", "type": ["int", "null"]},
         {"name": "favorite_color", "type": ["string", "null"]}
     ]
}))

writer = DataFileWriter(open("users.avro", "wb"), DatumWriter(), write_schema)
writer.append({"name": "Alyssa", "favorite_number": 256})
writer.append({"name": "Ben", "favorite_number": 7, "favorite_color": "red"})
writer.close()

################ Read AVRO File
read_schema = avro.schema.Parse(json.dumps({
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "first_name", "type": "string", "default": "", "aliases": ["name"]},
        {"name": "favorite_number", "type": ["int", "null"]},
        {"name": "favorite_color", "type": ["string", "null"]}
    ]
}))

# 1. open avro and extract passport + data
reader = DataFileReader(open("users.avro", "rb"), DatumReader(write_schema, read_schema))
new_schema = reader.GetMeta("avro.schema")
users = []
for user in reader:
    users.append(user)
    print(user)
reader.close()