import argparse
import sys
import fppm.cli.router as CMD_ROUTER


# setup the "registries" subcommand parser
def setup_registries_parser(subparsers) -> callable:
    registries_parser = subparsers.add_parser(
        "registries",
        description="Control and validate the package registries in the project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Control and validate the package registries in the project",
        add_help=False,
    )

    registries_parser.add_argument(
        "--validate", "--v", type=bool, help="Validate the package registries", required=False,
    )

    registries_parser.add_argument(
        "--add",
        "--a",
        type=str,
        help="Add a new package registry. Must be a direct URL to the registry.yaml file",
        required=False,
    )

    registries_parser.add_argument(
        "--project-yaml-path",
        type=str,
        help="The relative path to the project.yaml file",
        required=False,
    )

    return registries_parser


def setup_init_parser(subparsers) -> callable:
    init_parser = subparsers.add_parser(
        "init",
        description="Initialize a project.yaml file for an F Prime project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Initialize a project.yaml file for an F Prime project.",
        add_help=False,
    )

    return init_parser


# setup the "new" subcommand parser
def setup_new_parser(subparsers) -> callable:
    new_parser = subparsers.add_parser(
        "new",
        description="Create a new package.yaml metadata file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Create a new package.yaml metadata file.",
        add_help=False,
    )

    new_parser.add_argument(
        "--git-url",
        type=str,
        help="The git URL that your package will be version controlled with",
        required=False,
    )

    return new_parser


# function to setup the complete CLI
def start_cli_parser(args: list):
    # parent parser
    parser = argparse.ArgumentParser(
        description="fppm: F Prime Package Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    # setup all subparsers
    setup_init_parser(subparsers)
    setup_new_parser(subparsers)
    setup_registries_parser(subparsers)

    parsed, unknown = parser.parse_known_args(args)

    if len(unknown) > 0:
        print(f"[ERR] Unknown arguments: {unknown}")
        sys.exit(1)

    if parsed.command is None:
        print(f"[ERR] No command provided")
        sys.exit(1)

    # route the command
    return CMD_ROUTER.route_commands(parsed.command, parsed)
