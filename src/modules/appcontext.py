import threading
from dataclasses import dataclass

@dataclass(slots=True)
class AppContext:
    thread_shutdown: threading.Event
    
