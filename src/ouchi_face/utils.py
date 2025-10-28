from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests
from markdown import markdown


@dataclass(slots=True)
class ReadmeContent:
    source: str
    html: str


class ReadmeFetcher:
    @staticmethod
    def fetch(repo_url: str) -> Optional[ReadmeContent]:
        parser = urlparse(repo_url)
        if not parser.scheme:
            return None

        if "github" in parser.netloc:
            content = ReadmeFetcher._fetch_github(parser)
        elif "forgejo" in parser.netloc or "gitea" in parser.netloc:
            content = ReadmeFetcher._fetch_forgejo(parser)
        else:
            content = None

        if content is None:
            return None

        return ReadmeContent(source=repo_url, html=markdown(content))

    @staticmethod
    def _fetch_github(parser) -> Optional[str]:
        path = parser.path.strip("/")
        if not path:
            return None
        parts = path.split("/")
        if len(parts) < 2:
            return None
        owner, repo, *rest = parts
        branch = "main"
        if rest:
            if rest[0] in {"blob", "tree"}:
                branch = rest[1] if len(rest) > 1 else branch
            else:
                branch = rest[0]
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException:
            return None
        if response.status_code != 200:
            return None
        return response.text

    @staticmethod
    def _fetch_forgejo(parser) -> Optional[str]:
        # Forgejo/Gitea raw endpoint is typically /{owner}/{repo}/raw/branch/README.md
        path = parser.path.strip("/")
        if not path:
            return None
        parts = path.split("/")
        if len(parts) < 2:
            return None
        owner, repo, *rest = parts
        branch = "main"
        if rest:
            branch = rest[-1]
        url = f"{parser.scheme}://{parser.netloc}/{owner}/{repo}/raw/{branch}/README.md"
        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException:
            return None
        if response.status_code != 200:
            return None
        return response.text
