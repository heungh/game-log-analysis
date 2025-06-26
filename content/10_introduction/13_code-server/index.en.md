---
title : "VS Code Server"
weight : 13
---

The workshop environment has a VS Code server running. This environment has NodeJS and **[AWS Cloud Development Kit](https://aws.amazon.com/cdk/)** tools installed. Through the IDE environment, we will pre-create resources needed for the workshop and configure resources that are difficult to set up in the AWS console using CLI commands.

## Check Connection Information

**If you are using a workshop event account**

:button[Open Event Dashboard]{variant="primary" href="https://catalog.prod.workshops.aws/event/dashboard/en-US"}

Click the button to access the event dashboard. Please check the following two values in the Event Outputs at the bottom of the screen:
  - **URL**: CloudFront URL to access the VS CodeServer IDE.
  - **Password**: Password required for initial IDE access.

  :image[Stack Outputs]{src="/static/images/03.codeserver-output.png" width=512}

**If you are using your own account**

Check the CloudFormation stack information created in the previous step. Please check the following two values in the **Outputs** tab:
  - **URL**: CloudFront URL to access the VS CodeServer IDE.
  - **Password**: Password required for initial IDE access.

  :image[Stack Outputs]{src="/static/images/03.codeserver-stack-output.png" width=512}

## Connect to the Server

When you access the URL in your browser, a Password entry screen will appear.

:image[Submit Passcode]{src="/static/images/03.codeserver-password.png" width=512}

After submitting the Password, you should see the IDE screen as follows:

:image[Code Server IDE Preview]{src="/static/images/03.codeserver-ide.png" width=1024}

## Notes on Copy-Paste in Terminal

**For Firefox users**:
  - Windows/Linux: Shortcut `Shift+V`
  - macOS: Shortcut `Command+Shift+V`


**For Google Chrome users**: 

An alert will appear requesting permission to access clipboard text. To copy and paste terminal commands in later modules, please make sure to allow this permission.

:image[Opt-in accessibility privilleges]{src="/static/images/03.chrome-allowing-paste.png" width=512}


If you have successfully connected to the IDE, you can proceed to the next step!