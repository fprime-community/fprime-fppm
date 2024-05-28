import sys
import fppm.cli.setup_cli

def main():
    # run the CLI
    fppm.cli.setup_cli.start_cli_parser(args=sys.argv[1:])

if __name__ == "__main__":
    sys.exit(main())