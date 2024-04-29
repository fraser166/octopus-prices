import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {createLambdaFunctions} from "./LambdaFunctions";
import {createIAMRoles} from "./IAMRoles";
import {createDynamoDBTable} from "./DyanmoDB";
import {createCloudFrontDist} from "./CloudFront";
import {createAlertStateMachine} from "./AlertStateMachine";
import {createEventBridgeSchedule} from "./EventBridge";
import {createApiGateway} from "./APIGW";
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class OctoPricesStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const {lambdaRole, stateMachineRole} = createIAMRoles(this);
    const lambdaFunctions = createLambdaFunctions(this, lambdaRole);
    createApiGateway(this, lambdaFunctions);
    createDynamoDBTable(this, lambdaRole);
    createCloudFrontDist(this);
    const {alertStateMachine} = createAlertStateMachine(this, lambdaFunctions, stateMachineRole);
    createEventBridgeSchedule(this, alertStateMachine, lambdaFunctions)
  }
}
