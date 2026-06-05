import os
import logging
import uuid
from dotenv import load_dotenv

load_dotenv()

logger: logging.Logger = logging.getLogger(__name__)


def _generate_session_id() -> str:
    """
    Generates a New UUID using the UUID7 formating

    Returns:
        str: The generated UUID in string form
    """
    generated_uuid: uuid.UUID = uuid.uuid7()
    return str(generated_uuid)

def _get_env_variable(name: str, default: str | None = None) -> str | None:
    """
    Retrieves an environment variable, with an optional default value.

    Args:
            name (str): The name of the environment variable to retrieve.
            default (str | None): An optional default value to return if the environment variable is not set.

    Returns:
            str | None: The value of the environment variable, or the default value if it is not set.
    """

    try:
        value: str | None = os.getenv(name, default)

        if value in (None, ""):
            logger.warning(
                f"Environment variable '{name}' is not set, using default value: '{default if default is not None else 'None'}'"
            )
            return default

        return value
    except Exception as e:
        logger.error(f"Error retrieving environment variable '{name}': {e}")
        return default


# General Settings
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
PROBE_ID: str = _generate_session_id()

SEND_DATA_TO_SERVER: bool = False

# Database Settings
DATABASE_FILENAME: str = "probedata.db"
DATABASE_QUEUE_MAX_SIZE: int = 1000

# Sensor Setting
SEA_LEVEL_PRESSURE: int = 1013
SENSOR_FAIL_SHUTDOWN_LIMIT: int = 5
