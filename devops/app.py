#!/usr/bin/env python3

import aws_cdk as cdk

from devops.devops_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "devops")

app.synth()
