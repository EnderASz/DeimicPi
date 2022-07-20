import os
from pathlib import Path

from pydantic import BaseModel
from deimic_pi import settings as base


class BridgeSettings(BaseModel):
    deimic_map_file: Path = os.path.join(
        Path.home(),
        ".config",
        "deimic_pi",
        "map.json"
    )


class Settings(base.Settings):
    bridge: BridgeSettings = BridgeSettings()
