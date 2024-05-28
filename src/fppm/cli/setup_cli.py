import argparse

# setup the "new" subcommand parser
def setup_new_parser() -> callable:
    new_parser = argparse.ArgumentParser(
        description='Create a new package.yml metadata file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    return new_parser    

# function to setup the complete CLI
def start_cli_parser(args: list):
    # collect all parsers
    parsers = {
        'new': setup_new_parser(),
    }
    
    # parent parser
    parser = argparse.ArgumentParser(
        description='fppm: F Prime Package Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    print(f"parsers: {parsers}")