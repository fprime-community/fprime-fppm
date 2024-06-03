# Route all commands to their respective functions
import fppm.cli.commands.new as cmd_new
import fppm.cli.commands.registries as cmd_registries
import fppm.cli.commands.init as cmd_init
import sys

ROUTER = {
    "new": cmd_new.create_new_package_yml,
    "registries": cmd_registries.registries_entrypoint,
    "init": cmd_init.create_project_yaml_file,
}


def route_commands(command, args: list) -> int:
    try:
        exec = ROUTER[command](args, {})
        if exec:
            sys.exit(1)
        return 0
    except KeyError as e:
        print(f"[ERR]: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERR]: {e}")
        sys.exit(1)
