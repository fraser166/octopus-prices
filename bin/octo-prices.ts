#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { OctoPricesStack } from '../lib/octo-prices-stack';

const octoPrices = new cdk.App();
new OctoPricesStack(octoPrices, 'OctoPricesStack', {

});