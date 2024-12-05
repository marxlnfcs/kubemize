import typing

from colors1 import colors

from lib.helpers.jsons import JSON


class Logger:
    debug_enabled: bool = False

    @staticmethod
    def colors():
        return colors

    @staticmethod
    def _create_message(message: str, message_params: dict|list = None, level: str = None, indent: int = 0) -> str:
        msg = []
        if level is not None:
            msg.append("{0}:{1}".format(level.upper(), (" " * (8 - len(level)))))
        if indent is not None and indent > 0:
            msg.append((" " * indent))
        if message_params is not None:
            message = message.format(*message_params if isinstance(message_params, dict) else message_params)
        msg.append(message)
        return " ".join(msg)

    @staticmethod
    def _print_message(message: str or typing.List[str], message_params: dict | list = None, level: str = None, colors_list: typing.List[any] = None, indent: int = 0):
        lines = []
        for line in message.split("\n") if isinstance(message, str) else message:
            for line in line.split("\n"):
                lines.append(line)
        for index in range(len(lines)):
            # format indent
            new_indent = indent if indent is not None else 0
            if level is not None and index > 0:
                new_indent = new_indent + len(level)
            if index > 0:
                new_indent = new_indent + 6
            # create message
            msg = Logger._create_message(message=lines[index], message_params=message_params, level=level if index == 0 else None, indent=new_indent)
            # apply color
            if colors_list is not None:
                for color in colors_list:
                    msg = color("") + msg + colors.end("")
            # print message
            print(msg)

    @staticmethod
    def _print_dict(obj: dict, level: str = None, colors_list: typing.List[any] = None, indent: int = 0):
        key_length = len(max(obj, key=len)) + 4
        for key in obj:
            value = obj[key]
            key = "{0} {1} : ".format(key, ("." * (key_length - len(key))))
            if isinstance(value, bool):
                value = "{0}".format("true" if value else "false")
            elif value is None:
                value = ""
            elif isinstance(value, dict) or isinstance(value, list):
                value = JSON.stringify(value, 2).split("\n")
            if not isinstance(value, list):
                Logger._print_message(key + colors.end(value), level=level, colors_list=colors_list, indent=indent)
            else:
                for index in range(len(value)):
                    message = key + colors.end(value[index]) if index == 0 else ((" " * (len(key) - 2)) + ": ") + colors.end(value[index])
                    Logger._print_message(message, level=level, colors_list=colors_list, indent=indent)


    @staticmethod
    def log(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        return Logger._print_message(message=message, message_params=message_params, indent=indent)

    @staticmethod
    def log_dict(obj: dict, indent: int = None):
        return Logger._print_dict(obj=obj, indent=indent)

    @staticmethod
    def info(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        return Logger._print_message(message=message, message_params=message_params, level="INFO", colors_list=[colors.terminalBlue], indent=indent)

    @staticmethod
    def info_dict(obj: dict, indent: int = None):
        return Logger._print_dict(obj=obj, level="INFO", colors_list=[colors.terminalBlue], indent=indent)

    @staticmethod
    def success(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        return Logger._print_message(message=message, message_params=message_params, level="SUCCESS", colors_list=[colors.terminalGreen], indent=indent)

    @staticmethod
    def success_dict(obj: dict, indent: int = None):
        return Logger._print_dict(obj=obj, level="SUCCESS", colors_list=[colors.terminalGreen], indent=indent)

    @staticmethod
    def warn(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        return Logger._print_message(message=message, message_params=message_params, level="WARN", colors_list=[colors.terminalYellow], indent=indent)

    @staticmethod
    def warn_dict(obj: dict, indent: int = None):
        return Logger._print_dict(obj=obj, level="WARN", colors_list=[colors.terminalYellow], indent=indent)

    @staticmethod
    def error(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        return Logger._print_message(message=message, message_params=message_params, level="ERROR", colors_list=[colors.terminalRed], indent=indent)

    @staticmethod
    def error_dict(obj: dict, indent: int = None):
        return Logger._print_dict(obj=obj, level="ERROR", colors_list=[colors.terminalRed], indent=indent)

    @staticmethod
    def fatal(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        return Logger._print_message(message=message, message_params=message_params, level="FATAL", colors_list=[colors.terminalBrightRed], indent=indent)

    @staticmethod
    def fatal_dict(obj: dict, indent: int = None):
        return Logger._print_dict(obj=obj, level="FATAL", colors_list=[colors.terminalBrightRed], indent=indent)

    @staticmethod
    def debug(message: str or typing.List[str], message_params: dict | list = None, indent: int = None):
        if Logger.debug_enabled:
            return Logger._print_message(message=message, message_params=message_params, level="DEBUG", colors_list=[colors.terminalMagenta], indent=indent)

    @staticmethod
    def debug_dict(obj: dict, indent: int = None):
        if Logger.debug_enabled:
            return Logger._print_dict(obj=obj, level="DEBUG", colors_list=[colors.terminalMagenta], indent=indent)