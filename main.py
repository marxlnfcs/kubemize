import os
import traceback
import typing

from commands.apply import CommandApply
from commands.destroy import CommandDestroy
from commands.new import CommandNew
from commands.plan import CommandPlan
from commands.standalone import CommandStandalone
from commands.template import CommandTemplate
from lib.helpers.commander import Commander, CommanderCommand, CommanderCommandForProject, CommanderCommandStandalone
from lib.helpers.filesystem import resolve_path
from lib.helpers.logging import Logger
from lib.project import Project
from version import VERSION


def create_commands(commands: typing.List[CommanderCommand]):
    # create commander instance
    commander = Commander(
        prog="kubemize",
        description="Templating wrapper to deploy manifests and helm charts",
        version=VERSION,
    )

    # additional commands
    for command in commands:
        # add parser
        parser = commander.get_subparser().add_parser(
            name=command.name,
            help=command.description,
        )

        # append global arguments
        create_global_arguments(parser)

        # run commands function
        command.commands(parser)

    # parse arguments
    args = commander.parse_args()

    # format arguments
    args.project = resolve_path(args.project)
    args.config = resolve_path(args.config, cwd=args.project)
    args.state = resolve_path(args.state, cwd=args.project)

    # return arguments
    return args

def create_global_arguments(commander: Commander):
    # project path
    commander.add_argument(
        "-p", "--project",
        dest="project",
        help="Set an alternative project path",
        default=os.environ.get("KM_PROJECT", default=os.getcwd())
    )

    # project config
    commander.add_argument(
        "-c", "--config",
        dest="config",
        help="Set an alternative project config",
        default=os.environ.get("KM_CONFIG", default="./kubemize.yaml")
    )

    # project lock file
    commander.add_argument(
        "-s", "--state",
        dest="state",
        help="Set an alternative project state file",
        default=os.environ.get("KM_STATE", default="./.kubemize-state.json")
    )

    # set variable
    commander.add_argument(
        "--var",
        dest="variables",
        help="Set variables with json path",
        action="append",
        default=[]
    )

    # no hooks
    commander.add_argument(
        "--no-hooks",
        dest="no_hooks",
        help="Do not execute any hooks",
        action="store_true",
        default=os.environ.get("KM_NO_HOOKS", default=False)
    )

    # debug mode
    commander.add_argument(
        "-d", "--debug",
        dest="debug",
        help="Set an alternative project config",
        action="store_true",
        default=os.environ.get("KM_DEBUG", default=False)
    )

    # helm executable
    commander.add_argument(
        "--helm-executable",
        dest="helm_executable",
        help="Set an alternative path to the helm executable",
        default="helm"
    )

    # kubectl executable
    commander.add_argument(
        "--kubectl-executable",
        dest="kubectl_executable",
        help="Set an alternative path to the kubectl executable",
        default="kubectl"
    )

    # kubeconfig
    commander.add_argument(
        "--kube-config",
        dest="kube_config",
        help="Set an alternative Kubernetes configuration file",
        default=os.environ.get("KUBECONFIG", default="~/.kube/config")
    )

    # kube context
    commander.add_argument(
        "--kube-context",
        dest="kube_context",
        help="Name of the KubeContext to use",
        default=os.environ.get("KUBECONTEXT", default=None)
    )

    # kube context
    commander.add_argument(
        "--kube-insecure",
        dest="kube_insecure",
        help="If true, the Kubernetes API server's certificate will not be checked for validity. This will make your HTTPS connections insecure",
        action="store_true",
        default=False
    )

def main():
    try:

        # create commands
        commands: typing.List[CommanderCommand] = [
            CommandNew(),
            CommandTemplate(),
            CommandStandalone(),
            CommandPlan(),
            CommandApply(),
            CommandDestroy(),
        ]

        # parse arguments
        arguments = create_commands(commands)

        # configure logger
        Logger.debug_enabled = arguments.debug

        # run command
        for command in commands:
            if command.name == arguments.command:
                if isinstance(command, CommanderCommandForProject):
                    return command.run(Project(arguments))
                elif isinstance(command, CommanderCommandStandalone):
                    return command.run(arguments)

    except Exception as ex:
        Logger.fatal([str(ex), traceback.format_exc()] if Logger.debug_enabled else str(ex))


main()
