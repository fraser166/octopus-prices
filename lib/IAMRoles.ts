import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';

export function createIAMRoles(stack: cdk.Stack) {

    const lambdaRole = new iam.Role(stack, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      description: 'IAM Role for Lambda to access CloudWatch',
    });

    lambdaRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));

    const stateMachineRole = new iam.Role(stack, 'StateMachineRole', {
      assumedBy: new iam.ServicePrincipal('states.amazonaws.com'),
    });

    stateMachineRole.addToPolicy(new iam.PolicyStatement({
      actions: ['ses:SendEmail'],
      resources: ['*']
    }));

    return {
        lambdaRole,
        stateMachineRole
    };
}