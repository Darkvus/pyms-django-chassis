"""Tests for pyms_django views."""
from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    from pathlib import Path

import pytest
from rest_framework.test import APIRequestFactory

from pyms_django.views import DependenciesTreeView, VersioningView


@pytest.fixture
def rf() -> APIRequestFactory:
    return APIRequestFactory()


class TestVersioningView:
    def test_returns_version_from_pyproject(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "2.5.0"\n')
        request = rf.get("/version/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = VersioningView.as_view()
            response = view(request)
        assert response.status_code == 200
        assert response.data["version"] == "2.5.0"  # type: ignore[attr-defined]

    def test_falls_back_to_settings_when_no_pyproject(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        request = rf.get("/version/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = VersioningView.as_view()
            response = view(request)
        assert response.status_code == 200
        assert response.data["version"] == "0.0.1-test"  # type: ignore[attr-defined]

    def test_falls_back_when_pyproject_has_no_version(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = \"my-service\"\n")
        request = rf.get("/version/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = VersioningView.as_view()
            response = view(request)
        assert response.data["version"] == "0.0.1-test"  # type: ignore[attr-defined]

    def test_falls_back_on_invalid_toml(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("NOT VALID TOML ][[[")
        request = rf.get("/version/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = VersioningView.as_view()
            response = view(request)
        assert response.data["version"] == "0.0.1-test"  # type: ignore[attr-defined]


class TestDependenciesTreeView:
    def test_returns_dependencies(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = ["django>=4.2", "djangorestframework>=3.15"]\n')
        request = rf.get("/dependencies/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = DependenciesTreeView.as_view()
            response = view(request)
        assert response.status_code == 200
        assert "django>=4.2" in response.data["dependencies"]  # type: ignore[attr-defined]

    def test_returns_empty_when_no_pyproject(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        request = rf.get("/dependencies/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = DependenciesTreeView.as_view()
            response = view(request)
        assert response.data == {"dependencies": {}}  # type: ignore[attr-defined]

    def test_returns_empty_on_invalid_toml(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("INVALID ]]]]")
        request = rf.get("/dependencies/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = DependenciesTreeView.as_view()
            response = view(request)
        assert response.data == {"dependencies": {}}  # type: ignore[attr-defined]

    def test_returns_empty_list_when_no_dependencies_key(self, rf: APIRequestFactory, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = \"svc\"\n")
        request = rf.get("/dependencies/")
        with patch("pyms_django.views.Path.cwd", return_value=tmp_path):
            view = DependenciesTreeView.as_view()
            response = view(request)
        assert response.data["dependencies"] == []  # type: ignore[attr-defined]
