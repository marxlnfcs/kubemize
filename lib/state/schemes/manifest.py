from lib.config.schemes.kubectl_manifest import ProjectConfigKubectlManifest
from lib.helpers.common import to_md5


class ProjectStateManifest(ProjectConfigKubectlManifest):
    def get_checksum(self) -> str:
        return to_md5(self.to_state())