import typer
import util
from .logger import get_logger

logger = get_logger(__name__)


def create_hugging_face_secret():
    token = typer.prompt("hugging face api token:")
    secret_name = "huggingface_api_token"
    description = "Huggingfce api token for model hub"
    util.create_secret(secret_name, token, description=description)
    logger.info("created a hugging face secret with token")


if __name__ == "__main__":
    typer.run(create_hugging_face_secret)
