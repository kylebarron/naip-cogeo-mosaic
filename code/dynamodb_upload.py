"""
dynamodb_upload.py: Upload MosaicJSON tiles key to DynamoDB
"""

import hashlib
import json

import boto3
import click

from cogeo_mosaic import version as mosaic_version


@click.command()
@click.option(
    '--region',
    type=str,
    help='AWS region',
    default='us-west-2',
    show_default=True)
@click.argument('input_path', nargs=1, type=click.Path(exists=True))
def main(input_path, region):
    """Upload MosaicJSON quadkey-assets key-value pairs to DynamoDB

    This finds the "MosaicID" using an SHA224 hash in the same method as
    cogeo-mosaic-tiler. It then creates a new DynamoDB table with that MosaicID,
    and uploads the quadkey-assets key-value pairs to that DynamoDB table.
    """
    client = boto3.resource('dynamodb', region_name=region)

    with open(input_path) as f:
        mosaic = json.load(f)

    mosaicid = get_hash(body=mosaic, version=mosaic_version)
    print(f'mosaicid: {mosaicid}')

    create_table(client, mosaicid)
    items = create_items(mosaic)
    upload_items(items)


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
        for item in items:
            batch.put_item(item)


def create_items(mosaic):
    items = []
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
