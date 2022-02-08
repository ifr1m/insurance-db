import logging
import logging.config
import logging.config
import logging.handlers
from typing import Any, Dict

log_config_registry_map: Dict[str, Any] = {}


def get_log_config(disable_existing_loggers=False, root_logger_level='WARN', app_logger_level='INFO'):
    config = {
        'version': 1,
        'disable_existing_loggers': disable_existing_loggers,
        'formatters': {
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
            },
            'simple': {
                'class': 'logging.Formatter',
                'format': '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'detailed'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'insurancedb.log',
                'mode': 'w',
                'formatter': 'detailed'
            },
            'errors': {
                'class': 'logging.FileHandler',
                'filename': 'insurancedb-errors.log',
                'mode': 'w',
                'formatter': 'detailed',
                'level': 'ERROR'
            }
        },
        'loggers': {
            'insurancedb':{
                'handlers': ['console', 'file', 'errors'],
                'level': app_logger_level,
                'propagate': False
            },
            '__main__': {
                'handlers': ['console', 'file', 'errors'],
                'level': 'DEBUG',
                'propagate': False
            }
        },
        'root': {
            'handlers': ['console', 'file', 'errors'],
            'level': root_logger_level
        }
    }
    return config


def get_dispatch_log_config(q, disable_existing_loggers=False, root_logger_level='WARN', app_logger_level='INFO'):
    config = {
        'version': 1,
        'disable_existing_loggers': disable_existing_loggers,
        'handlers': {
            'queue': {
                'class': 'logging.handlers.QueueHandler',
                'queue': q
            }
        },
        'loggers': {
            'insurancedb': {
                 'handlers': ['queue'],
                'level': app_logger_level,
                'propagate': False
            },
            '__main__': {
                 'handlers': ['queue'],
                'level': 'DEBUG',
                'propagate': False
            }
        },
        'root': {
            'handlers': ['queue'],
            'level': root_logger_level
        }
    }
    return config


def worker_log_initializer(config):
    logging.config.dictConfig(config)
