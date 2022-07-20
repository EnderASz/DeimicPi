from pydantic import BaseModel
from deimic_pi import settings as base


class CLIToolSettings(BaseModel):
    pass


class Settings(base.Settings):
    cli_tool: CLIToolSettings = CLIToolSettings()
