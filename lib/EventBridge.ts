import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';

export function createEventBridgeSchedule(stack: cdk.Stack, alertStateMachine: sfn.StateMachine, lambdaFunctions: { [key: string]: lambda.Function }) {

    const alertRule = new events.Rule(stack, 'alertRule', {
      schedule: events.Schedule.cron({ minute: '15', hour: '18' }), // 18:15 UTC
    });
    alertRule.addTarget(new targets.SfnStateMachine(alertStateMachine));

    const getRatesRule = new events.Rule(stack, 'getRatesRule', {
      schedule: events.Schedule.rate(cdk.Duration.hours(2)),
    });
    getRatesRule.addTarget(new targets.LambdaFunction(lambdaFunctions.storeDailyFunction));
}