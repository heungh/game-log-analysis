---
title : "EC2 코드서버 접속"
weight : 13
---

워크샵 환경에는 VS 코드 서버 한 대가 실행중입니다. 이 환경에는 NodeJS 와 **[AWS Cloud Development Kit](https://aws.amazon.com/cdk/)** 도구가 설치되어 있습니다. IDE 환경을 통해 워크샵에 필요한 자원을 사전에 생성하고, AWS 콘솔에서 구성하기 까다로운 자원들을 CLI 명령으로 구성할 에정입니다.

## 접속 정보 확인

**워크샵 이벤트 계정을 사용하는 경우**

:button[Open Event Dashboard]{variant="primary" href="https://catalog.prod.workshops.aws/event/dashboard/ko-KR"}

버튼을 눌러 이벤트 대시보드에 접속합니다. 화면 하단에 Event Outputs 에서 다음 두 가지 값을 확인하시기 바랍니다.
  - **URL**: VS CodeServer IDE 에 접속할 수 있는 CloudFront URL 입니다.
  - **Password**: IDE 첫 진입시 필요한 비밀번호 값입니다.

  :image[Stack Outputs]{src="/static/images/03.codeserver-output.png" width=512}

**자체 계정을 사용하는 경우**

전 단계에서 생성한 CloudFormation 스택 정보를 확인합니다. **Outputs** 탭에서 다음 두 가지 값을 확인하시기 바랍니다.
  - **URL**: VS CodeServer IDE 에 접속할 수 있는 CloudFront URL 입니다.
  - **Password**: IDE 첫 진입시 필요한 비밀번호 값입니다.

  :image[Stack Outputs]{src="/static/images/03.codeserver-stack-output.png" width=512}

## 서버 접속

브라우저에서 URL로 접속하면 Password 입력 화면이 등장합니다.

:image[Submit Passcode]{src="/static/images/03.codeserver-password.png" width=512}

Password 값을 전송하면 다음과 같은 IDE 화면이 표시되어야 합니다.

:image[Code Server IDE Preview]{src="/static/images/03.codeserver-ide.png" width=1024}

## 터미널 명령어 복사-붙여넣기 유의사항

**Firefox** 유저의 경우:
  - Windows/Linux: 단축키 `Shift+V`
  - macOS: 단축키 `Command+Shift+V`


**Google Chrome** 유저의 경우: 

알럿이 표시되며 클립보드 텍스트를 접근하는 권한이 요청됩니다. 이후 모듈에서 터미널 명령어를 복사-붙여넣기 하려면, 이 권한을 꼭 허용해 주세요.

:image[Opt-in accessibility privilleges]{src="/static/images/03.chrome-allowing-paste.png" width=512}


정상적으로 IDE 접속을 완료하셨다면, 다음 단계로 진행하실 수 있습니다!