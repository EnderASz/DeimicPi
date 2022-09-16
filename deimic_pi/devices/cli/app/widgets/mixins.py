from textual import log
from textual.reactive import Reactive
from rich.console import StyleType
from rich.box import Box, ROUNDED as ROUNDED_BOX


class TitleMixin:
    _title: str = Reactive("")
    title_style: StyleType = Reactive("bold")

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str | None):
        self._title = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Title changed to: {value}")

    _styled_title: str = ""

    @property
    def styled_title(self):
        return (
            f"[{self.title_style}]{self.title}[/{self.title_style}]"
            if self.title_style and self.title
            else self.title
        )

    def __init__(
        self,
        title: str | None,
        *,
        title_style: StyleType = "bold",
    ):
        self.title = title
        self.title_style = title_style


class SubtitleMixin(TitleMixin):
    _subtitle: str = Reactive("")
    subtitle_style: StyleType = Reactive("")

    @property
    def subtitle(self):
        return self._title

    @subtitle.setter
    def subtitle(self, value: str | None):
        self._subtitle = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Title changed to: {value}")

    @property
    def styled_subtitle(self):
        return (
            f"[{self.subtitle_style}]{self.subtitle}[/{self.subtitle_style}]"
            if self.subtitle_style and self.subtitle
            else self.subtitle
        )

    full_title_style: StyleType = Reactive("")

    @property
    def full_title(self) -> str:
        return (
            f"{self.title} - {self.subtitle}"
            if self.subtitle
            else self.title
        )

    @property
    def styled_full_title(self):
        styled_full_title = (
            f"{self.styled_title} - {self.styled_subtitle}"
            if self.subtitle
            else self.title
        )
        if self.full_title_style and self.full_title:
            styled_full_title = f"[{self.full_title_style}]{styled_full_title}[/{self.full_title_style}]"
        return styled_full_title

    def __init__(
        self,
        title: str | None,
        subtitle: str | None,
        *,
        title_style: StyleType = "bold",
        subtitle_style: StyleType = "",
        full_title_style: StyleType = ""
    ):
        TitleMixin.__init__(
            self,
            title,
            title_style=title_style
        )

        self.subtitle = subtitle
        self.subtitle_style = subtitle_style

        self.full_title_style = full_title_style


class BorderMixin:
    border_style: StyleType = Reactive("")
    box: Box = Reactive(ROUNDED_BOX)

    def __init__(
        self,
        box: Box = ROUNDED_BOX,
        *,
        border_style: StyleType = ""
    ):
        self.box = box
        self.border_style = border_style


class TextContentMixin:
    _content: str = Reactive("")
    content_style: StyleType = Reactive("")

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

    @property
    def styled_content(self) -> str:
        return (
            f"[{self.content_style}]{self.content}[/{self.content_style}]"
            if self.content_style and self.content
            else self.content
        )

    def __init__(
        self,
        initial_content: str | None = None,
        *,
        content_style: StyleType = ""
    ):
        self.content = initial_content
        self.content_style = content_style

    def write(self, value):
        self.content = (
            self.content + value
            if self.content is not None
            else value
        )

    def clear(self):
        self.content = ""


class TextContentCursorMixin(TextContentMixin):
    # Cursor position is at `cursor` character in `content`
    _cursor: int = Reactive(0)
    cursor_style: StyleType = Reactive("underline")
    _cursor_visibility: bool = Reactive(False)

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
    def styled_cursor(self) -> str:
        if not self.cursor_visibility:
            return self.at_cursor
        cursor_character = self.at_cursor or ' '
        return (
            f"[{self.cursor_style}]{cursor_character}[/{self.cursor_style}]"
            if self.cursor_style
            else cursor_character
        )

    @property
    def before_cursor(self) -> str:
        return self.content[:self.cursor]

    @property
    def to_cursor(self) -> str:
        return self.content[:self.cursor + 1]

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
        return self.content[self.cursor + 1:]

    @property
    def cursor_visibility(self) -> bool:
        return self._cursor_visibility

    def __init__(
        self,
        initial_content: str | None = None,
        cursor_initial_position: int = 0,
        cursor_visibility: bool = False,
        *,
        content_style: StyleType = "",
        cursor_style: StyleType = "underline",
    ):
        super().__init__(initial_content, content_style=content_style)
        self.cursor = cursor_initial_position
        if cursor_visibility:
            self.show_cursor()
        self.cursor_style = cursor_style

    @property
    def styled_content(self) -> str:
        if not self.cursor_visibility:
            return super().styled_content
        cursor_character = self.styled_cursor
        styled_content = f"{self.before_cursor}{cursor_character}{self.after_cursor}"
        if self.content_style:
            styled_content = f"[{self.content_style}]{styled_content}[/{self.content_style}]"
        return styled_content

    def move_cursor(self, move: int):
        self.cursor += move

    def set_cursor_on_start(self):
        self.cursor = 0

    def set_cursor_on_end(self):
        self.cursor = len(self.content)

    def show_cursor(self):
        self._cursor_visibility = True

    def hide_cursor(self):
        self._cursor_visibility = False

    def write(self, value):
        self.content = (
            self.before_cursor + value + self.from_cursor
            if self.content is not None
            else value
        )
        self.move_cursor(len(value))

    def clear(self):
        super().clear()
        self.cursor = 0

    def delete(self, n=1):
        self.content = self.before_cursor + self.after_cursor[n-1:]

    def backspace(self, n=1):
        self.content = self.before_cursor[:-n] + self.from_cursor
        self.move_cursor(-n)


class TextHintMixin:
    _hint: str = Reactive("")
    hint_style: StyleType = Reactive("italic bright_black")

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
    def styled_hint(self) -> str:
        return (
            f"[{self.hint_style}]{self.hint}[{self.hint_style}]"
            if self.hint_style
            else self.hint
        )

    def __init__(
        self,
        hint: str,
        *,
        hint_style: StyleType = "italic bright_black"
    ):
        self.hint = hint
        self.hint_style = hint_style
