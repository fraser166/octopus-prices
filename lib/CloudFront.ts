import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';

export function createCloudFrontDist(stack: cdk.Stack) {

    const bucket = new s3.Bucket(stack, 'frontendBucket', {
      bucketName: 'octopus-fraser-miller',
    });

    const oai = new cloudfront.OriginAccessIdentity(stack, 'OAI', {
      comment: 'OAI for octopus-fraser-miller'
    });

    bucket.grantRead(oai);

    const certificateArn = 'arn:aws:acm:us-east-1:730335636950:certificate/d782b0fb-9b86-4ea7-b046-d30c083e8613';
    const certificate = acm.Certificate.fromCertificateArn(stack, 'SiteCertificate', certificateArn);

    const distribution = new cloudfront.Distribution(stack, 'frontendDistribution', {
      defaultBehavior: { origin: new origins.S3Origin(bucket, { originAccessIdentity: oai }) },
      domainNames: ['octopus.frmtechnology.com'],
      certificate: certificate,
      priceClass: cloudfront.PriceClass.PRICE_CLASS_ALL,
      defaultRootObject: 'index.html'
    });

    new s3deploy.BucketDeployment(stack, 'deployFrontend', {
      sources: [s3deploy.Source.asset('buckets/frontend')],
      destinationBucket: bucket,
      distribution: distribution,
      distributionPaths: ['/*'], // Invalidate the CloudFront cache
    });

    new cdk.CfnOutput(stack, 'DistributionDomainName', {
      value: distribution.distributionDomainName,
    });
}