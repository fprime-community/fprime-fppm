from fprime.fbuild.settings import IniSettings

def is_valid_name(word: str):
    invalid_characters = [
        "#",
        "%",
        "&",
        "{",
        "}",
        "/",
        "\\",
        "<",
        ">",
        "*",
        "?",
        " ",
        "$",
        "!",
        "'",
        '"',
        ":",
        "@",
        "+",
        "`",
        "|",
        "=",
    ]
    for char in invalid_characters:
        if isinstance(word, str) and char in word:
            return char
        if not isinstance(word, str):
            raise ValueError("Incorrect usage of is_valid_name")
    return "valid"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def prompt(msg, options):
    response = input(bcolors.BOLD + msg + bcolors.ENDC)
    
    if response in options:
        return response
    else:
        print(f"{bcolors.FAIL}Invalid option {response}, try again.{bcolors.ENDC}")
        return prompt(msg, options)

def openSettingsIni(path):
    try:
        with open(path, "r") as file:
            file.close()
    except FileNotFoundError:
        print(f"{bcolors.FAIL}The file {path} does not exist.{bcolors.ENDC}")
        return None
    
    settings = IniSettings()
    return settings.load(path)

def print_success(msg):
    print(f"{bcolors.OKGREEN}{msg}{bcolors.ENDC}")
    
def print_warning(msg):
    print(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")
    
def print_error(msg):
    print(f"{bcolors.FAIL}{msg}{bcolors.ENDC}")