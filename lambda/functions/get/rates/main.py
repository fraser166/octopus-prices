import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name="eu-west-2")
table = dynamodb.Table("OctPrices")


def lambda_handler(event, context):
    rate_type = event["pathParameters"]["TYPE"]

    data = fetch_values(rate_type)
    flex_data = fetch_values(rate_type + 'Flex')
    cap_data = fetch_values(rate_type + 'Cap')
    # fix_data = getFixData(rate_type, start, end)

    result = {
        "tracker": [create_entry(i) for i in data["Items"]],
        "flex": [create_entry(i) for i in flex_data["Items"]],
        "cap": [create_entry(i) for i in cap_data["Items"]],
        # "fixed": [create_entry(i) for i in fix_data["Items"]]
    }

    response = {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }

    return response


def create_entry(item):
    return {
        "start": item["Date"],
        "end": item.get("End", None),
        "cost": item["Value"]
    }


def fetch_values(rate_type):
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() + timedelta(weeks=-12)).strftime("%Y-%m-%d")

    return table.query(
        Select='SPECIFIC_ATTRIBUTES',
        ProjectionExpression='#d,#v',
        ExpressionAttributeNames={'#d': 'Date', '#v': 'Value'},
        KeyConditionExpression=Key('Type').eq(rate_type)  # & Key('Date').between(start, end)
    )
