---
title : "자체 계정에서 실행하기"
weight : 12
---

:::alert{header="중요" type="warning"}
이 항목을 진행하려면 여러분 소유의 AWS 계정이 필요합니다.
:::

워크샵을 준비할 수 있는 AWS CloudFormation 템플릿을 각 AWS 리전별로 제공하고 있습니다. 

템플릿을 배포하면 여러분의 계정에 VS 코드서버 인스턴스가 실행됩니다. 서버에 접속하여 이번 AWS Entity Resolution 실습을 수행할 수 있습니다. 

## CloudFormation 스택 배포

1. 하위 탭에서 리전을 선택하고, **Launch** 버튼을 실행하여 AWS CloudFormation 콘솔에 접속하실 수 있습니다. (AWS 계정 로그인이 요구될 수 있습니다.)

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

페이지에 도착하면 Stack 을 구성 정보를 확인할 수 있습니다. 별다른 수정사항 없이 스크롤을 아래로 진행합니다.

:image[Pre-configured Resources]{src="/static/images/02.quick-create-stack.png" width=512}

2. 페이지 가장 하단에 IAM Capabilities 를 활성합니다. **Create stack** 버튼을 눌러 스택 생성을 요청합니다.

:image[Pre-configured Resources]{src="/static/images/02.iam-capabilities.png" width=512}



3. 스택 생성과 함께 필요한 인프라가 배치될 것입니다. 스택 상태가 `CREATE_COMPLETE`로 변경될 때까지 잠시 대기합니다.

:image[Pre-configured Resources]{src="/static/images/02.create-in-progress.png" height=256}

:image[Pre-configured Resources]{src="/static/images/02.create-complete.png" width=512}

---
워크샵을 위한 스택 배포에 성공하였습니다. 다음 섹션으로 이동하여 VS Code Server 에 접속을 진행하여 주십시오.