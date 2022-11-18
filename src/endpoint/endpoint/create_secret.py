import typer
from . import util
from .logger import get_logger

logger = get_logger(__name__)


def create_hugging_face_secret():
    token = typer.prompt("hugging face api token:")
    secret_name = util.get_huggingface_secret_name()
    description = "Huggingfce api token for model hub"
    util.create_secret(secret_name, token, description=description)
    logger.info("created a hugging face secret with token")


if __name__ == "__main__":
    typer.run(create_hugging_face_secret)
