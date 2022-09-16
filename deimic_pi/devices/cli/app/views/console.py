from textual import events
from textual.views import GridView
from textual.widgets import Placeholder

from deimic_pi.devices.cli import CLITool
from deimic_pi.devices.cli.app.widgets import TextInput, ClockHeader, Submitted


class BridgeConsoleView(GridView):
    command_line_input: TextInput

    def __init__(self, device: CLITool):
        super().__init__()
        self.device = device

    def handle_submitted(self, message: Submitted):
        if message.sender is self.command_line_input:
            # self.device.request_socket.send_string(self.command_line_input.content)
            self.command_line_input.clear()

    async def on_mount(self, event: events.Mount):
        self.command_line_input = TextInput(
            name='command_line',
            title="",
            hint="Enter command for bridge here..."
        )
        self.grid.add_column('left', fraction=1, max_size=35)
        self.grid.add_column('right', fraction=3)
        self.grid.add_row('header', size=3)
        self.grid.add_row('top')
        self.grid.add_row('bottom', size=3)
        self.grid.add_areas(
            header='left-start | right-end, header',
            commands_area='left, top-start | bottom-end',
            monitor_area='right, top',
            command_line_area='right, bottom'
        )
        self.grid.add_widget(ClockHeader(subtitle="Console"), area='header')
        self.grid.add_widget(Placeholder(name='commands'), area='commands_area')
        self.grid.add_widget(Placeholder(name='monitor'), area='monitor_area')
        self.grid.add_widget(
            self.command_line_input,
            area='command_line_area'
        )