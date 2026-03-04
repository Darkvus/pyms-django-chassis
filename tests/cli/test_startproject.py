"""Tests for pyms_django CLI utilities."""
from __future__ import annotations

from pyms_django.cli.startproject import _to_module_name


class TestToModuleName:
    def test_simple_name(self) -> None:
        assert _to_module_name("booking") == "booking"

    def test_spaces_become_underscores(self) -> None:
        assert _to_module_name("my module") == "my_module"

    def test_hyphens_become_underscores(self) -> None:
        assert _to_module_name("my-module") == "my_module"

    def test_mixed_spaces_and_hyphens(self) -> None:
        assert _to_module_name("my module-name") == "my_module_name"

    def test_uppercase_lowercased(self) -> None:
        assert _to_module_name("MyModule") == "mymodule"

    def test_leading_trailing_spaces(self) -> None:
        assert _to_module_name("  booking  ") == "booking"

    def test_special_chars_removed(self) -> None:
        assert _to_module_name("my!module@") == "mymodule"

    def test_multiple_consecutive_hyphens(self) -> None:
        assert _to_module_name("a---b") == "a_b"

    def test_multiple_consecutive_spaces(self) -> None:
        assert _to_module_name("a   b") == "a_b"

    def test_empty_string(self) -> None:
        assert _to_module_name("") == ""

    def test_numbers_preserved(self) -> None:
        assert _to_module_name("module2") == "module2"

    def test_underscore_preserved(self) -> None:
        assert _to_module_name("already_snake") == "already_snake"
