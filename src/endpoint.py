from sagemaker.async_inference import AsyncInferenceConfig
from diffusers import StableDiffusionPipeline
from sagemaker.huggingface import HuggingFaceModel
import sagemaker


class Endpoint:
    def __init__(self):
        self.role = sagemaker.get_execution_role()
        # s3_url = "s3://{s3_bucket}/{bucket_prefix}/output"

    def deploy(self):
        self.get_model()
        async_config = AsyncInferenceConfig(
            # output_path=s3_url,
        )
        self.async_predictor = self.model.deploy(async_inference_config=async_config)

    def undeploy(self):
        self.async_predictor.delete_endpoint()

    def predict(self, input_data):
        self.async_predictor.predict(input_data)

    def get_model(self):
        # Hub Model configuration. https://huggingface.co/models
        hub = {
            "HF_MODEL_ID": "CompVis/stable-diffusion-v1-4",  # model_id from hf.co/models
            "HF_TASK": "question-answering",  # NLP task you want to use for predictions
        }
        # create Hugging Face Model Class
        self.model = HuggingFaceModel(
            env=hub,
            role=self.role,  # iam role with permissions to create an Endpoint
            transformers_version="4.6",  # transformers version used
            pytorch_version="1.7",  # pytorch version used
            py_version="py36",  # python version of the DLC
        )
