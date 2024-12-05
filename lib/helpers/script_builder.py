import typing

from lib.helpers.filesystem import resolve_path


class ScriptBuilder:
    def __init__(self, platform: str, linux_shell: str = None, header_comments: typing.List[str] = None):
        self.platform: str = platform.strip().lower()
        self.platform_linebreak: str = "\n" if platform == "windows" else "\n"
        self.linux_shell: str = (linux_shell or "/bin/bash").strip()
        self.lines: typing.List[str] = []
        if header_comments:
            for comment in header_comments:
                self._add_comment(comment)

    def _is_linux(self) -> bool:
        return self.platform == "linux"

    def _is_windows(self) -> bool:
        return self.platform == "windows"

    def _append(self, content: str) -> typing.Self:
        self.lines.append(content)
        return self

    def _prepend(self, content: str) -> typing.Self:
        self.lines.insert(0, content)
        return self

    def _add_comment(self, comment: str or typing.List[str] or None) -> typing.Self:
        if comment is not None:
            for line in (comment if isinstance(comment, list) else [comment]):
                if self._is_windows():
                    self._append(":: {0}".format(line))
                elif self._is_linux():
                    self._append("# {0}".format(line))
        return self

    def _add_print(self, content: str or typing.List[str] or None) -> typing.Self:
        if content is not None:
            for line in (content if isinstance(content, list) else [content]):
                if line is not None:
                    if self._is_windows():
                        self._append("echo {0}".format(line))
                    elif self._is_linux():
                        self._append("echo \"{0}\"".format(line))
        return self

    def _add_header(self):
        if self._is_windows():
            if "@echo off" not in self.lines:
                self._prepend("")
                self._prepend("@echo off")
        elif self._is_linux():
            header = "#!{0}".format(self.linux_shell)
            if header not in self.lines:
                self._prepend("")
                self._prepend(header)

    def add(self, content: str or typing.List[str], prints: str or typing.List[str] = None, comment: str or typing.List[str] = None) -> typing.Self:
        self._add_comment(comment)
        self._add_print(prints)
        for line in (content if isinstance(content, list) else [content]):
            self._append(line)
        return self

    def add_comment(self, comment: str or typing.List[str]) -> typing.Self:
        self._add_comment(comment)
        return self

    def add_print(self, content: str or typing.List[str]) -> typing.Self:
        self._add_print(content)
        return self

    def add_sleep(self, seconds: int = 1, prints: str or typing.List[str] = None) -> typing.Self:
        self.add_print(prints)
        if self._is_windows():
            self.add("TIMEOUT /T {0}".format(str(seconds)))
        elif self._is_linux():
            self.add("sleep {0}".format(str(seconds)))
        return self

    def newline(self, count: int = None) -> typing.Self:
        for i in range(count if count is not None and count > 0 else 1):
            self.add("")
        return self

    def get_lines(self) -> typing.List[str]:
        return self.lines

    def save(self, filename: str, cwd: str = None) -> str:
        path = resolve_path("{0}.{1}".format(filename, "bat" if self._is_windows() else "sh"), cwd=cwd)
        with open(path, "w") as f:
            self._add_header()
            for line in self.lines:
                f.write(line + self.platform_linebreak)
        return path
