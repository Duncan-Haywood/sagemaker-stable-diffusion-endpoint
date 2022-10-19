#!/usr/bin/env python3
import os

import aws_cdk as cdk

from endpoint_infrastructure.endpoint_infrastructure_stack import (
    EndpointInfrastructureStack,
)


app = cdk.App()
EndpointInfrastructureStack(
    app,
    "EndpointInfrastructureStack",
)

app.synth()
