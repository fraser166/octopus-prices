import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';

export function createDynamoDBTable(stack: cdk.Stack, lambdaRole: iam.Role) {

    const table = new dynamodb.Table(stack, 'MyTable', {
        partitionKey: { name: 'Type', type: dynamodb.AttributeType.STRING },
        sortKey: { name: 'Date', type: dynamodb.AttributeType.STRING },
        tableName: 'OctPrices',
        timeToLiveAttribute: 'expire',
        billingMode: dynamodb.BillingMode.PROVISIONED,
        readCapacity: 1,
        writeCapacity: 1,
    });

     const readScaling = table.autoScaleReadCapacity({
        minCapacity: 1,
        maxCapacity: 10
    });

    readScaling.scaleOnUtilization({
        targetUtilizationPercent: 70
    });

    const writeScaling = table.autoScaleWriteCapacity({
        minCapacity: 1,
        maxCapacity: 10
    });

    writeScaling.scaleOnUtilization({
        targetUtilizationPercent: 70
    });

    table.grantReadWriteData(lambdaRole);
}