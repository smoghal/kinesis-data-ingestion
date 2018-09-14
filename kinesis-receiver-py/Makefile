AWS_PROFILE=receiver-profile
AWS_REGION=us-east-1
AWS_CLI_BIN="aws"
PIP3_BIN=pip3

# cfn template config
stack_name=receiver-sandbox
sam_template=kinesis-receiver.yaml
cfn_template=kinesis-receiver-output.yaml

# cfn template parameters
artifacts_s3_bucket=<YOUR_BUCKET_NAME>
trust_account=<TRUSTED_AWS_ACCOUNT_WHERE_FORWARDER_LAMBDA_RUNS>
kinesis_stream_name=ReceiverStream
kinesis_stream_env_tag=Sandbox
kinesis_stream_retention_hrs=168
kinesis_stream_shard_count=1
event_source_batch_size=5


# kinesis forwarder lambda config
build_time=$(shell cat /tmp/make.build-time)
lambda_name=kinesis-receiver-lambda
lambda_file_name=$(lambda_name)-$(build_time)
lambda_zip=dist/$(lambda_file_name).zip
lambda_export=lambda_function.lambda_handler

.PHONY: all
all: clean build-time compile package deploy

build-time:
	@date +"%m-%d-%Y-%H-%M-%S" > /tmp/make.build-time

clean:
	rm -rf build/* && rm -rf dist/* && rm -f /tmp/make.*

compile:
	echo "starting build"
	cp kinesis*py build
	cp requirements.txt build
	cp setup.cfg build
	$(PIP3_BIN) install -r requirements.txt --target build --no-cache-dir --find-links file:///tmp/packages

package:
	( cd build; zip -0r ../$(lambda_zip) . )

copy-to-s3:
	$(AWS_CLI_BIN) s3 cp $(lambda_zip) s3://$(artifacts_s3_bucket)/ --profile $(AWS_PROFILE)

validate-cfn-template:
	$(AWS_CLI_BIN) cloudformation validate-template \
		--template-body file://$(sam_template)

package-cfn-template:
	$(AWS_CLI_BIN) cloudformation package \
		--template-file $(sam_template) \
		--output-template-file $(cfn_template) \
		--s3-bucket $(artifacts_s3_bucket) \
		--region $(AWS_REGION) \
		--profile $(AWS_PROFILE)

deploy-cfn-template:
	$(AWS_CLI_BIN) cloudformation deploy \
		--template-file $(cfn_template) \
		--stack-name $(stack_name) \
		--parameter-overrides \
			ArtificatS3Bucket=$(artifacts_s3_bucket) \
			LambdaZipFile=$(lambda_file_name).zip \
			TrustAccount=$(trust_account) \
			KinesisStreamName=$(kinesis_stream_name) \
			KinesisStreamRetentionHours=$(kinesis_stream_retention_hrs) \
			KinesisStreamShardCount=$(kinesis_stream_shard_count) \
			KinesisStreamEnv=$(kinesis_stream_env_tag) \
			EventSourceBatchSize=$(event_source_batch_size) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset \
		--region $(AWS_REGION) \
		--profile $(AWS_PROFILE)

update-lambda-test:
	$(AWS_CLI_BIN) lambda update-function-code \
        --function-name $(lambda_name) \
        --zip-file fileb://$(lambda_zip) \
		--region $(AWS_REGION) \
        --profile $(AWS_PROFILE)

deploy: copy-to-s3 validate-cfn-template package-cfn-template deploy-cfn-template

# some tests for build-time.  We want to make sure that 'build-time' variable
# contains a constant timestamp value.
# Execute 'make build-time-test' to test
build-time-test: clean build-time build-time-1 build-time-2
build-time-1:
	@echo $(build_time)
	sleep 4s
build-time-2:
	@echo $(build_time)
