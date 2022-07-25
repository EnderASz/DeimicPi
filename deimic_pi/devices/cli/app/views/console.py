from textual import events
from textual.views import GridView
from textual.widgets import Placeholder

from deimic_pi.devices.cli import CLITool
from deimic_pi.devices.cli.app.widgets import TextInput


class BridgeConsoleView(GridView):
    def __init__(self, device: CLITool):
        super().__init__()
        self.device = device

    async def on_mount(self, event: events.Mount):
        self.grid.add_column('left', fraction=1, max_size=35)
        self.grid.add_column('right', fraction=3)
        self.grid.add_row('top')
        self.grid.add_row('bottom', size=3)
        self.grid.add_areas(
            commands_area='left, top-start | bottom-end',
            monitor_area='right, top',
            command_line_area='right, bottom'
        )
        self.grid.add_widget(Placeholder(name='commands'), area='commands_area')
        self.grid.add_widget(Placeholder(name='monitor'), area='monitor_area')
        self.grid.add_widget(
            TextInput(
                name='command_line',
                title="",
                hint="Enter command for bridge here..."
            ),
            area='command_line_area'
        )
