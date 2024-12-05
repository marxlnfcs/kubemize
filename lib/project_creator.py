from lib.errors.project_already_exists import ProjectAlreadyExistsError
from lib.helpers.filesystem import resolve_path, create_dir, file_exists
from lib.helpers.logging import Logger
from lib.helpers.yamls import YAML


class ProjectCreator:
    def __init__(self, project_dir: str, project_config: str):
        # set global variables
        self.project_dir: str = project_dir
        self.project_config: str = project_config
        # set example directories
        self.dir_project = resolve_path(self.project_dir)
        self.dir_bases = resolve_path("bases", cwd=self.project_dir)
        self.dir_bases_manifests = resolve_path("manifests", cwd=self.dir_bases)
        self.dir_manifests = resolve_path("manifests", cwd=self.project_dir)
        self.dir_charts = resolve_path("charts", cwd=self.project_dir)

    def create(self, silent: bool = False):
        # fail if project exists
        if file_exists(self.project_config, cwd=self.project_dir):
            raise ProjectAlreadyExistsError(self.project_dir)
        # log information
        Logger.info("Creating project under {0}...".format(self.dir_project))
        # create directories
        self._create_directories()
        # create bases
        self._create_bases()
        # create charts
        self._create_charts()
        # create manifests
        self._create_manifests()
        # create project file
        self._create_project_file()
        pass

    def _create_directories(self):
        Logger.info("- Creating directories...")
        for dir in [self.dir_project, self.dir_bases, self.dir_bases_manifests, self.dir_manifests, self.dir_charts]:
            create_dir(dir)
            Logger.success("- Created directory '{0}'...".format(dir), indent=1)

    def _create_bases(self):
        # log information
        Logger.info("- Creating example files under '{0}'...".format(self.dir_bases))
        # create namespace
        self._create_yaml(type="namespace manifest example", file="namespace.yaml", cwd=self.dir_bases_manifests, content={
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "{{ vars.namespace }}"
            }
        })
        # create variables
        self._create_yaml(type="variables base example", file="variables.yaml", cwd=self.dir_bases, content={
            "variables": {
                "namespace": "testing-namespace"
            }
        })
        # create repositories
        self._create_yaml(type="repositories base example", file="repositories.yaml", cwd=self.dir_bases, content={
            "helm": {
                "repositories": [
                    {
                        "name": "example-repository",
                        "url": "https://charts.example.com/",
                    }
                ]
            }
        })
        # create manifests
        self._create_yaml(type="manifests base example", file="manifests.yaml", cwd=self.dir_bases, content={
            "kubectl": {
                "manifests": [
                    "manifests/**/*.{yml,yaml}"
                ]
            }
        })
        # create base
        self._create_yaml(type="base example", file="kubemize.yaml", cwd=self.dir_bases, content={
            "extends": [
                "variables.yaml",
                "repositories.yaml",
                "manifests.yaml",
            ]
        })

    def _create_charts(self):
        # log information
        Logger.info("- Creating example chart files under '{0}'...".format(self.dir_charts))
        # create example chart values
        self._create_yaml(type="values example", file="example-values.yaml", cwd=self.dir_charts, content={
            "foo": {
                "bar": {
                    "enabled": True
                }
            }
        })

    def _create_manifests(self):
        # log information
        Logger.info("- Creating example manifests under '{0}'...".format(self.dir_manifests))
        # create example config map
        self._create_yaml(type="config map example", file="example-configmap.yaml", cwd=self.dir_manifests, content={
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "example-configmap",
                "namespace": "{{ vars.namespace }}",
            },
            "data": {
                "foo": "bar"
            }
        })

    def _create_project_file(self):
        # log information
        Logger.info("- Creating project files under '{0}'...".format(self.dir_project))
        # create project file
        self._create_yaml(type="project file", file="kubemize.yaml", cwd=self.dir_project, content={
            "extends": [
                "bases/kubemize.yaml",
            ],
            "helm": {
                "releases": [
                    {
                        "name": "example",
                        "chart": "example-repository/example-chart",
                        "namespace": "{{ vars.namespace }}",
                        "values": [
                            "charts/example-values.yaml",
                            {
                                "foo": {
                                    "bar": {
                                        "name": "example-chart"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "name": "example-oci",
                        "chart": "oci://charts.example.com/example-chart",
                        "namespace": "{{ vars.namespace }}",
                        "values": [
                            "charts/example-values.yaml",
                            {
                                "foo": {
                                    "bar": {
                                        "name": "example-chart-oci"
                                    }
                                }
                            }
                        ]
                    }
                ]
            },
            "kubectl": {
                "manifests": [
                    "manifests/**/*.{yml,yaml}"
                ]
            }
        })

    def _create_yaml(self, type: str, file: str, content: any, cwd: str, logger_indent: int = 1):
        YAML.to_file(file, obj=content, cwd=cwd)
        Logger.success("- Created {0} under '{1}'...".format(type, resolve_path(file, cwd)), indent=logger_indent)
