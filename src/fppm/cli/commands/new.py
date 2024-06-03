import os
import yaml
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
from pathlib import Path
import sys
import subprocess


# context is usually empty unless unit testing
def create_new_package_yml(args, context):
    # check whether git url provided is valid
    userProvidedGitURL = hasattr(args, "git_url") and args.git_url is not None
    if userProvidedGitURL:
        try:
            validate = subprocess.run(
                ["git", "ls-remote", args.git_url], capture_output=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[ERR]: Invalid git URL provided. Please provide a valid git URL.")
            return 1

    print(f"[INFO]: Creating new package.yml file...")

    # get source of cookiecutter
    try:
        source = os.path.dirname(__file__) + "/../../templates/cookiecutter-package"
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
        print(f"{e}", file=sys.stderr)
        return 1

    print(f"\n")  # just for prettiness

    # check if user wants to initialize this package as a git repo
    skipGitSetup = False

    if bool(context) and context["inputs"] is not None:
        # for testing
        if "git" in context["inputs"]:
            if context["inputs"]["git"] == "n":
                print(f"[INFO]: Skipping git repo initialization...")
                skipGitSetup = True
            elif context["inputs"]["git"] == "y":
                print(f"[INFO]: Initializing package as a git repo...")
                skipGitSetup = False
        else:
            print(f"[INFO]: Skipping git repo initialization...")
            skipGitSetup = True
    else:
        # for user input
        if userProvidedGitURL:
            print(
                f"[INFO]: Git url was passed in. Initializing package as a git repo..."
            )
            skipGitSetup = False
        elif (
            input(
                "[???] Would you like to initialize this package as a git repo? (y/n): "
            )
            == "y"
        ):
            print(f"[INFO]: Initializing package as a git repo...")
            skipGitSetup = False
        else:
            print(f"[INFO]: Skipping git repo initialization...")
            skipGitSetup = True

    if not skipGitSetup:
        # check if package was created inside a git repo
        isInGitRepo = False
        try:
            validate = subprocess.run(
                ["git", "status"], cwd=gen_path, capture_output=True, check=True
            )
            print(f"[INFO]: Detected package created in a git repo.")
            isInGitRepo = True
        except subprocess.CalledProcessError:
            print(f"[INFO]: Detected not in a git repo.")
            isInGitRepo = False

        try:
            print(f"[INFO]: Setting up package as a git repo...")
            gitInit = subprocess.run(
                ["git", "init"], cwd=gen_path, capture_output=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[ERR]: Failed to set up package as a git repo: {e}")
            return 1

        if args.git_url is not None:
            try:
                print(f"[INFO]: Setting up remote origin...")
                addRemoteSource = subprocess.run(
                    ["git", "remote", "add", "origin", args.git_url],
                    cwd=gen_path,
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"[ERR]: Failed to set up remote origin. {e}")
                return 1

    print(
        f"""\n
[DONE]: Generated package.yml file inside {gen_path}

Please remember to fill in the fields indicated in the package.yml 
before publishing.

{f"Your package was also initialized as a git repo." if not skipGitSetup else "The package was not initialized as a git repo. You can do so manually if desired."}

All files related to your package should be kept within the generated folder.

Happy developing!
          """
    )

    return 0
