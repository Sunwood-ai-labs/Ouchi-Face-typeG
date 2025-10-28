from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ResourceType(str, Enum):
    APP = "app"
    DATASET = "dataset"
    REPOSITORY = "repository"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [
            (cls.APP.value, "アプリ"),
            (cls.DATASET.value, "データセット"),
            (cls.REPOSITORY.value, "リポジトリ"),
        ]


@dataclass(slots=True)
class Resource:
    id: int
    name: str
    resource_type: ResourceType
    description: str
    link_url: Optional[str]
    location: Optional[str]
    icon_url: Optional[str]
    repo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
