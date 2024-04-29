import boto3
import requests
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name="eu-west-2")
table = dynamodb.Table("OctPrices")

endpoints = {
    'ERATE': 'https://api.octopus.energy/v1/products/SILVER-23-12-06/electricity-tariffs/E-1R-SILVER-23-12-06-N/standard-unit-rates/',
    'ESTAND': 'https://api.octopus.energy/v1/products/SILVER-23-12-06/electricity-tariffs/E-1R-SILVER-23-12-06-N/standing-charges/',
    'GRATE': 'https://api.octopus.energy/v1/products/SILVER-23-12-06/gas-tariffs/G-1R-SILVER-23-12-06-N/standard-unit-rates/',
    'GSTAND': 'https://api.octopus.energy/v1/products/SILVER-23-12-06/gas-tariffs/G-1R-SILVER-23-12-06-N/standing-charges/'
}

flex_endpoints = {
    'ERATEFlex': 'https://api.octopus.energy/v1/products/VAR-22-11-01/electricity-tariffs/E-1R-VAR-22-11-01-N/standard-unit-rates/',
    'ESTANDFlex': 'https://api.octopus.energy/v1/products/VAR-22-11-01/electricity-tariffs/E-1R-VAR-22-11-01-N/standing-charges/',
    'GRATEFlex': 'https://api.octopus.energy/v1/products/VAR-22-11-01/gas-tariffs/G-1R-VAR-22-11-01-N/standard-unit-rates/',
    'GSTANDFlex': 'https://api.octopus.energy/v1/products/VAR-22-11-01/gas-tariffs/G-1R-VAR-22-11-01-N/standing-charges/'
}

TTL = int(datetime.timestamp(datetime.now() + timedelta(weeks=12)))
TTL_SHORT = int(datetime.timestamp(datetime.now() + timedelta(days=2)))


def lambda_handler(event, context):
    for rateType in list(endpoints.keys()):
        r = requests.get(endpoints[rateType]).json()
        results = r["results"]
        putEntries(results, rateType, 0)
        if r["count"] > 1:
            putEntries(results, rateType, 1)

    for rateType in list(flex_endpoints.keys()):
        r = requests.get(flex_endpoints[rateType]).json()
        results = [i for i in r["results"] if i["payment_method"] == "DIRECT_DEBIT"]
        putFlex(results, rateType, 0)
        if r["count"] > 1:
            putFlex(results, rateType, 1)

    return {
        'statusCode': 200,
        'body': 'Success'
    }


def putEntries(r, rateType, i):
    itemDate = formatDate(r[i]["valid_from"])
    itemEndDate = formatDate(r[i]["valid_to"])
    table.put_item(
        TableName='OctPrices',
        Item={
            'Date': itemDate,
            'End': itemEndDate,
            'Type': rateType,
            'Value': str(r[i]["value_inc_vat"]),
            'expire': TTL
        }
    )


def putFlex(r, rateType, i):
    itemDate = formatDate(r[i]["valid_from"])
    itemEndDate = formatDate(r[i]["valid_to"])
    table.put_item(
        TableName='OctPrices',
        Item={
            'Date': itemDate,
            'End': itemEndDate,
            'Type': rateType,
            'Value': str(r[i]["value_inc_vat"]),
            'expire': TTL
        }
    )


def formatDate(date):
    if date is None:
        return None
    return (datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=3)).strftime("%Y-%m-%d")
