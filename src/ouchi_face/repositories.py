from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from .database import get_connection
from .models import Resource, ResourceType


def _row_to_resource(row) -> Resource:
    return Resource(
        id=row["id"],
        name=row["name"],
        resource_type=ResourceType(row["resource_type"]),
        description=row["description"],
        link_url=row["link_url"],
        location=row["location"],
        icon_url=row["icon_url"],
        repo_url=row["repo_url"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def list_resources(*, search: str | None = None, resource_type: ResourceType | None = None) -> list[Resource]:
    query = "SELECT * FROM resources"
    clauses: list[str] = []
    params: list[str] = []

    if search:
        clauses.append("LOWER(name) LIKE ?")
        params.append(f"%{search.lower()}%")

    if resource_type:
        clauses.append("resource_type = ?")
        params.append(resource_type.value)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY updated_at DESC"

    with get_connection() as connection:
        cursor = connection.execute(query, params)
        rows = cursor.fetchall()

    return [_row_to_resource(row) for row in rows]


def get_resource(resource_id: int) -> Optional[Resource]:
    with get_connection() as connection:
        cursor = connection.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return _row_to_resource(row)


def create_resource(
    *,
    name: str,
    resource_type: ResourceType,
    description: str,
    link_url: Optional[str],
    location: Optional[str],
    icon_url: Optional[str],
    repo_url: Optional[str],
) -> Resource:
    now = datetime.utcnow().isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO resources (
                name, resource_type, description, link_url, location, icon_url, repo_url, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                resource_type.value,
                description,
                link_url or None,
                location or None,
                icon_url or None,
                repo_url or None,
                now,
                now,
            ),
        )
        connection.commit()
        resource_id = cursor.lastrowid

    created = get_resource(resource_id)
    assert created is not None
    return created


def update_resource(
    resource_id: int,
    *,
    name: str,
    resource_type: ResourceType,
    description: str,
    link_url: Optional[str],
    location: Optional[str],
    icon_url: Optional[str],
    repo_url: Optional[str],
) -> Optional[Resource]:
    now = datetime.utcnow().isoformat()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE resources
            SET name = ?,
                resource_type = ?,
                description = ?,
                link_url = ?,
                location = ?,
                icon_url = ?,
                repo_url = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                name,
                resource_type.value,
                description,
                link_url or None,
                location or None,
                icon_url or None,
                repo_url or None,
                now,
                resource_id,
            ),
        )
        connection.commit()

    return get_resource(resource_id)


def delete_resource(resource_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        connection.commit()
