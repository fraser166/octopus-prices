import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';

export function createLambdaFunctions(stack: cdk.Stack, lambdaRole: iam.Role) {

    const baseLayer = new lambda.LayerVersion(stack, 'baseLayer', {
      code: lambda.Code.fromAsset('lambda/layers/base'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
      description: 'A layer to include dependencies',
    });

    const getRatesFunction = new lambda.Function(stack, 'getRatesFunction', {
          runtime: lambda.Runtime.PYTHON_3_11,
          code: lambda.Code.fromAsset('lambda/functions/get/rates'),
          handler: 'main.lambda_handler',
          role: lambdaRole
    });

    const alertFunction = new lambda.Function(stack, 'alertFunction', {
          runtime: lambda.Runtime.PYTHON_3_11,
          code: lambda.Code.fromAsset('lambda/functions/alert'),
          handler: 'main.lambda_handler',
          role: lambdaRole
    });

    const storeDailyFunction = new lambda.Function(stack, 'storeDailyFunction', {
          runtime: lambda.Runtime.PYTHON_3_11,
          code: lambda.Code.fromAsset('lambda/functions/store/daily'),
          handler: 'main.lambda_handler',
          role: lambdaRole,
          layers: [baseLayer]
    });

    const manualFunction = new lambda.Function(stack, 'manualFunction', {
          runtime: lambda.Runtime.PYTHON_3_11,
          code: lambda.Code.fromAsset('lambda/functions/store/manual'),
          handler: 'main.lambda_handler',
          role: lambdaRole,
          layers: [baseLayer]
    });

    return {
        getRatesFunction,
        alertFunction,
        storeDailyFunction,
        manualFunction
    }

}