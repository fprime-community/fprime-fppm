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
    if hasattr(args, 'git_url') and args.git_url is not None:
        try:
            validate = subprocess.run(['git', 'ls-remote', args.git_url], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERR]: Invalid git URL provided. Please provide a valid git URL.")
            return 1
    
    print(f"[INFO]: Creating new package.yml file...")
    
    # get source of cookiecutter
    try:
        source = os.path.dirname(__file__) + '/../../templates/cookiecutter-package'
        actual_cookiecutter = None
        
        # for unit testing
        if bool(context):
            if context['extra_context'] is not None:
                actual_cookiecutter = cookiecutter(source, extra_context=context['extra_context'], no_input=True)
        else:
            actual_cookiecutter = cookiecutter(source)
        
        gen_path = Path(
            actual_cookiecutter
        ).resolve()
    except OutputDirExistsException as e:
        print(f"{e}", file=sys.stderr)
        return 1
        
    print(f"\n") # just for prettiness
        
    # check if package was created inside a git repo
    isInGitRepo = False
    try:
        validate = subprocess.run(['git', 'status'], cwd=gen_path, capture_output=True, check=True)
        print(f"[INFO]: Detected package created in a git repo.")
        isInGitRepo = True
    except subprocess.CalledProcessError:
        print(f"[INFO]: Detected not in a git repo.")
        isInGitRepo = False
        
    try:
        print(f"[INFO]: Setting up package as a git repo...")
        gitInit = subprocess.run(['git', 'init'], cwd=gen_path, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERR]: Failed to set up package as a git repo: {e}")
        return 1
            
    if args.git_url is not None:
        try:
            print(f"[INFO]: Setting up remote origin...")
            addRemoteSource = subprocess.run(['git', 'remote', 'add', 'origin', args.git_url], cwd=gen_path, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERR]: Failed to set up remote origin. {e}")
            return 1


    print(f"""\n
[DONE]: Generated package.yml file inside {gen_path}

Please remember to fill in the fields indicated in the package.yml 
before publishing. {"Your package was also added as a git submodule." if isInGitRepo else "Your package was also inited as a git repo."}

{f"Your package was also added as a git remote with the URL {args.git_url}" if args.git_url is not None else "Please remember to add a remote source to your package."}

All files related to your package should be kept within the generated folder.

Happy developing!
          """)
    
    return 0