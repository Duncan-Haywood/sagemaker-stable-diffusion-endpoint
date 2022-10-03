from sagemaker.async_inference import AsyncInferenceConfig
from diffusers import StableDiffusionPipeline
from sagemaker.huggingface import HuggingFaceModel
import sagemaker
from sagemaker.predictor_async import AsyncPredictor


class Endpoint:
    def __init__(self):
        self.role = sagemaker.get_execution_role()
        self.output_path = "s3://{s3_bucket}/{bucket_prefix}/output"
        self.input_path = "s3://{s3_bucket}/{bucket_prefix}/input"
        self.model_path = "s3://{s3_bucket}/{bucket_prefix}/input"

    def get_model(self):
        # create Hugging Face Model Class
        self.model = HuggingFaceModel(
            model_data=self.model_path,
            # entry_point=
            role=self.role,  # iam role with permissions to create an Endpoint
            transformers_version="4.6",  # transformers version used
            pytorch_version="1.7",  # pytorch version used
            py_version="py36",  # python version of the DLC
        )

    def deploy(self):
        self.get_model()
        async_config = AsyncInferenceConfig(
            output_path=self.output_path,
        )
        # data_capture_config= TODO
        self.async_predictor = self.model.deploy(
            async_inference_config=async_config,
            initial_instance_count=0,
            #    instance_type="ml.p2.xlarge",
            # accelerator_type=''
            # data_capture_config=data_capture_config
        )

    def predict(self, file_path):
        file = f"{self.input_path}/{file_path}"
        response = self.async_predictor.predict(file)
        return response

    def undeploy(self):
        self.async_predictor.delete_endpoint()
