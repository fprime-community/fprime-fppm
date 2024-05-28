# Route all commands to their respective functions
import fppm.cli.commands.new as cmd_new
import sys

ROUTER = {
    'new': cmd_new.create_new_package_yml
}

def route_commands(command, args: list) -> int:
    try:
        return ROUTER[command](args)
    except KeyError:
        print(f"[ERR]: Unknown command '{command}'")
        sys.exit(1)
    except Exception as e:
        print(f"[ERR]: {e}")
        sys.exit(1)