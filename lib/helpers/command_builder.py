import subprocess
import typing

from lib.helpers.jsons import JSON


class CommandBuilder:
    def __init__(self, command: str, cwd: str = None):
        self.command: str = command
        self.cwd = cwd if cwd is not None else None
        self.sub_commands: list = []
        self.arguments: dict = {}

    def _format_value(self, value: any) -> str or None:
        if isinstance(value, bool):
            return "" if value else "false"
        elif isinstance(value, str):
            return '"{0}"'.format(value)
        elif isinstance(value, int) or isinstance(value, float):
            return "{0}".format(value)
        elif isinstance(value, dict) or isinstance(value, list):
            return self._format_value(JSON.stringify(value).replace('"', '\\"'))
        return None

    def add_argument(self, name: str, value: any, allow_multi: bool = None) -> typing.Self:
        value = self._format_value(value)
        if value is not None:
            if allow_multi:
                self.arguments[name] = self.arguments[name] if name in self.arguments and isinstance(self.arguments[name], list) else []
                self.arguments[name].append(value)
            else:
                self.arguments[name] = value
        return self

    def add_command(self, *names: str) -> typing.Self:
        for name in names:
            self.sub_commands.append(name)
        return self

    def execute(self):
        yield { "type": "command", "data": self.to_string() }
        process = subprocess.Popen(
            self.to_string(),
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line: yield { "type": "data", "data": stdout_line.strip() }
            stderr_line = process.stderr.readline()
            if stderr_line: yield { "type": "error", "data": stderr_line.strip() }
            if process.poll() is not None and not stdout_line and not stderr_line: break
        process.wait()
        yield { "type": "code", "data": process.returncode }



    def get_args(self) -> typing.List[str]:
        args: typing.List[str] = []
        for item in self.sub_commands:
            args.append(item)
        for key in self.arguments:
            for item in (self.arguments[key] if isinstance(self.arguments[key], list) else [self.arguments[key]]):
                args.append(("{0}={1}" if item else "{0}").format(key, item))
        return args

    def to_string(self) -> str:
        return "{0} {1}".format(self.command, " ".join(self.get_args()))