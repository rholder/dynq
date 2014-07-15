import boto
import click
import json
import os
import sys
import zipfile

from boto.dynamodb2.table import Table

__version__ = '0.1.0'

# this is the default calculated endpoint path from boto
DEFAULT_ENDPOINTS_PATH = os.path.join(os.path.dirname(boto.__file__), 'endpoints.json')

def load_endpoint_json(path):
    """
    Loads a given JSON file & returns it. Handle being inside of an egg.

    :param path: The path to the JSON file
    :type path: string

    :returns: The loaded data
    """
    if DEFAULT_ENDPOINTS_PATH == path:
        egg_path = os.path.dirname(__file__)
        with zipfile.ZipFile(egg_path, 'r') as egg_file:
            return json.load(egg_file.open('boto/endpoints.json', 'r'))
    else:
        with open(path, 'r') as endpoints_file:
            return json.load(endpoints_file)

# monkeypatch the original load to account for loading inside of an eggsecutable
boto.regioninfo.load_endpoint_json = load_endpoint_json


@click.command()
@click.option('--aws-access-key-id', metavar='AWS_ACCESS_KEY_ID',
              help="This is the AWS access key id.",
              default=os.getenv('AWS_ACCESS_KEY_ID'))
@click.option('--aws-secret-access-key', metavar='AWS_SECRET_ACCESS_KEY',
              help="This is the AWS secret access key.",
              default=os.getenv('AWS_SECRET_ACCESS_KEY'))
@click.option('--region', metavar='REGION',
              help='The AWS region (e.g. us-east-1).', default='us-east-1')
@click.option('--table-name', metavar='TABLE_NAME',
              help='The target table to query.', required=True)
@click.option('--query', metavar='QUERY',
              help='The query to run on the target table.', required=True)
@click.option('--quiet', metavar='QUIET', is_flag=True,
              help="Don't print the version and header info.", default=False)
@click.version_option(__version__)
def main(aws_access_key_id, aws_secret_access_key, region, table_name, query, quiet):
    if not quiet:
        click.echo('Boto ' + boto.__version__)
        click.echo("{} {} {} {} {}".format(aws_access_key_id, aws_secret_access_key, region, table_name, query))

    conn = boto.dynamodb2.connect_to_region(
        region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    items = Table(table_name, connection=conn).get_item(**json.loads(query))

    for field, value in items.items():
        click.echo(field + ":" + value)


def table_key():
    """Return a single result for the given table and key"""
    pass


def query():
    pass

if __name__ == "__main__":
    sys.exit(main())

