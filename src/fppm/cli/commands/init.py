import os
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
from pathlib import Path
import sys
import subprocess
import fppm.cli.utils as FppmUtils


def create_project_yaml_file(args, context) -> int:
    # check whether fprime project
    try:
        os.path.exists("./fprime")
    except FileNotFoundError as e:
        FppmUtils.print_error(
            f"[ERR]: This command needs to be ran in the F Prime project root directory."
        )
        return 1

    gen_path = None
    try:
        source = (
            os.path.dirname(__file__) + "/../../templates/cookiecutter-project-yaml"
        )
        actual_cookiecutter = None

        # for unit testing
        if bool(context):
            if context["extra_context"] is not None:
                actual_cookiecutter = cookiecutter(
                    source, extra_context=context["extra_context"], no_input=True
                )
        else:
            actual_cookiecutter = cookiecutter(source)

        gen_path = Path(actual_cookiecutter).resolve()
    except OutputDirExistsException as e:
        FppmUtils.print_error(f"{e}")
        return 1
    except Exception as e:
        FppmUtils.print_error(f"[ERR]: {e}")
        return 1

    # move project.yaml out of the generated directory
    try:
        os.rename(
            f"{gen_path}/project.yaml",
            "./project.yaml",
        )
        os.rmdir(gen_path)
    except FileNotFoundError as e:
        FppmUtils.print_error(f"[ERR]: {e}")
        return 1
    except Exception as e:
        FppmUtils.print_error(f"[ERR]: {e}")
        return 1

    # get keys of context
    keys = context.keys()

    if "sac" not in keys:
        askIf = FppmUtils.prompt("[???]: Do you have the subtopology autocoder installed? (y/n): ", ["y", "n"])
        if askIf.lower() == "n":
            print(f"[INFO]: Installing subtopology autocoder...")
            try:
                subprocess.check_call(
                    [
                        "git",
                        "submodule",
                        "add",
                        "https://github.com/mosa11aei/fprime-subtopology-tool",
                    ]
                )
            except Exception as e:
                FppmUtils.print_error(f"[ERR]: Error installing subtopology autocoder: {e}")
                return 1

            print(
                f"[INFO]: Subtopology autocoder installed. Please follow the instructions in the tool's docs/README.md file to add the tool to your CMake process."
            )

    FppmUtils.print_success(
        f"[DONE]: Created project.yaml file in the current directory. You are ready to use F Prime packages."
    )
    return 0
