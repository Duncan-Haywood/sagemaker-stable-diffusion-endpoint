import typer
from endpoint import util
from endpoint.logger import get_logger

logger = get_logger(__name__)


def create_github_token_secret():
    token = typer.prompt("github access token:")
    secret_name = "github-token"
    description = "github access token for aws codepipeline"
    util.create_secret(secret_name, token, description=description)
    logger.info("created a github secret with token")


if __name__ == "__main__":
    typer.run(create_github_token_secret)
