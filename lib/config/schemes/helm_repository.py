from lib.helpers.jsons import JSON


class ProjectConfigHelmRepository:
    def __init__(self, data: dict, config):
        self.data: dict = data
        self.config = config

    def get_name(self) -> str:
        return JSON.get("name", self.data)

    def get_url(self) -> str:
        return JSON.get("url", self.data)

    def get_username(self) -> str or None:
        return JSON.get("username", self.data)

    def get_password(self) -> str or None:
        return JSON.get("password", self.data)

    def pass_credentials(self) -> bool:
        return JSON.get("passCredentials", self.data, fallback=False)

    def get_cert_file(self) -> str or None:
        return JSON.get("certFile", self.data)

    def get_key_file(self) -> str or None:
        return JSON.get("keyFile", self.data)

    def get_key_ring(self) -> str or None:
        return JSON.get("keyRing", self.data)

    def get_verify(self) -> bool or None:
        return JSON.get("verify", self.data, fallback=False)

    def to_dict(self) -> dict:
        return self.data