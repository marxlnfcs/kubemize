from typing import TYPE_CHECKING

from lib.helpers.command_builder import CommandBuilder
from lib.helpers.filesystem import get_extension, resolve_path
from lib.helpers.logging import Logger

if TYPE_CHECKING:
    from lib.project import Project

class ProjectHooksRunner:
    def __init__(self, project: "Project"):
        self.project: "Project" = project

    def _get_executable_from_script(self, script: str) -> str or None:
        ext = get_extension(script, cwd=self.project.get_project_dir())
        if ext == ".js":
            return "node"
        elif ext == ".sh":
            return "bash"
        elif ext == ".py":
            return "python"
        return None


    def _run_hook(self, type: str, script: str, logger_indent: int = 0) -> bool:
        # skip if hooks are disabled
        if self.project.arguments.no_hooks:
            return True
        # resolve script
        script = resolve_path(script, cwd=self.project.get_project_dir())
        # get executable
        executable = self._get_executable_from_script(script)
        # create command builder
        builder = CommandBuilder(executable if executable else script, cwd=self.project.get_project_dir())
        # add script as command
        if executable:
            builder.add_command('"{0}"'.format(script))
        # log information
        Logger.info("Running {0} hook '{1}'...".format(type, script))
        # run hook
        for line in builder.execute():
            if line["type"] == "command":
                Logger.debug("$ {0}".format(line["data"]), indent=logger_indent+1)
                Logger.debug("-----", indent=logger_indent+1)
            elif line["type"] == "data":
                Logger.debug(line["data"], indent=logger_indent+1)
            elif line["type"] == "error":
                Logger.error(line["data"], indent=logger_indent+1)
            elif line["type"] == "code":
                if line["data"] != 0:
                    return False
        return True

    def run_hooks_pre_all(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_pre_all():
            if not self._run_hook("PreAll", hook, logger_indent):
                return False
        return True

    def run_hooks_post_all(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_post_all():
            if not self._run_hook("PostAll", hook, logger_indent):
                return False
        return True

    def run_hooks_pre_apply(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_pre_apply():
            if not self._run_hook("PreApply", hook, logger_indent):
                return False
        return True

    def run_hooks_post_apply(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_post_apply():
            if not self._run_hook("PostApply", hook, logger_indent):
                return False
        return True

    def run_hooks_pre_template(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_pre_template():
            if not self._run_hook("PreTemplate", hook, logger_indent):
                return False
        return True

    def run_hooks_post_template(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_post_template():
            if not self._run_hook("PostTemplate", hook, logger_indent):
                return False
        return True

    def run_hooks_pre_standalone(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_pre_standalone():
            if not self._run_hook("PreStandalone", hook, logger_indent):
                return False
        return True

    def run_hooks_post_standalone(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_post_standalone():
            if not self._run_hook("PostStandalone", hook, logger_indent):
                return False
        return True
    
    def run_hooks_pre_plan(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_pre_plan():
            if not self._run_hook("PrePlan", hook, logger_indent):
                return False
        return True

    def run_hooks_post_plan(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_post_plan():
            if not self._run_hook("PostPlan", hook, logger_indent):
                return False
        return True
    
    def run_hooks_pre_destroy(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_pre_destroy():
            if not self._run_hook("PreDestroy", hook, logger_indent):
                return False
        return True

    def run_hooks_post_destroy(self, logger_indent: int = 0) -> bool:
        for hook in self.project.config.get_hooks_post_destroy():
            if not self._run_hook("PostDestroy", hook, logger_indent):
                return False
        return True
