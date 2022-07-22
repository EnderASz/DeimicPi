from textual.app import App
from textual.widgets import Placeholder

from deimic_pi.devices.cli import CLITool
from deimic_pi.devices.cli.app.views import (
    ConnectionEstablishView,
    AppConnected
)


class CLIApp(App):
    cli_device: CLITool

    async def handle_app_connected(self, message: AppConnected):
        self.cli_device = message.cli_device
        self.view.layout.docks.clear()
        self.view.widgets.clear()

        await self.view.dock(Placeholder(name=str(self.cli_device)))

    async def on_mount(self):
        await self.view.dock(ConnectionEstablishView())


if __name__ == '__main__':
    CLIApp.run()
