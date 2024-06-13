from typing import Literal, Dict

Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LEVEL_COLORS: Dict[Level, str] = {
    "DEBUG": "\033[36m",  # Cyan (DEBUG)
    "INFO": "\033[32m",  # Green (INFO)
    "WARNING": "\033[33m",  # Yellow (WARNING)
    "ERROR": "\033[31m",  # Red (ERROR)
    "CRITICAL": "\033[91m",  # Bright Red (CRITICAL)
    "DEFAULT": "\033[0m",  # Reset to default color (DEFAULT)
}
