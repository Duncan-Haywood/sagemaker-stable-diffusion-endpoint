"""looks to default inference.py for handler overwriting."""
from sagemaker_inference import model_server
import subprocess
from retrying import retry
from subprocess import CalledProcessError
from sagemaker_inference import model_server
from .logger import get_logger
import sys
import shlex
logger = get_logger(__name__)


def _retry_if_error(exception):
    return isinstance(exception, CalledProcessError or OSError)


@retry(stop_max_delay=1000 * 50, retry_on_exception=_retry_if_error)
def _start_mms():
    # by default the number of workers per model is 1, but we can configure it through the
    # environment variable below if desired.
    # os.environ['SAGEMAKER_MODEL_SERVER_WORKERS'] = '2'
    model_server.start_model_server()


def main():
    if sys.argv[1] == "serve":
        _start_mms()
        logger.info("server started")
    else:
        subprocess.check_call(shlex.split(" ".join(sys.argv[1:])))
    # prevent docker exit -- might not be needed in async version when shutting down constantly
    subprocess.call(["tail", "-f", "/dev/null"])


if __name__ == "__main__":
    main()
