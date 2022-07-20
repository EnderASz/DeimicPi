import typing as t

from rich import align
from rich.console import RenderableType
from rich.panel import Panel
from rich.segment import Segment
from rich.text import Text
from textual import events, log
from textual.reactive import Reactive
from textual.widget import Widget


class TextInput(Widget):
    _display_title: RenderableType = Reactive("")

    _display_content: RenderableType = Reactive("")

    _focused: bool = False

    _title: str = ""

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

    _content: str = ""

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

    # Cursor position is at `cursor` character in `content`
    _cursor: int = 0

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

    @property
    def before_cursor(self) -> str:
        return self.content[:self.cursor]

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

    _hint: str = ""

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
        title: str = None,
        *,
        content: str = "",
        cursor: int = 0,
        hint: str = "",
        title_align: align.AlignMethod = "center",
        content_align: align.AlignMethod = "left",
        title_style: str = "bold",
        content_style: str = "",
        cursor_style: str = "underline",
        hint_style: str = "italic bright_black",
        line_length: int = 10,
        lines: int = 1,
        trim_whitespaces: bool = True
    ):
        super().__init__(title)
        self.title = title if title is not None else ""
        self.hint = hint

        self.line_length = line_length
        self.lines = lines

        self.content = content
        self.cursor = cursor or 0

        self.title_align = title_align
        self.content_align = content_align

        self.title_style = title_style
        self.hint_style = hint_style
        self.content_style = content_style
        self.cursor_style = cursor_style

        self.trim_whitespaces = trim_whitespaces

        self.render_title()
        self.render_content()

    def on_key(self, event: events.Key):
        if len(event.key) == 1 and 32 <= ord(event.key) <= 126:
            self.write(event.key)
        else:
            match event.key:
                case "ctrl+h":
                    if self.cursor > 0:
                        self.backspace()
                case "delete":
                    if self.cursor < len(self.content):
                        self.content = self.before_cursor+self.after_cursor
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

    def on_focus(self, event: events.Focus):
        self._focused = True
        self.render_content()

    def on_blur(self, event: events.Blur):
        self._focused = False
        if self.content == "":
            self._set_content(None)
        self.render_content()

    def write(self, value):
        self.content = (
            self.before_cursor + value + self.from_cursor
            if self.content is not None
            else value
        )
        self.cursor += 1
        self.render_content()

    def backspace(self):
        self.content = self.before_cursor[:-1] + self.from_cursor
        self.cursor -= 1
        self.render_content()

    def move_cursor(self, move):
        self.cursor += move
        self.render_content()

    def render_title(self):
        self._display_title = (
            f"[{self.title_style}]{self.title}[/{self.title_style}]"
            if self.title_style
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
                self.before_cursor,
                *content,
                self.after_cursor
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
        return Panel(
            align.Align(
                self._display_content,
                align=self.content_align,
            ),
            title=self._display_title,
            title_align=self.title_align,
            width=self.line_length+2,
            height=self.lines+2,
        )
