"""Interactive TUI wizard for pyms-django startproject using Textual."""
from __future__ import annotations

from typing import Final

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, RadioButton, RadioSet, Rule, Static, Switch

from pyms_django.cli.types import ProjectConfig

PYTHON_VERSIONS: Final[list[str]] = ["3.11", "3.12", "3.13", "3.14"]
EXTRAS: Final[list[str]] = ["monitoring", "aws", "tenant", "docs", "restql", "import-export", "dev-tools", "all"]
SELECTABLE_EXTRAS: Final[list[str]] = [e for e in EXTRAS if e != "all"]

EXTRAS_INFO: Final[dict[str, str]] = {
    "monitoring":    "OpenTelemetry tracing & OTLP export",
    "aws":           "AWS SDK — Secrets Manager, S3, etc.",
    "tenant":        "Schema-based tenant isolation (django-tenants + PostgreSQL)",
    "docs":          "OpenAPI / Swagger docs (drf-spectacular)",
    "restql":        "Dynamic field filtering via query params",
    "import-export": "CSV & XLSX import / export",
    "dev-tools":     "Debug toolbar & django-extensions",
    "all":           "All of the above, bundled",
}

_COMMON_CSS = """
Screen {
    background: $surface;
}
.wizard-title {
    text-style: bold;
    color: $accent;
    margin: 1 2;
}
.section-label {
    text-style: bold;
    margin: 1 2 0 2;
}
.field-row {
    margin: 0 2 1 2;
}
.button-row {
    dock: bottom;
    height: 3;
    margin: 1 2;
    align: right middle;
}
.button-row Button {
    margin: 0 1;
}
.summary-box {
    margin: 1 2;
    padding: 1;
    border: round $accent;
    height: auto;
}
.error-label {
    color: $error;
    margin: 0 2;
}

/* ── FeaturesScreen ──────────────────────────────────────────── */
.mt-panel {
    border: round $primary-darken-2;
    margin: 0 2 0 2;
    padding: 0 1;
    height: 5;
}
.mt-row {
    height: 3;
    align: left middle;
}
.mt-title {
    text-style: bold;
    margin: 0 0 0 1;
}
.mt-hint {
    color: $text-muted;
    margin: 0 0 0 1;
}
.extras-hdr {
    margin: 1 2 0 2;
    height: 1;
}
.extras-hdr-label {
    text-style: bold;
    width: auto;
}
.extras-counter {
    width: 1fr;
    text-align: right;
    color: $accent;
}
.extras-scroll {
    margin: 0 2 0 2;
    border: round $primary-darken-2;
    height: 1fr;
    min-height: 8;
}
.extra-row {
    height: 3;
    padding: 0 1;
    align: left middle;
}
.extra-row:hover {
    background: $boost;
}
.extra-desc {
    width: 1fr;
    color: $text-muted;
    margin: 0 0 0 2;
}
.all-row {
    height: 3;
    padding: 0 1;
    align: left middle;
}
.all-row:hover {
    background: $boost;
}
"""


