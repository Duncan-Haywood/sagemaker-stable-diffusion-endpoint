from sagemaker.async_inference import AsyncInferenceConfig
from sagemaker.huggingface import HuggingFaceModel
import sagemaker
from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor


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

    def predict(self, relative_file_path, **kwargs):
        self.get_predictor()
        full_file_path = f"{self.input_path}/{relative_file_path}"
        response = self.async_predictor.predict(full_file_path, kwargs)
        return response

    def upload_and_predict(self, local_file_path, **kwargs):
        pass

    def build_model(self):
        """Create Hugging Face Model Class for dpeloyment and prediction."""
        self.model = HuggingFaceModel(
            model_data=self.model_path,
            # entry_point=
            role=self.role,  # iam role with permissions to create an Endpoint
            transformers_version="4.6",  # transformers version used
            pytorch_version="1.7",  # pytorch version used
            py_version="py36",  # python version of the DLC
        )

    def deploy(self):
        """Deploy model to endpoint"""
        self.build_model()
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
        self.get_predictor()
        self.async_predictor.delete_endpoint()

    def model_hub_to_s3(self):
        """move hugging face model to s3 bucket for use"""
        NotImplemented

    def get_predictor(self):
        """Retrieve predictor object"""
        if self.async_predictor == None:
            self.async_predictor = AsyncPredictor(
                Predictor(endpoint_name=self.endpoint_name, sagemaker_session=self.sess)
            )
        else:
            pass
