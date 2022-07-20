import json
from functools import lru_cache
import os
from pathlib import Path

from pydantic import BaseSettings
import yaml

from .types import Port

from typing import Any


ENV_PREFIX = 'deimicpi'


class Settings(BaseSettings):
    bridge_addr_form: str = 'tcp://localhost:{port}'

    deimic_port: Port = 5555

    inter_broadcaster_port: Port = 5556
    inter_listener_port: Port = 5557

    extern_bcst_port: Port = 5558
    extern_req_port: Port = 5559

    class Config:
        env_prefix = f'{ENV_PREFIX}_'
        env_nested_delimiter = '__'

        case_sensitive = False

    @classmethod
    def from_file(cls, filename: Path | str = None, **override):
        if filename is None:
            filename = os.path.join(
                Path.home(),
                ".config",
                "deimic_pi",
                "config.yaml"
            )
            if not os.path.isfile(filename):
                dirpath = os.path.dirname(filename)
                os.makedirs(dirpath)
                json.dump(
                    {},
                    open(filename, 'w')
                )
                return cls(**override)
        if not os.path.isfile(filename):
            return cls(**override)
        settings: dict[str, Any] = json.load(open(filename))
        settings.update(override)
        return cls(**settings)

    @classmethod
    @lru_cache
    def get_default(cls, field: str = None):
        """
        Initializes default settings instance and returns it or chosen field of
        name given via `field` parameter if it's not None.

        Returns:
            Default settings instance or chosen field default value

        """
        value = cls()
        if field is None:
            return value
        value = value.dict()
        keys = field.split('__')
        for key in keys:
            value = value.get(key)
        return value