class ProjectSetupScreen(Screen[dict]):  # type: ignore[type-arg]
    """Step 1 — Package manager, service name, base path, Python version."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    CSS = _COMMON_CSS

    def __init__(self, project_name: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Step 1 of 3 — Project Setup", classes="wizard-title")

        yield Label("Package manager", classes="section-label")
        with RadioSet(id="pkg_manager"):
            yield RadioButton("uv", value=True, id="pkg_uv")
            yield RadioButton("poetry", id="pkg_poetry")

        yield Label("SERVICE_NAME", classes="section-label")
        yield Input(
            placeholder=f"ms-{self._project_name}",
            value=f"ms-{self._project_name}",
            id="service_name",
            classes="field-row",
        )

        yield Label("BASE_PATH", classes="section-label")
        yield Input(
            placeholder=f"/{self._project_name}",
            value=f"/{self._project_name}",
            id="base_path",
            classes="field-row",
        )

        yield Label("Python version", classes="section-label")
        with RadioSet(id="py_version"):
            for i, v in enumerate(PYTHON_VERSIONS):
                yield RadioButton(v, value=(i == 1), id=f"py_{v.replace('.', '_')}")

        yield Static("", id="error_msg", classes="error-label")

        with Horizontal(classes="button-row"):
            yield Button("Next →", variant="primary", id="btn_next")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "btn_next":
            return

        service_name = str(self.query_one("#service_name", Input).value).strip()
        base_path = str(self.query_one("#base_path", Input).value).strip()

        if not service_name or not base_path:
            self.query_one("#error_msg", Static).update("SERVICE_NAME and BASE_PATH cannot be empty.")
            return

        pkg_set = self.query_one("#pkg_manager", RadioSet)
        package_manager = "uv" if pkg_set.pressed_index == 0 else "poetry"

        py_set = self.query_one("#py_version", RadioSet)
        python_version = PYTHON_VERSIONS[py_set.pressed_index]

        self.dismiss({
            "package_manager": package_manager,
            "service_name": service_name,
            "base_path": base_path,
            "python_version": python_version,
        })


class FeaturesScreen(Screen[dict]):  # type: ignore[type-arg]
    """Step 2 — Multi-tenancy and extras."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    CSS = _COMMON_CSS

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._syncing = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Step 2 of 3 — Features", classes="wizard-title")

        # ── Multi-tenancy ─────────────────────────────────────────────
        with Vertical(classes="mt-panel"):
            with Horizontal(classes="mt-row"):
                yield Switch(value=False, id="multitenant")
                with Vertical():
                    yield Label("Enable multi-tenant support", classes="mt-title")
                    yield Label("Schema isolation via django-tenants — requires PostgreSQL", classes="mt-hint")

        # ── Extras ────────────────────────────────────────────────────
        with Horizontal(classes="extras-hdr"):
            yield Label("Extras to install", classes="extras-hdr-label")
            yield Static(f"0 / {len(SELECTABLE_EXTRAS)} selected", id="extras_counter", classes="extras-counter")

        with ScrollableContainer(classes="extras-scroll"):
            for extra in SELECTABLE_EXTRAS:
                cb_id = f"extra_{extra.replace('-', '_')}"
                with Horizontal(classes="extra-row"):
                    yield Checkbox(extra, value=False, id=cb_id)
                    yield Label(EXTRAS_INFO[extra], classes="extra-desc")
            yield Rule()
            with Horizontal(classes="all-row"):
                yield Checkbox("all  — install everything", value=False, id="extra_all")

        yield Static("", id="error_msg", classes="error-label")

        with Horizontal(classes="button-row"):
            yield Button("← Back", id="btn_back")
            yield Button("Next →", variant="primary", id="btn_next")

        yield Footer()

    def _update_counter(self) -> None:
        count = sum(
            1 for e in SELECTABLE_EXTRAS
            if self.query_one(f"#extra_{e.replace('-', '_')}", Checkbox).value
        )
        self.query_one("#extras_counter", Static).update(f"{count} / {len(SELECTABLE_EXTRAS)} selected")

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if self._syncing:
            return
        self._syncing = True
        try:
            if event.checkbox.id == "extra_all":
                # Propagate to all individual checkboxes
                for extra in SELECTABLE_EXTRAS:
                    self.query_one(f"#extra_{extra.replace('-', '_')}", Checkbox).value = event.value
            else:
                # If all individual are checked, auto-check "all"; otherwise uncheck it
                all_checked = all(
                    self.query_one(f"#extra_{e.replace('-', '_')}", Checkbox).value
                    for e in SELECTABLE_EXTRAS
                )
                self.query_one("#extra_all", Checkbox).value = all_checked
        finally:
            self._syncing = False
        self._update_counter()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back":
            self.app.pop_screen()
            return

        if event.button.id != "btn_next":
            return

        multitenant = self.query_one("#multitenant", Switch).value

        # If "all" is checked submit the bundle alias; otherwise collect individual selections
        if self.query_one("#extra_all", Checkbox).value:
            selected_extras: list[str] = ["all"]
        else:
            selected_extras = [
                e for e in SELECTABLE_EXTRAS
                if self.query_one(f"#extra_{e.replace('-', '_')}", Checkbox).value
            ]

        if not selected_extras:
            self.query_one("#error_msg", Static).update("Select at least one extra.")
            return

        self.query_one("#error_msg", Static).update("")
        self.dismiss({
            "multitenant": multitenant,
            "extras": selected_extras,
        })


