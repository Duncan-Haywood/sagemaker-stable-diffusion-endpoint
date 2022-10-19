from aws_cdk import Stack

from constructs import Construct
from aws_cdk import aws_sagemaker as sagemaker
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecr_assets as ecr_assets


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
            variant_name="production",
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

        return endpoint_config


class ModelConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # model bucket
        model_bucket = s3.Bucket(self, "ModelBucket")

        # container
        environment = None
        container_definition_property = sagemaker.CfnModel.ContainerDefinitionProperty(
            environment=environment,
            image=NotImplemented,
            image_config=sagemaker.CfnModel.ImageConfigProperty(
                repository_access_mode="repositoryAccessMode",
                # the properties below are optional
                repository_auth_config=sagemaker.CfnModel.RepositoryAuthConfigProperty(
                    repository_credentials_provider_arn="repositoryCredentialsProviderArn"
                ),
            ),
            inference_specification_name="inferenceSpecificationName",
            mode="mode",
            model_data_url="modelDataUrl",
            model_package_name="modelPackageName",
        )


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

        return async_inference_config


class ModelContainer(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        NotImplemented
        """Deep Learning AMI GPU PyTorch 1.12.? ${PATCH_VERSION} (Amazon Linux 2) ${YYYY-MM-DD}
        
        Supported EC2 Instances: G3, P3, P3dn, P4d, G5, G4dn
        
        https://aws.amazon.com/releasenotes/aws-deep-learning-ami-gpu-pytorch-1-12-amazon-linux-2/"""

        repository = ecr.Repository(
            self,
            "DiffusionEndpointRepository",
            image_scan_on_push=True,
        )

        image = ecr_assets  # TODO
