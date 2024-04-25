api_logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"level": "INFO", "propagate": True},
        "uvicorn.error": {"level": "INFO", "propagate": True},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

front_logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": "INFO",
        "propagate": True,
    },
    "loggers": {
        "gunicorn.error": {
            "level": "INFO",
            "propagate": True,
            "qualname": "gunicorn.error",
        },
        "gunicorn.access": {
            "level": "ERROR",
            "propagate": True,
            "qualname": "gunicorn.access",
        },
    },
    "formatters": {
        "generic": {
            "format": "%(levelname)s: (Front server) %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        }
    },
}
