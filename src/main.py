import logging
import sys

logger: logging.Logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from core import sensor_reader
from config import BASE_DIR

def main():
    sensor_reader.load_sensors()
    sensor_reader.read_sensor_loop()


if __name__ == "__main__":
    main()
