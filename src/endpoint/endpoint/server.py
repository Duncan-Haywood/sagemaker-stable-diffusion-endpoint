"""looks to default inference.py for handler overwriting."""
from sagemaker_inference import model_server


def main():
    model_server.start_model_server()


if __name__ == "__main__":
    main()
