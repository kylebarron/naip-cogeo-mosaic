"""
dynamodb_upload.py: Upload MosaicJSON to DynamoDB
"""

import hashlib
import json
from decimal import Decimal

import boto3
import click

from cogeo_mosaic import version as mosaic_version


@click.command()
@click.option(
    '-n',
    '--table-name',
    type=str,
    default=None,
    help='Name of dynamodb table. If None will be created based on mosaic id.')
@click.option(
    '--region',
    type=str,
    help='AWS region',
    default='us-west-2',
    show_default=True)
@click.argument('input_path', nargs=1, type=click.Path(exists=True))
def main(table_name, region, input_path):
    """Upload MosaicJSON quadkey-assets key-value pairs to DynamoDB

    This finds the "MosaicID" using an SHA224 hash in the same method as
    cogeo-mosaic-tiler. It then creates a new DynamoDB table with that MosaicID,
    and uploads the quadkey-assets key-value pairs to that DynamoDB table.

    All fields of the MosaicJSON other than the "tiles" key is uploaded as an
    object with `quadkey` value `-1`. Otherwise, each record is a mapping from
    `quadkey` to asset urls.
    """
    client = boto3.resource('dynamodb', region_name=region)

    with open(input_path) as f:
        mosaic = json.load(f)

    if table_name is None:
        table_name = get_hash(body=mosaic, version=mosaic_version)
    print(f'table_name: {table_name}')

    create_table(client, table_name)
    items = create_items(mosaic)
    upload_items(client, items, table_name)


def create_table(client, mosaicid, billing_mode='PAY_PER_REQUEST'):
    attr_defs = [{'AttributeName': 'quadkey', 'AttributeType': 'S'}]
    key_schema = [{'AttributeName': 'quadkey', 'KeyType': 'HASH'}]

    # Note: errors if table already exists
    try:
        response = client.create_table(
            AttributeDefinitions=attr_defs,
            TableName=mosaicid,
            KeySchema=key_schema,
            BillingMode=billing_mode)
        print('creating table')

        # If I put this outside the try/except block, could wait forever if
        # unable to create table
        client.Table(mosaicid).wait_until_exists()
    except boto3.client('dynamodb').exceptions.ResourceInUseException:
        print('unable to create table, may already exist')


def upload_items(client, items, mosaicid):
    table = client.Table(mosaicid)
    with table.batch_writer() as batch:
        print(f'Uploading items to table {mosaicid}')
        counter = 0
        for item in items:
            if counter % 1000 == 0:
                print(f'Uploading #{counter}')

            batch.put_item(item)
            counter += 1


def create_items(mosaic):
    items = []
    # Create one metadata item with quadkey=-1
    meta = {k: v for k, v in mosaic.items() if k != 'tiles'}

    # Convert float to decimal
    # https://blog.ruanbekker.com/blog/2019/02/05/convert-float-to-decimal-data-types-for-boto3-dynamodb-using-python/
    meta = json.loads(json.dumps(meta), parse_float=Decimal)

    # NOTE: quadkey is a string type
    meta['quadkey'] = '-1'
    items.append(meta)

    for quadkey, assets in mosaic['tiles'].items():
        item = {'quadkey': quadkey, 'assets': assets}
        items.append(item)

    return items


def get_hash(**kwargs) -> str:
    """Create hash from a dict."""
    return hashlib.sha224(
        json.dumps(kwargs, sort_keys=True, default=str).encode()).hexdigest()


if __name__ == '__main__':
    main()
