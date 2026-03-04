"""CLI package for pyms-django-chassis."""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    """Main entry point for the pyms-django CLI."""
    parser = argparse.ArgumentParser(
        prog="pyms-django",
        description="PyMS Django Chassis CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: startproject  # noqa: ERA001
    sp = subparsers.add_parser("startproject", help="Generate a Django microservice skeleton")
    sp.add_argument("project_name", help="Name of the project")

    # Subcommand: folderddd  # noqa: ERA001
    fd = subparsers.add_parser("folderddd", help="Generate DDD folder structure")
    fd.add_argument("module", help="Name of the module (aggregate root)")
    fd.add_argument("--actor", help="Name of the actor (optional)")

    args = parser.parse_args()
    if args.command == "startproject":
        from .startproject import run_startproject
        run_startproject(args.project_name)
    elif args.command == "folderddd":
        from pyms_django.base.management.commands.folderddd import run_folderddd
        run_folderddd(args.module, args.actor)
    else:
        parser.print_help()
        sys.exit(1)
