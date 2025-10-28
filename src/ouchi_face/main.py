from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Annotated, Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import ensure_database
from .models import ResourceType
from .repositories import (
    create_resource,
    delete_resource,
    get_resource,
    list_resources,
    update_resource,
)
from .schemas import ResourceCreate, ResourceRead, ResourceUpdate
from .utils import ReadmeFetcher

ensure_database()

app = FastAPI(title="Ouchi Face", version="0.1.0")

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(base_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str | None = None, resource_type: str | None = None) -> HTMLResponse:
    resource_filter = None
    if resource_type in {item.value for item in ResourceType}:
        resource_filter = ResourceType(resource_type)
    resources = list_resources(search=q, resource_type=resource_filter)

    is_filtered = bool(q) or resource_filter is not None
    featured_resources = resources
    grouped_resources: dict[str, list] = {}

    if not is_filtered:
        featured_resources = resources[:6]
        remainder = resources[6:]
        grouped: dict[str, list] = defaultdict(list)
        for item in remainder:
            grouped[item.resource_type.value].append(item)
        grouped_resources = {
            type_value: grouped[type_value]
            for type_value, _ in ResourceType.choices()
            if grouped.get(type_value)
        }

    type_labels = {value: label for value, label in ResourceType.choices()}
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "resources": resources,
            "query": q or "",
            "active_type": resource_type or "all",
            "type_choices": ResourceType.choices(),
            "featured_resources": featured_resources,
            "grouped_resources": grouped_resources,
            "type_labels": type_labels,
            "is_filtered": is_filtered,
        },
    )


@app.get("/resources/new", response_class=HTMLResponse)
def new_resource(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "form.html",
        {
            "action": "/resources",
            "method": "post",
            "resource": None,
            "type_choices": ResourceType.choices(),
            "title": "リソース登録",
            "submit_label": "登録する",
        },
    )


@app.post("/resources")
def create_resource_action(
    name: Annotated[str, Form(...)],
    resource_type: Annotated[str, Form(...)],
    description: Annotated[str, Form(...)],
    link_url: Annotated[Optional[str], Form()] = None,
    location: Annotated[Optional[str], Form()] = None,
    icon_url: Annotated[Optional[str], Form()] = None,
    repo_url: Annotated[Optional[str], Form()] = None,
) -> RedirectResponse:
    try:
        resource_kind = ResourceType(resource_type)
    except ValueError as exc:  # pragma: no cover - handled by HTTP 400
        raise HTTPException(status_code=400, detail="Invalid resource type") from exc

    payload = ResourceCreate(
        name=name,
        resource_type=resource_kind,
        description=description,
        link_url=link_url,
        location=location,
        icon_url=icon_url,
        repo_url=repo_url,
    )
    create_resource(**payload.model_dump())
    return RedirectResponse(url="/", status_code=303)


@app.get("/resources/{resource_id}", response_class=HTMLResponse)
def resource_detail(resource_id: int, request: Request) -> HTMLResponse:
    resource = get_resource(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    readme = None
    if resource.repo_url:
        readme = ReadmeFetcher.fetch(resource.repo_url)
    return templates.TemplateResponse(
        request,
        "detail.html",
        {
            "resource": resource,
            "readme": readme,
        },
    )


@app.get("/resources/{resource_id}/edit", response_class=HTMLResponse)
def edit_resource(resource_id: int, request: Request) -> HTMLResponse:
    resource = get_resource(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return templates.TemplateResponse(
        request,
        "form.html",
        {
            "action": f"/resources/{resource_id}/update",
            "method": "post",
            "resource": resource,
            "type_choices": ResourceType.choices(),
            "title": "リソース編集",
            "submit_label": "更新する",
        },
    )


@app.post("/resources/{resource_id}/update")
def update_resource_action(
    resource_id: int,
    name: Annotated[str, Form(...)],
    resource_type: Annotated[str, Form(...)],
    description: Annotated[str, Form(...)],
    link_url: Annotated[Optional[str], Form()] = None,
    location: Annotated[Optional[str], Form()] = None,
    icon_url: Annotated[Optional[str], Form()] = None,
    repo_url: Annotated[Optional[str], Form()] = None,
) -> RedirectResponse:
    try:
        resource_kind = ResourceType(resource_type)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail="Invalid resource type") from exc

    payload = ResourceUpdate(
        name=name,
        resource_type=resource_kind,
        description=description,
        link_url=link_url,
        location=location,
        icon_url=icon_url,
        repo_url=repo_url,
    )
    updated = update_resource(resource_id, **payload.model_dump())
    if updated is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return RedirectResponse(url=f"/resources/{resource_id}", status_code=303)


@app.post("/resources/{resource_id}/delete")
def delete_resource_action(resource_id: int) -> RedirectResponse:
    delete_resource(resource_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/resources", response_model=list[ResourceRead])
def api_list_resources(q: str | None = None, resource_type: str | None = None) -> list[ResourceRead]:
    resource_filter = None
    if resource_type in {item.value for item in ResourceType}:
        resource_filter = ResourceType(resource_type)
    elif resource_type is not None:
        raise HTTPException(status_code=400, detail="Invalid resource type")
    resources = list_resources(search=q, resource_type=resource_filter)
    return [ResourceRead.from_model(resource) for resource in resources]


@app.get("/api/resources/{resource_id}", response_model=ResourceRead)
def api_get_resource(resource_id: int) -> ResourceRead:
    resource = get_resource(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceRead.from_model(resource)
