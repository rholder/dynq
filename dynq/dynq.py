## Copyright 2014-2016 Ray Holder
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import json
import os
import sys

import click

__version__ = '0.2.0-dev'

# set this environment variable to True to print debugging information for boto
DYNQ_DEBUG = os.getenv("DYNQ_DEBUG", False)


@click.command()
@click.option('--aws-access-key-id', metavar='AWS_ACCESS_KEY_ID',
              help="This is the AWS access key id, defaults to environment variable AWS_ACCESS_KEY_ID.",
              default=os.getenv('AWS_ACCESS_KEY_ID'))
@click.option('--aws-secret-access-key', metavar='AWS_SECRET_ACCESS_KEY',
              help="This is the AWS secret access key, defaults to environment variable AWS_SECRET_ACCESS_KEY.",
              default=os.getenv('AWS_SECRET_ACCESS_KEY'))
@click.option('--region', metavar='REGION',
              help='The AWS region, defaults to us-east-1',
              default='us-east-1')
@click.option('--output-json', metavar='OUTPUT_JSON', is_flag=True,
              help='Output the returned key/values as JSON',
              required=False,
              default=False)
@click.option('--table-name', metavar='TABLE_NAME',
              help='The target table to query',
              required=True)
@click.option('--query', metavar='QUERY',
              help='The query to run on the target table in raw JSON',
              required=False)
@click.option('--key-value', metavar='KEY_VALUE',
              help='The query to run on the target table of the form key=value, (converted to {key:value})',
              required=False)
@click.version_option(__version__)
def cli(aws_access_key_id, aws_secret_access_key, region, table_name, query, key_value, output_json):
    """
    dynq - 0.2.0 - a simple DynamoDB client that just works

    \b
    Examples:
      dynq --table-name deployment --key-value environment=gozer-dev
      dynq --output-json --table-name deployment --key-value environment=gozer-prod
      dynq --output-json --table-name deployment --query '{"environment":"gozer-potato"}'

    \b
    Check https://github.com/rholder/dynq for the latest release and project updates.
    """

    # TODO make this a validator callback
    if key_value is None and query is None:
        raise click.BadParameter("Missing --query or --key-value parameter")

    import dynq.boto_monkey
    import boto3

    # TODO add more validation to input key=value format
    if key_value is not None:
        kv = key_value.split('=')
        query_value = { kv[0]: { 'S': kv[1]} }
    else:
        query_value = json.loads(query)

    client = boto3.client(
        'dynamodb',
        region_name=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    run_query(client, table_name, query_value, output_json)


def run_query(client, table_name, query_value, output_json):
    """
    Run the given query against DynamoDB.

    :param connection: a DynamoDB client object to use
    :param table_name: the table name to query
    :param query_value: the query to issue to DynamoDB, should be in JSON format
    :param output_json: whether we should try to output the result in JSON instead of shell
    :return: content for the given query, if it exists
    """
    if DYNQ_DEBUG:
        boto.set_stream_logger('boto')

    response = client.get_item(TableName=table_name, Key=query_value)
    if 'Item' not in response:
        click.echo(err=True, message='No such item found for: ' + str(query_value))
        sys.exit(1)

    if output_json:
        click.echo(json.dumps(response))
    else:
        key_values = response['Item'].items()
        for field, value in key_values:
            click.echo('{}={}'.format(field, value['S']))


if __name__ == "__main__":
    cli()