class DDDScreen(Screen[dict]):  # type: ignore[type-arg]
    """Step 3 — DDD module name and actor."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    CSS = _COMMON_CSS

    def __init__(self, project_name: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Step 3 of 3 — DDD Structure", classes="wizard-title")

        yield Label("Module name (aggregate root)", classes="section-label")
        yield Input(
            placeholder=self._project_name,
            value=self._project_name,
            id="module_name",
            classes="field-row",
        )

        yield Label("Actor (optional, press Enter to skip)", classes="section-label")
        yield Input(placeholder="", id="actor", classes="field-row")

        yield Static("", id="error_msg", classes="error-label")

        with Horizontal(classes="button-row"):
            yield Button("← Back", id="btn_back")
            yield Button("Next →", variant="primary", id="btn_next")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back":
            self.app.pop_screen()
            return

        if event.button.id != "btn_next":
            return

        module_name = str(self.query_one("#module_name", Input).value).strip()
        if not module_name:
            self.query_one("#error_msg", Static).update("Module name cannot be empty.")
            return

        actor = str(self.query_one("#actor", Input).value).strip()

        self.dismiss({"module_name": module_name, "actor": actor})


class ConfirmationScreen(Screen[bool]):
    """Final confirmation screen — shows a summary before generating."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    CSS = _COMMON_CSS

    def __init__(self, config: ProjectConfig, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._config = config

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Confirmation — Review your project settings", classes="wizard-title")

        c = self._config
        extras_str = ", ".join(c["extras"])
        actor_str = c["actor"] if c["actor"] else "(none)"
        summary = (
            f"  Package manager : {c['package_manager']}\n"
            f"  SERVICE_NAME    : {c['service_name']}\n"
            f"  BASE_PATH       : {c['base_path']}\n"
            f"  Python version  : {c['python_version']}\n"
            f"  Multi-tenant    : {c['multitenant']}\n"
            f"  Extras          : {extras_str}\n"
            f"  Module name     : {c['module_name']}\n"
            f"  Actor           : {actor_str}\n"
        )
        with Vertical(classes="summary-box"):
            yield Static(summary)

        with Horizontal(classes="button-row"):
            yield Button("← Back", id="btn_back")
            yield Button("Cancel", variant="error", id="btn_cancel")
            yield Button("Generate", variant="success", id="btn_generate")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back":
            self.app.pop_screen()
        elif event.button.id == "btn_cancel":
            self.dismiss(False)
        elif event.button.id == "btn_generate":
            self.dismiss(True)


class StartProjectApp(App[None]):
    """Textual wizard app for pyms-django startproject."""

    CSS = _COMMON_CSS
    TITLE = "pyms-django — New Project Wizard"

    def __init__(self, project_name: str, result_holder: list[ProjectConfig | None]) -> None:
        super().__init__()
        self._project_name = project_name
        self._result_holder = result_holder
        self._setup_data: dict[str, object] = {}
        self._features_data: dict[str, object] = {}

    def on_mount(self) -> None:
        self.push_screen(ProjectSetupScreen(self._project_name), self._on_setup_done)

    def _on_setup_done(self, data: dict[str, object] | None) -> None:
        if data is None:
            self.exit()
            return
        self._setup_data = data
        self.push_screen(FeaturesScreen(), self._on_features_done)

    def _on_features_done(self, data: dict[str, object] | None) -> None:
        if data is None:
            self.exit()
            return
        self._features_data = data
        self.push_screen(DDDScreen(self._project_name), self._on_ddd_done)

    def _on_ddd_done(self, data: dict[str, object] | None) -> None:
        if data is None:
            self.exit()
            return

        self._pending_config: ProjectConfig = {
            "package_manager": str(self._setup_data.get("package_manager", "uv")),
            "service_name": str(self._setup_data.get("service_name", "")),
            "base_path": str(self._setup_data.get("base_path", "")),
            "python_version": str(self._setup_data.get("python_version", "3.12")),
            "multitenant": bool(self._features_data.get("multitenant", False)),
            "extras": list(self._features_data.get("extras", [])),  # type: ignore[arg-type]
            "module_name": str(data.get("module_name", "")),
            "actor": str(data.get("actor", "")),
        }
        self.push_screen(ConfirmationScreen(self._pending_config), self._on_confirmed)

    def _on_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self._result_holder[0] = self._pending_config
        self.exit()


def run_tui_wizard(project_name: str) -> ProjectConfig | None:
    """Run the Textual wizard and return the collected config, or None if cancelled.

    Args:
        project_name: The name of the project passed on the CLI.

    Returns:
        A ProjectConfig if the user completed the wizard, None if cancelled.
    """
    result_holder: list[ProjectConfig | None] = [None]
    app = StartProjectApp(project_name, result_holder)
    app.run(inline=True)
    return result_holder[0]
