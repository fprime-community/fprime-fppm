import os
import yaml
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
from pathlib import Path
import sys
import subprocess


def create_new_package_yml(args):
    # check whether git url provided is valid
    try:
        checkIfGitValid = subprocess.Popen(['git', 'ls-remote', args.git_url], stdout=subprocess.PIPE)
        output = checkIfGitValid.stdout.read()
        if not output or b'fatal' in output:
            raise Exception(f"Invalid git URL provided. Please provide a valid git URL.")
    except:
        print(f"[ERR]: Invalid git URL provided. Please provide a valid git URL.")
        sys.exit(1)
    
    print(f"[INFO]: Creating new package.yml file...")
    
    # get source of cookiecutter
    try:
        source = os.path.dirname(__file__) + '/../../templates/cookiecutter-package'
        gen_path = Path(
            cookiecutter(source)
        ).resolve()
    
    except OutputDirExistsException as e:
        print(f"{e}", file=sys.stderr)
        
    # set up package as a git submodule/remote
    try:
        print(f"[INFO]: Setting up package as a git submodule...")
        removeFromIdx = subprocess.Popen(['git', 'rm', '-r', '--cached', '.'], cwd=gen_path)
        initRepo = subprocess.Popen(['git', 'init'], cwd=gen_path)
        addRemoteSource = subprocess.Popen(['git', 'remote', 'add', 'origin', args.git_url], cwd=gen_path)
        firstCommit = subprocess.Popen(['git', 'add', '.', '&&', 'git', 'commit', '-m', '"[fppm] Package init"', '&&', 'git', 'push', '--set-upstream', 'origin', 'main'], cwd=gen_path)
        print(f"[DONE]: Package added as git submodule.")
    except:
        print(f"[ERR]: Failed to set up package as a git submodule. See above for the error.")
        sys.exit(1)

    print(f"""\n
[DONE]: Generated package.yml file inside {gen_path}

Please remember to fill in the fields indicated in the package.yml 
before publishing. Your package is also added as a git submodule to the 
repo you provided.

All files related to your package should be kept within the generated folder.

Happy developing!
          """)