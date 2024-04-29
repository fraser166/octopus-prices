import * as cdk from 'aws-cdk-lib';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as iam from "aws-cdk-lib/aws-iam";

export function createAlertStateMachine(stack: cdk.Stack, lambdaFunctions: { [key: string]: lambda.Function }, stateMachineRole: iam.Role) {

    lambdaFunctions.storeDailyFunction.grantInvoke(stateMachineRole);
    lambdaFunctions.alertFunction.grantInvoke(stateMachineRole);

    const updateRates = new tasks.LambdaInvoke(stack, 'UpdateRates', {
      lambdaFunction: lambdaFunctions.storeDailyFunction,
      outputPath: '$.Payload',
    });

    const checkForAlerts = new tasks.LambdaInvoke(stack, 'CheckAlerts', {
      lambdaFunction: lambdaFunctions.alertFunction,
      outputPath: '$.Payload',
    }).addCatch(new sfn.Wait(stack, 'Wait30', {
      time: sfn.WaitTime.duration(cdk.Duration.minutes(30))
    }).next(updateRates), {
      errors: ['States.TaskFailed', 'KeyError']
    });

    const emailAddresses = require('./emails.json')
    const sendEmail = new tasks.CallAwsService(stack, 'SendEmail', {
        iamResources: ['*'],
        service: 'ses',
      action: 'sendEmail',
      parameters: {
        Destination: {
          ToAddresses: emailAddresses
        },
        Message: {
          Body: {
            Html: {
              Data: sfn.JsonPath.stringAt('$.email')
            }
          },
          Subject: {
            Data: 'Energy Alert'
          }
        },
        Source: 'octopus@frmtechnology.com'
      },
      resultPath: sfn.JsonPath.DISCARD
    });

    const choice = new sfn.Choice(stack, 'Choice')
      .when(sfn.Condition.isPresent('$.email'), sendEmail)
      .otherwise(new sfn.Pass(stack, 'Pass'));

    const chain = sfn.Chain.start(updateRates)
      .next(checkForAlerts)
      .next(choice);

    const alertStateMachine = new sfn.StateMachine(stack, 'AlertStateMachine', {
        definitionBody: sfn.DefinitionBody.fromChainable(chain),
        timeout: cdk.Duration.hours(3),
        role: stateMachineRole
    });

    return {
        alertStateMachine
    };
}