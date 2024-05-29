import os
import yaml
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
from pathlib import Path
import sys


def create_new_package_yml(args: list):
    print(f"[INFO]: Creating new package.yml file...")
    
    # get source of cookiecutter
    try:
        source = os.path.dirname(__file__) + '/../../templates/cookiecutter-package'
        gen_path = Path(
            cookiecutter(source)
        ).resolve()
    
    except OutputDirExistsException as e:
        print(f"{e}", file=sys.stderr)

    print(f"""\n
[DONE]: Generated package.yml file inside {gen_path}

Please remember to fill in the fields indicated in the package.yml 
before publishing.

All files related to your package should be kept within the generated folder.

Happy developing!
          """)