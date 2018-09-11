# Overview
Amazon Kinesis is widely used for data ingestion.  This project aims at demonstrating one specific data ingestion pattern, i.e. forwarder pattern.  Using a AWS Lambda function and Kinesis stream as event trigger, it becomes possible to consume the data and forward (in real time) to a different stream for further processing.  This lambda can further enrich or transform data as it forwards it to another stream.

Note: It is also possible to permanently save the original data on S3 for example using Amazon Kinesis Firehose.  This pattern will be discussed in a separate project.

Overall architecture of the forwarder pattern is shown below.

![architecture][arch-v1]

There are three main components of this architecture:
- The producer/client which uses KPL (Kinesis Producer Library)
- The forwarder Lambda which receives, deaggregates, enriches data from `Source Stream` and fowrads it to the `Target Stream` (receiver stream).  Note: the enrichment is not shown in the sample code.
- And finally, the receiver lambda that receives the data from target stream and processes it.  Note: receiver lambda only displays the read read in CloudWatch logs at the moment.

# Producer

# Forwarder

# Recevier


[arch-v1]: Architecture_v1.png

