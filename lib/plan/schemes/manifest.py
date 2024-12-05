from lib.state.schemes.manifest import ProjectStateManifest


class ProjectPlanManifest:
    def __init__(self, action: str, manifest: ProjectStateManifest, manifest_current: ProjectStateManifest or None = None):
        self.action: str = action
        self.manifest: ProjectStateManifest = manifest
        self.manifest_current: ProjectStateManifest or None = manifest_current

    def get_action(self) -> str:
        return self.action.strip().lower()

    def is_action(self, *actions: str) -> bool:
        for action in actions:
            if action.strip().lower() == self.get_action():
                return True
        return False

    def get_manifest(self) -> ProjectStateManifest:
        return self.manifest

    def get_current_manifest(self) -> ProjectStateManifest or None:
        return self.manifest_current

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "manifest": self.manifest,
            "manifest_current": self.manifest_current,
        }