---
title : "Running in Your Own Account"
weight : 12
---

:::alert{header="Important" type="warning"}
To proceed with this section, you need your own AWS account.
:::

We provide AWS CloudFormation templates for each AWS region to prepare for the workshop.

When you deploy the template, a VS Code server instance will run in your account. You can connect to the server and perform this AWS Entity Resolution exercise.

## Deploy CloudFormation Stack

1. Select a region in the tabs below and click the **Launch** button to access the AWS CloudFormation console. (You may be required to log in to your AWS account.)

::::tabs{variant="container"}
:::tab{id="us-east-2" label="Ohio"}

:button[Launch]{variant="primary" href="https://us-east-2.console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-cmh-8d6e9c21a4dec77d.s3.us-east-2.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-cmh-8d6e9c21a4dec77d/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="us-east-1" label="N. Virginia"}

:button[Launch]{variant="primary" href="https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-iad-ed304a55c2ca1aee.s3.us-east-1.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-iad-ed304a55c2ca1aee/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="us-west-2" label="Oregon"}

:button[Launch]{variant="primary" href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-pdx-f3b3f9f1a7d6a3d0.s3.us-west-2.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-pdx-f3b3f9f1a7d6a3d0/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="ap-northeast-2" label="Seoul"}

:button[Launch]{variant="primary" href="https://ap-northeast-2.console.aws.amazon.com/cloudformation/home?region=ap-northeast-2#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-icn-ced060f0d38bc0b0.s3.ap-northeast-2.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-icn-ced060f0d38bc0b0/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="ap-southeast-1" label="Singapore"}

:button[Launch]{variant="primary" href="https://ap-southeast-1.console.aws.amazon.com/cloudformation/home?region=ap-southeast-1#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-sin-694a125e41645312.s3.ap-southeast-1.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-sin-694a125e41645312/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="ap-southeast-2" label="Sydney"}

:button[Launch]{variant="primary" href="https://ap-southeast-2.console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-syd-b04c62a5f16f7b2e.s3.ap-southeast-2.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-sin-694a125e41645312/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="ap-northeast-1" label="Tokyo"}

:button[Launch]{variant="primary" href="https://ap-northeast-1.console.aws.amazon.com/cloudformation/home?region=ap-northeast-1#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-nrt-2cb4b4649d0e0f94.s3.ap-northeast-1.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-nrt-2cb4b4649d0e0f94/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="eu-central-1" label="Frankfurt"}

:button[Launch]{variant="primary" href="https://eu-central-1.console.aws.amazon.com/cloudformation/home?region=eu-central-1#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-fra-b129423e91500967.s3.eu-central-1.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-fra-b129423e91500967/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
:::tab{id="eu-west-2" label="London"}

:button[Launch]{variant="primary" href="https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/review?templateUrl=https://ws-assets-prod-iad-r-lhr-cc4472a651221311.s3.eu-west-2.amazonaws.com/d1efe734-f76b-45bd-8fd4-801ed1394e45/vscode-server.yaml&stackName=VSCode&param_HomeFolder=/workshop&param_AssetZipS3Path=ws-assets-prod-iad-r-lhr-cc4472a651221311/d1efe734-f76b-45bd-8fd4-801ed1394e45/workshop.zip"}

:::
::::

When you arrive at the page, you can check the Stack configuration information. Continue scrolling down without making any modifications.

:image[Pre-configured Resources]{src="/static/images/02.quick-create-stack.png" width=512}

2. At the bottom of the page, enable IAM Capabilities. Click the **Create stack** button to request stack creation.

:image[Pre-configured Resources]{src="/static/images/02.iam-capabilities.png" width=512}



3. The necessary infrastructure will be deployed along with the stack creation. Please wait until the stack status changes to `CREATE_COMPLETE`.

:image[Pre-configured Resources]{src="/static/images/02.create-in-progress.png" height=256}

:image[Pre-configured Resources]{src="/static/images/02.create-complete.png" width=512}

---
You have successfully deployed the stack for the workshop. Please proceed to the next section to connect to the VS Code Server.