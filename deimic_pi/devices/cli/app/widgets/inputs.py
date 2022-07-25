from rich import align
from rich.console import RenderableType
from rich.panel import Panel
from textual import events, log
from textual.message import Message
from textual.message_pump import MessagePump
from textual.reactive import Reactive
from textual.widget import Widget
from textual import widgets as base

from deimic_pi.types import Port


class Submitted(Message):
    pass


class Submittable(MessagePump):
    async def submit(self):
        await self.emit(Submitted(self))


class TextInput(Widget, Submittable):
    _display_title: RenderableType = ""

    _display_content: RenderableType = ""

    border_style: RenderableType = Reactive("")

    _focused: bool = Reactive(False)

    _content_boundaries: tuple[int, int] = Reactive((0, 0))

    _title: str = Reactive("")

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Title changed to: {value}")

    _content: str = Reactive("")

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str | None):
        self._content = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Content changed to: {value}")

        if self._content_boundaries[0] > 0:
            if len(self.content) < self._content_boundaries[1]:
                self._move_boundaries(-1)
                return
        log(f"{self} - Content boundaries changed to: {self._content_boundaries}")

    # Cursor position is at `cursor` character in `content`
    _cursor: int = Reactive(0)

    @property
    def cursor(self) -> int:
        return self._cursor

    @cursor.setter
    def cursor(self, value: int):
        value = int(value)
        if value < 0:
            raise ValueError("Cursor position cannot be negative value.")
        if value > len(self.content):
            raise ValueError("Cursor position cannot exceed the text length.")
        self._cursor = value
        log(f"{self} - Cursor moved to: {value}")

        if self._content_boundaries[0] > self.cursor:
            self._move_boundaries(self.cursor - self._content_boundaries[0])
        elif self._content_boundaries[1] < self.cursor:
            self._move_boundaries(self.cursor - self._content_boundaries[1])
        elif self._content_boundaries[1] == self.cursor:
            self._move_boundaries(1)

    @property
    def before_cursor(self) -> str:
        return self.content[:self.cursor]

    @property
    def before_cursor_in_boundaries(self) -> str:
        return self.content[self._content_boundaries[0]:self.cursor]

    @property
    def to_cursor(self) -> str:
        return self.content[:self.cursor+1]

    @property
    def at_cursor(self) -> str:
        if self.cursor == len(self.content):
            return ""
        return self.content[self.cursor]

    @property
    def from_cursor(self) -> str:
        return self.content[self.cursor:]

    @property
    def after_cursor(self) -> str:
        return self.content[self.cursor+1:]

    @property
    def after_cursor_in_boundaries(self) -> str:
        return self.content[self.cursor+1:self._content_boundaries[1]]

    _hint: str = Reactive("")

    @property
    def hint(self) -> str:
        return self._hint

    @hint.setter
    def hint(self, value: str):
        self._hint = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Hint changed to: {value}")

    @property
    def value(self) -> str:
        """
        Returns value contained in text input content.
        """
        if self.trim_whitespaces:
            return self.content.strip()
        return self.content

    def __init__(
        self,
        name: str,
        *,
        title: str | None = None,
        content: str = "",
        cursor: int = 0,
        hint: str = "",
        title_align: align.AlignMethod = "center",
        content_align: align.AlignMethod = "left",
        title_style: str = "bold",
        content_style: str = "",
        cursor_style: str = "underline",
        border_style: str = "",
        hint_style: str = "italic bright_black",
        max_width: int | None = None,
        # lines: int = 1,
        trim_whitespaces: bool = True
    ):
        super().__init__(name)
        self.title = title if title is not None else name
        self.hint = hint

        self.max_width = max_width
        # self.lines = lines
        self.lines = 1

        self.content = content
        self.cursor = cursor or 0

        self.title_align = title_align
        self.content_align = content_align

        self.title_style = title_style
        self.hint_style = hint_style
        self.content_style = content_style
        self.cursor_style = cursor_style
        self.border_style = border_style

        self.trim_whitespaces = trim_whitespaces

    def on_show(self, event: events.Show):
        self._content_boundaries = (0, self.size.width-4)

    async def on_key(self, event: events.Key):
        if len(event.key) == 1 and 32 <= ord(event.key) <= 126:
            self.write(event.key)
        else:
            match event.key:
                case "ctrl+h":
                    if self.cursor > 0:
                        self.backspace()
                case "delete":
                    if self.cursor < len(self.content):
                        self.delete()
                case "left":
                    try:
                        self.move_cursor(-1)
                    except ValueError:
                        pass
                case "right":
                    try:
                        self.move_cursor(1)
                    except ValueError:
                        pass
                case "enter":
                    await self.submit()

    def on_focus(self, event: events.Focus):
        self._focused = True

    def on_blur(self, event: events.Blur):
        self._focused = False

    def write(self, value):
        self.content = (
            self.before_cursor + value + self.from_cursor
            if self.content is not None
            else value
        )
        self.move_cursor(1)

    def backspace(self):
        self.content = self.before_cursor[:-1] + self.from_cursor
        self.move_cursor(-1)

    def delete(self):
        self.content = self.before_cursor + self.after_cursor

    def clear(self):
        self.content = ""
        self.cursor = 0

    def move_cursor(self, move: int):
        self.cursor += move

    def _move_boundaries(self, move: int):
        self._content_boundaries = (
            self._content_boundaries[0] + move,
            self._content_boundaries[1] + move
        )
        log(f"{self} - Content boundaries moved to: {self._content_boundaries}")

    def render_title(self):
        self._display_title = (
            f"[{self.title_style}]{self.title}[/{self.title_style}]"
            if self.title_style and self.title
            else self.title
        )
        log(f"{self} - New display_title rendered: {self._display_title}")

    def render_content(self):
        if self._focused or self.content:
            content = [self.at_cursor or " "]
            if self.cursor_style and self._focused:
                content = [
                    f"[{self.cursor_style}]",
                    *content,
                    f"[/{self.cursor_style}]",
                ]
            content = [
                self.before_cursor_in_boundaries,
                *content,
                self.after_cursor_in_boundaries
            ]
            if self.content_style:
                content = [
                    f"[{self.content_style}]",
                    *content,
                    f"[/{self.content_style}]"
                ]
            self._display_content = "".join(content)
        else:
            content = [self.hint]
            if self.hint_style:
                content = [
                    f"[{self.hint_style}]",
                    *content,
                    f"[/{self.hint_style}]",
                ]
            self._display_content = "".join(content)
        log(f"{self} - New display_content rendered: {self._display_content}")

    def render(self) -> RenderableType:
        self.render_title()
        self.render_content()

        return Panel(
            align.Align(
                self._display_content,
                align=self.content_align,
            ),
            title=self._display_title,
            title_align=self.title_align,
            width=self.max_width,
            height=self.lines+2,
            border_style=self.border_style
        )


class PortInput(TextInput):
    @property
    def value(self) -> Port:
        return Port(super().value)


class SubmitButton(base.Button, Submittable):
    async def on_key(self, event: events.Key):
        if event.key == "enter":
            await self.submit()

    async def on_click(self, event: events.Click) -> None:
        event.prevent_default().stop()
        await self.submit()
