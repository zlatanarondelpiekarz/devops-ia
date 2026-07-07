import os
from dataclasses import dataclass


@dataclass
class GitLabAuth:
    url: str
    token: str
    project_id: str

    @classmethod
    def from_env(cls) -> "GitLabAuth":
        url = os.getenv("GITLAB_URL", "https://gitlab.com")
        project_id = os.getenv("GITLAB_PROJECT_ID", "")
        if not project_id:
            raise ValueError("GITLAB_PROJECT_ID must be set in environment")
        return cls(url=url, token=_get_token(), project_id=project_id)

    @classmethod
    def from_settings(cls, settings: "Settings") -> "GitLabAuth":
        return cls(
            url=settings.gitlab_url,
            token=settings.gitlab_token,
            project_id=settings.gitlab_project_id,
        )


def _get_token() -> str:
    token = os.getenv("GITLAB_TOKEN")
    if token:
        return token
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITLAB_TOKEN="):
                    return line.split("=", 1)[1]
    raise ValueError(
        "GITLAB_TOKEN must be set in environment or .env file"
    )
