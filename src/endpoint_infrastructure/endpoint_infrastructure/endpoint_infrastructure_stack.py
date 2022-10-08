from aws_cdk import Stack

from constructs import Construct
from aws_cdk import aws_sagemaker as sagemaker
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from sagemaker.huggingface import HuggingFaceModel


class EndpointInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        endpoint_config = EndpointConifgConstruct(self, "EndpointConfig")

        # create endpoint
        endpoint = sagemaker.CfnEndpoint(
            self,
            "DiffusionEndpoint",
            endpoint_config_name=endpoint_config.endpoint_config_name,
        )


class EndpointConifgConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        accelerator_type = "eia2.xlarge"
        instance_type = "ml.t2.xlarge"

        model = ModelConstruct(self)
        async_inference_config = AsyncConfigConstruct(self)

        # create production deployent config for instances
        prod_variant_config = sagemaker.CfnEndpointConfig.ProductionVariantProperty(
            model_name=model.model_name,
            accelerator_type=accelerator_type,
            initial_instance_count=0,
            instance_type=instance_type,
        )

        # wrap in standard config
        endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "DiffusionEndpointConfig",
            async_inference_config=async_inference_config,
            production_variants=[prod_variant_config],
        )


class ModelConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # model bucket
        model_bucket = s3.Bucket(self, "ModelBucket")


class AsyncConfigConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create output bucket
        output_bucket = s3.Bucket(
            self,
            "OutputBucket",
            # block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )
        s3_output_path = output_bucket.bucketWebsiteUrl

        # create notifications topics
        success_topic = sns.Topic(self, "DiffusionSuccess")
        error_topic = sns.Topic(self, "DiffusionError")

        # add topics to async config
        async_notification_config = (
            sagemaker.CfnEndpointConfig.AsyncInferenceNotificationConfigProperty(
                error_topic=error_topic.topic_name,
                success_topic=success_topic.topic_name,
            )
        )
        # wrap in async config
        async_inference_config = (
            sagemaker.CfnEndpointConfig.AsyncInferenceConfigProperty(
                output_config=sagemaker.CfnEndpointConfig.AsyncInferenceOutputConfigProperty(
                    s3_output_path=s3_output_path,  # TODO test
                    notification_config=async_notification_config,
                ),
            ),
        )
