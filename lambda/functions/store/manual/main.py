import boto3
from datetime import datetime, timedelta, date

dynamodb = boto3.resource('dynamodb', region_name="eu-west-2")
table = dynamodb.Table("OctPrices")

manual = {
    'ERATE': '27.73',
    'ESTAND': '60.02',
    'GRATE': '6.99',
    'GSTAND': '27.47',
    'Start': '2023-07-01',
    'End': '2023-08-17',
    'Tariff': 'Test'
}


def lambda_handler(event, context):
    rate_types = ["ERATE", "GRATE", "ESTAND", "GSTAND"]
    for rate_type in rate_types:
        table.put_item(
            TableName='OctPrices',
            Item={
                'Date': manual["Start"],
                'End': manual["End"],
                'Type': rate_type + manual["Tariff"],
                'Value': manual[rate_type],
                'expire': int(datetime.timestamp(datetime.now() + timedelta(days=1)))
            }
        )
    return
