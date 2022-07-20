from textual.app import App

from deimic_pi.devices.cli import CLITool
from deimic_pi.devices.cli.app.views import ConnectionEstablishView
from deimic_pi.devices.cli.settings import Settings


class CLIApp(App):
    device: CLITool

    async def on_mount(self):
        await self.view.dock(
            ConnectionEstablishView()
        )
        self.device = CLITool(settings=Settings())


if __name__ == '__main__':
    CLIApp.run()
