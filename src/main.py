import logging
import sys
import threading


logger: logging.Logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

from core import sensor_reader, filewriting
from config import BASE_DIR


def main():
    sensor_reader.load_sensors()

    sensor_thread = threading.Thread(target=sensor_reader.read_sensor_loop)
    file_writing_thread = threading.Thread()
    networking_thread = threading.Thread()

    sensor_thread.start()


if __name__ == "__main__":
    main()
