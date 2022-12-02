from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sagemaker as sagemaker
from constructs import Construct
from aws_cdk import aws_iam as iam
from aws_cdk import RemovalPolicy
from aws_cdk.aws_sagemaker import CfnModel

# TODO change once bug fixing is done
INSTANCE_TYPE = "ml.t2.medium"
realinstancetypetochangeto = "ml.p2.xlarge"


class EndpointStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, image_uri=None, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # async output bucket
        async_output_bucket = s3.Bucket(
            self,
            "OutputBucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # model bucket for hosting the model files
        model_bucket = s3.Bucket(
            self,
            "ModelBucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # path of output bucket
        async_s3_output_path = async_output_bucket.s3_url_for_object()

        # create role needed for execution of model construct
        model_execution_role = iam.Role(
            self,
            "ModelExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ContainerRegistryReadOnly"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],
        )
        execution_role_arn = model_execution_role.role_arn

        # create model
        model = sagemaker.CfnModel(
            self,
            "Model",
            execution_role_arn=execution_role_arn,
            primary_container=CfnModel.ContainerDefinitionProperty(
                environment={"MODEL_BUCKET_NAME": model_bucket.bucket_name},
                image=image_uri,
            ),
        )

        # wrap in standard config
        endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "DiffusionEndpointConfig",
            async_inference_config=sagemaker.CfnEndpointConfig.AsyncInferenceConfigProperty(
                output_config=sagemaker.CfnEndpointConfig.AsyncInferenceOutputConfigProperty(
                    s3_output_path=async_s3_output_path,
                ),
            ),
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    initial_variant_weight=1.0,
                    model_name=model.attr_model_name,
                    variant_name="V1",
                    initial_instance_count=1,
                    instance_type=INSTANCE_TYPE,
                )
            ],
        )

        # create endpoint
        self.endpoint = sagemaker.CfnEndpoint(
            self,
            "DiffusionEndpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name,
        )
        self.endpoint_name = CfnOutput(
            self, "EndpointName", value=self.endpoint.attr_endpoint_name
        )
        self.model_bucket_name = model_bucket.bucket_name
