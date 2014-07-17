import atexit
import json
import os
import sys
import tempfile
import zipfile

import boto
import click
from boto.dynamodb2.table import Table

__version__ = '0.1.0'

DYNQ_DEBUG = os.getenv("DYNQ_DEBUG", False)

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
        # default is inside the egg now, so load from there
        egg_path = os.path.dirname(__file__)
        with zipfile.ZipFile(egg_path, 'r') as egg_file:
            return json.load(egg_file.open('boto/endpoints.json', 'r'))
    else:
        # it was overridden
        with open(path, 'r') as endpoints_file:
            return json.load(endpoints_file)

# monkeypatch the original load to handle being inside of an eggsecutable
boto.regioninfo.load_endpoint_json = load_endpoint_json


def patch_ca_certs():
    """
    Boto needs an actual file path for the cacerts.txt so we extract it from
    inside the egg. If it's been overridden by Boto's 'ca_certificates_file'
    setting then just skip this patch.
    """

    # skip this if user overrides ca_certificates_file
    detected_ca = boto.config.get('Boto', 'ca_certificates_file')
    if detected_ca is None:
        egg_path = os.path.dirname(__file__)
        with zipfile.ZipFile(egg_path, 'r') as egg_file:
            cert_file = tempfile.NamedTemporaryFile(prefix='cacerts', delete=False)
            cert_file.write(egg_file.open('boto/cacerts/cacerts.txt').read())
            cert_file.close()

            if not boto.config.has_section('Boto'):
                boto.config.add_section('Boto')
            boto.config.set('Boto', 'ca_certificates_file', cert_file.name)
            atexit.register(clean_ca_certs, cert_file.name)


def clean_ca_certs(ca_cert_filename):
    os.remove(ca_cert_filename)

@click.command()
@click.option('--aws-access-key-id', metavar='AWS_ACCESS_KEY_ID',
              help="This is the AWS access key id.",
              default=os.getenv('AWS_ACCESS_KEY_ID'))
@click.option('--aws-secret-access-key', metavar='AWS_SECRET_ACCESS_KEY',
              help="This is the AWS secret access key.",
              default=os.getenv('AWS_SECRET_ACCESS_KEY'))
@click.option('--region', metavar='REGION',
              help='The AWS region (e.g. us-east-1).',
              default='us-east-1')
@click.option('--table-name', metavar='TABLE_NAME',
              help='The target table to query.',
              required=True)
@click.option('--query', metavar='QUERY',
              help='The query to run on the target table.',
              required=False)
@click.option('--key-value', metavar='KEY_VALUE',
              help='The query to run on the target table of the form key=value, (converted to {key:value}).',
              required=False)
@click.option('--output-json', metavar='OUTPUT_JSON', is_flag=True,
              help='Output the returned key/values as JSON.',
              required=False,
              default=False)
@click.option('--verbose', metavar='verbose', is_flag=True,
              help="Print the version and header info.", default=False)
@click.version_option(__version__)
def main(aws_access_key_id, aws_secret_access_key, region, table_name, query, key_value, verbose, output_json):
    if key_value is None and query is None:
        raise click.ClickException("Missing --query or --key-value parameter")

    if verbose:
        click.echo('dynq - ' + __version__ + " - A simple DynamoDB client that just works.")
        click.echo('boto ' + boto.__version__)
        click.echo()

    patch_ca_certs()
    connection = boto.dynamodb2.connect_to_region(
        region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    if key_value is not None:
        kv = key_value.split('=')
        query_value = {kv[0]: kv[1]}
    else:
        query_value = query

    try:
        run_query(connection, table_name, query_value, output_json)
        return 0
    except:
        click.echo(sys.exc_info()[1])
        return 1


def run_query(connection, table_name, query_value, output_json):
    if DYNQ_DEBUG:
        boto.set_stream_logger('boto')

    items = Table(table_name, connection=connection).get_item(**query_value)
    if output_json:
        click.echo(json.dumps(items._data))
    else:
        for field, value in items.items():
            click.echo(field + "=" + value)


if __name__ == "__main__":
    # TODO why are these error codes broken?
    sys.exit(main())

