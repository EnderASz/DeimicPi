import asyncio
import os
from pathlib import Path

import click

from deimic_pi.devices.led_driver import LedDriver
from deimic_pi.devices.led_driver.settings import LedDriverSettings, Settings
from deimic_pi.types import Port


@click.command()
@click.option(
    '--bridge-addr',
    '-a',
    'bridge_addr_form',
    default=Settings.get_default('bridge_addr_form'),
    show_default=True,
    help="Bridge's address")
@click.option(
    '--bcst-port',
    '-b',
    'inter_req_bcst_port',
    default=Settings.get_default('inter_req_bcst_port'),
    show_default=True,
    type=Port(),
    help="Internal requests broadcaster's port")
@click.option(
    '--listener-port',
    '-l',
    'inter_rep_recv_port',
    default=Settings.get_default('inter_req_bcst_port'),
    show_default=True,
    type=Port(),
    help="Internal replies receiver's port")
@click.option(
    '--strip-length',
    '-L',
    'strip_length',
    default=Settings.get_default('led_driver__strip_length'),
    type=int,
    help="Led strip length")
def execute(
    bridge_addr_form: str,
    inter_req_bcst_port: Port,
    inter_rep_recv_port,
    strip_length: int
):
    settings = Settings.from_file(
        led_driver=LedDriverSettings(strip_length=strip_length),
        bridge_addr_form=bridge_addr_form,
        inter_req_bcst_port=inter_req_bcst_port,
        inter_rep_recv_port=inter_rep_recv_port,
    )
    driver = LedDriver(settings)
    asyncio.run(driver.execute())


if __name__ == '__main__':
    execute()
