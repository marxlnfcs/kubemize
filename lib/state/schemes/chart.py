from lib.config.schemes.helm_release import ProjectConfigHelmRelease
from lib.helpers.common import to_md5


class ProjectStateChart(ProjectConfigHelmRelease):
    def get_checksum(self) -> str:
        return to_md5(self.to_state())
