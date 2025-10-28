from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from .models import Resource, ResourceType


class ResourceBase(BaseModel):
    name: str
    resource_type: ResourceType
    description: str
    link_url: Optional[str] = None
    location: Optional[str] = None
    icon_url: Optional[str] = None
    repo_url: Optional[str] = None

    @field_validator("link_url", "icon_url", "repo_url", mode="before")
    @classmethod
    def empty_to_none(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(ResourceBase):
    pass


class ResourceRead(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, resource: Resource) -> "ResourceRead":
        return cls(
            id=resource.id,
            name=resource.name,
            resource_type=resource.resource_type,
            description=resource.description,
            link_url=resource.link_url,
            location=resource.location,
            icon_url=resource.icon_url,
            repo_url=resource.repo_url,
            created_at=resource.created_at,
            updated_at=resource.updated_at,
        )
