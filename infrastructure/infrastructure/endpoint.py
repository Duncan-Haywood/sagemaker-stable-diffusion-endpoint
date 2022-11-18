from aws_cdk import Stack, Tags
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sagemaker as sagemaker
from constructs import Construct
from aws_cdk import aws_iam as iam


class EndpointStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # adds resource tags to all resources in this stack for the purposes of IAM access management
        Tags.of(self).add("Application", "DiffusionEndpoint")

        # model bucket for hosting the model files
        model_bucket = s3.Bucket(self, "ModelBucket")

        # name of model bucket
        self.model_bucket_name = model_bucket.bucket_name

        # async output bucket
        async_output_bucket = s3.Bucket(
            self,
            "OutputBucket",
        )

        # path of output bucket
        async_s3_output_path = async_output_bucket.s3_url_for_object()

        # creates role needed for execution of model construct
        model_role_construct = ModelRoleConstruct(self, "ModelRole")
        model_execution_role = model_role_construct.model_execution_role
        execution_role_arn = model_execution_role.role_arn

        # model to be used in endpoint
        model_construct = ModelConstruct(
            self,
            "ModelConstruct",
            model_bucket_name=self.model_bucket_name,
            execution_role_arn=execution_role_arn,
        )
        model = model_construct.model
        model_name = model.attr_model_name

        # config for endpoint
        endpoint_config_construct = EndpointConfigConstruct(
            self,
            "EndpointConfig",
            async_s3_output_path=async_s3_output_path,
            model_name=model_name,
        )
        endpoint_config = endpoint_config_construct.endpoint_config
        endpoint_config_name = endpoint_config.attr_endpoint_config_name

        # create endpoint
        self.endpoint = sagemaker.CfnEndpoint(
            self,
            "DiffusionEndpoint",
            endpoint_config_name=endpoint_config_name,
        )
        self.endpoint_name = self.endpoint.attr_endpoint_name


class EndpointConfigConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        async_s3_output_path: str = "",
        model_name: str = "",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # type of instance on which the endpoint will run
        instance_type = "ml.p2.xlarge"

        # name of production variant
        variant_name = "TODO"

        # which proportion of instances to use with this model on scale [0,1.0] -- required paramenter that's not relevant to us
        initial_variant_weight = 1.0

        # configuration for async output
        async_inference_config = sagemaker.CfnEndpointConfig.AsyncInferenceConfigProperty(
            output_config=sagemaker.CfnEndpointConfig.AsyncInferenceOutputConfigProperty(
                s3_output_path=async_s3_output_path,
            ),
        )

        # create production deployent config for instances
        prod_variant_config = sagemaker.CfnEndpointConfig.ProductionVariantProperty(
            initial_variant_weight=initial_variant_weight,
            model_name=model_name,
            variant_name=variant_name,
            initial_instance_count=0,
            instance_type=instance_type,
        )

        # wrap in standard config
        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "DiffusionEndpointConfig",
            async_inference_config=async_inference_config,
            production_variants=[prod_variant_config],
        )


class ModelConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        model_bucket_name: str = "",
        execution_role_arn: str = "",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # docker image with inference code and server for sagemaker predictions
        image = ecr_assets.DockerImageAsset(
            self, "ModelImage", directory="../src/", file="endpoint/Dockerfile.endpoint"
        )
        image_uri = image.image_uri

        # environment to pass to container
        environment = {"MODEL_BUCKET_NAME": model_bucket_name}

        # container
        container_definition_property = sagemaker.CfnModel.ContainerDefinitionProperty(
            environment=environment,
            image=image_uri,
        )

        # creates model with execution role and container defenition
        self.model = sagemaker.CfnModel(
            self,
            "Model",
            execution_role_arn=execution_role_arn,
            primary_container=container_definition_property,
        )


class ModelRoleConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # managed policy that allows all access to resources with the endpoint tag
        EndpointApplicationAllAccessManagedPolicy = iam.ManagedPolicy(
            self,
            "EndpointApplicationAllAccessManagedPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["*"],
                    conditions={
                        "StringEquals": {
                            "aws:ResourceTag/Application": "DiffusionEndpoint"
                        }
                    },
                    resources=["*"],
                )
            ],
        )

        # role needed for model
        # TODO reduce access to only what's needed.
        self.model_execution_role = iam.Role(
            self,
            "ModelExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[EndpointApplicationAllAccessManagedPolicy],
        )
