#!/usr/bin/env python3

import aws_cdk as cdk

from .devops import DevPipelineStack, ProdPipelineStack


def main():
    app = cdk.App()
    DevPipelineStack(app, "DevPipeline")
    ProdPipelineStack(app, "DevPipeline")
    cloud_assembly = app.synth()
    return cloud_assembly


if __name__ == "__main__":
    main()
