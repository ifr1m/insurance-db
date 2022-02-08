import functools
from typing import Dict

from insurancedb.extractors.base import BaseRcaExtractor

extractors_registry_map: Dict[str, BaseRcaExtractor.__class__] = {}


def register(cls):
    extractors_registry_map[cls.__name__.lower()] = cls
    return cls


extractor_register = functools.partial(register)
