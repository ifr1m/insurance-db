import logging
import logging.config
import logging.config
import logging.handlers
from pathlib import Path
from typing import Any, Dict

log_config_registry_map: Dict[str, Any] = {}


def get_log_config(disable_existing_loggers=False, root_logger_level='WARN', app_logger_level='INFO',
                   log_dir: Path = Path('.'), to_file=False):
    if to_file is True:
        active_handlers = ['console', 'file', 'errors']
        handlers = {
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'detailed'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': str(log_dir / 'insurancedb.log'),
                    'mode': 'w',
                    'formatter': 'detailed'
                },
                'errors': {
                    'class': 'logging.FileHandler',
                    'filename': str(log_dir / 'insurancedb-errors.log'),
                    'mode': 'w',
                    'formatter': 'detailed',
                    'level': 'ERROR'
                }
            }
        }
    else:
        active_handlers = ['console']
        handlers = {
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'detailed'
                }
            }
        }

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
        'loggers': {
            'insurancedb': {
                'handlers': active_handlers,
                'level': app_logger_level,
                'propagate': False
            },
            '__main__': {
                'handlers': active_handlers,
                'level': 'DEBUG',
                'propagate': False
            }
        },
        'root': {
            'handlers': active_handlers,
            'level': root_logger_level
        }
    }
    config.update(handlers)
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
