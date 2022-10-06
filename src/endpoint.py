from sagemaker.async_inference import AsyncInferenceConfig
from sagemaker.huggingface import HuggingFaceModel
import sagemaker
from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor
from sagemaker.async_inference.async_inference_response import AsyncInferenceResponse
from diffusers import StableDiffusionInpaintPipeline
import boto3


class DiffusionEndpoint:
    def __init__(self):
        self.role = sagemaker.get_execution_role()
        self.sess = sagemaker.Session()
        self.s3_bucket = self.sess.default_bucket()
        self.bucket_prefix = "diffusion_endpoint"
        self.model_repository = "CompVis/stable-diffusion-v-1-4"
        self.model_name = self.model_repository.split("/")[-1]
        self.output_path = "s3://{self.s3_bucket}/{self.bucket_prefix}/output"
        self.input_path = "s3://{self.s3_bucket}/{self.bucket_prefix}/input"
        self.model_path = (
            "s3://{self.s3_bucket}/{self.bucket_prefix}/{self.model_name}/model.tar.gz"
        )
        self.endpoint_name = "stable-diffusion-inpaint-endpoint"
        self.async_predictor = None
        self.model = None
        self.huggingface_token_ssm_name = "hugging_face_hub_token"
        self.HUGGINGFACE_TOKEN = None
        self.ssm = None

    def main_predict(self, local_file_path: str, **kwargs) -> AsyncInferenceResponse:
        """Runs Stable Diffusion Inpaint Hugging Face model on Async Sagemaker endpoint.
        Args:
            local_file_path: the location of files to run endpoint on.
        Kwargs:
            TODO
        Return:
            Sagemaker Endpoint response sagemaker `AsyncInferenceResponse` (call  `response.get_response()` for data)
        """
        NotImplemented
        self._upload_input_data_to_s3(local_file_path)
        response = self._predict(local_file_path, kwargs)
        return response

    def deploy(self):
        """Deploy model to Sagemaker endpoint"""
        self._build_model()
        async_config = AsyncInferenceConfig(
            output_path=self.output_path,
        )
        self.async_predictor = self.model.deploy(
            async_inference_config=async_config,
            initial_instance_count=0,
            endpoint_name=self.endpoint_name,
            instance_type="",  # TODO
            #    instance_type="ml.p2.xlarge", # price per hour: $1.125 for GPU use
            accelerator_type="ml.eia2.xlarge",  # price per hour: $0.476
        )

    def undeploy(self):
        """Delete endpoint for predictions. Does not delete model."""
        self._get_predictor()
        self.async_predictor.delete_endpoint()

    def get_model_from_hub(self):
        """Move hugging face model to s3 bucket for use. Zips with inference.py for use by sagemaker."""
        hugging_face_token = self._get_secret(self.huggingface_token_ssm_name)
        model = StableDiffusionInpaintPipeline.from_pretrained(
            self.model_repository, use_auth_token=hugging_face_token
        )

    def _get_secret(self, secret_name):
        """Get an ssm secret's value from it's common name."""
        self.ssm = boto3.client("secretsmanager")
        secret_info = self.ssm.list_secrets(
            Filters=[{"Key": "name", "Values": secret_name}]
        )
        secret_arn = secret_info["SecretList"][0]["ARN"]
        secret_response = self.ssm.get_secret_value(SecretId=secret_arn)
        secret = secret_response["SecretString"]
        return secret

    def _get_predictor(self):
        """Retrieve predictor object"""
        if self.async_predictor == None:
            self.async_predictor = AsyncPredictor(
                Predictor(endpoint_name=self.endpoint_name, sagemaker_session=self.sess)
            )
        else:
            pass

    def _predict(self, relative_file_path, **kwargs):
        """Prediction step. See main_predict for more details."""
        self._get_predictor()
        full_file_path = f"{self.input_path}/{relative_file_path}"
        response = self.async_predictor.predict(full_file_path, kwargs)
        return response

    def _upload_input_data_to_s3(self, local_file_path):
        """Upload input data from local file to correct s3 bucket for prediction."""
        NotImplemented

    def _build_model(self):
        """Create Hugging Face Model Class for dpeloyment and prediction."""
        self.model = HuggingFaceModel(
            model_data=self.model_path,
            # entry_point=
            role=self.role,  # iam role with permissions to create an Endpoint
            transformers_version="4.6",  # transformers version used
            pytorch_version="1.7",  # pytorch version used
            py_version="py36",  # python version of the DLC
        )
