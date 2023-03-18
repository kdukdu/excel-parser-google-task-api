import logging
import os

import boto3

import config

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


class LocalstackManager:
    @staticmethod
    def __get_credentials():
        """
        Get credentials from .env
        """
        credentials = {
            'aws_access_key_id': config.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': config.AWS_SECRET_ACCESS_KEY,
            'region_name': config.REGION_NAME,
            'endpoint_url': f'{config.HOSTNAME_EXTERNAL}:'
                            f'{config.PORT_EXTERNAL}'
        }
        return credentials

    def _get_client(self, client_name):
        credentials = self.__get_credentials()
        client = boto3.client(service_name=client_name,
                              **credentials)
        return client

    def _get_resource(self, resource_name):
        credentials = self.__get_credentials()
        resource = boto3.resource(service_name=resource_name,
                                  **credentials)
        return resource


class LocalstackLambda(LocalstackManager):
    def create_lambda(self, function_name):
        """
        Creates a Lambda function in LocalStack.
        To generate zip write down in the console: zip -r lambda.zip .
        """
        try:
            lambda_client = self._get_client('lambda')
            with open(config.LAMBDA_ZIP, 'rb') as f:
                zipped_code = f.read()
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.8',
                Role='role',
                Handler=function_name + '.handler',
                Code=dict(ZipFile=zipped_code),
                Timeout=30,
                Environment={
                    'Variables': {
                        'LOCALSTACK': 'True',
                        'GOOGLE_API_KEY': config.GOOGLE_API_KEY,
                        'SHEET_URL': config.SHEET_URL,
                        'REFRESH_TOKEN': config.REFRESH_TOKEN,
                        'CLIENT_ID': config.CLIENT_ID,
                        'CLIENT_SECRET': config.CLIENT_SECRET
                    }
                }
            )
        except Exception as e:
            logger.exception(e)

    def delete_lambda(self, function_name):
        """
        Deletes the specified lambda function.
        """
        try:
            lambda_client = self._get_client('lambda')
            lambda_client.delete_function(
                FunctionName=function_name
            )
            # remove the lambda function zip file
            os.remove(config.LAMBDA_ZIP)
        except Exception as e:
            logger.exception('Error while deleting lambda function')
            raise e

    def invoke_function(self, function_name):
        """
        Invokes the specified function and returns the result.
        """
        try:
            lambda_client = self._get_client('lambda')
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event'
            )
            logger.info(response)
        except Exception as e:
            logger.exception('Error while invoking function')
            raise e
