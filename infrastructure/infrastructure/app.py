#!/usr/bin/env python3

import aws_cdk as cdk

from infrastructure.endpoint import EndpointStack


def main():
    app = cdk.App()
    EndpointStack(
        app,
        "EndpointInfrastructureStack",
    )
    cloud_assembly = app.synth()
    return cloud_assembly


if __name__ == "__main__":
    main()
