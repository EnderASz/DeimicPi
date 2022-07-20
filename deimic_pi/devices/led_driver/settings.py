from pydantic import BaseModel
from deimic_pi import settings as base


class LedDriverSettings(BaseModel):
    strip_length: int = 0
    data_pin: int = 18


class Settings(base.Settings):
    led_driver: LedDriverSettings = LedDriverSettings()
