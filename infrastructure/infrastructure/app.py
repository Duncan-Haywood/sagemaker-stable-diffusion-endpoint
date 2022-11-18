#!/usr/bin/env python3

import aws_cdk as cdk

from infrastructure.devops import PipelineStack


def main():
    app = cdk.App()
    PipelineStack(app, "Pipeline")
    cloud_assembly = app.synth()
    return cloud_assembly


if __name__ == "__main__":
    main()
