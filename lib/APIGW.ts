import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from "aws-cdk-lib/aws-lambda";

export function createApiGateway(stack: cdk.Stack, lambdaFunctions: { [key: string]: lambda.Function }) {

    const api = new apigateway.RestApi(stack, 'OctopusAPI', {
      restApiName: 'OctopusAPI'
    });

    api.root.addResource('latest').addResource('{TYPE}')
        .addMethod('GET', new apigateway.LambdaIntegration(lambdaFunctions.getRatesFunction));

}