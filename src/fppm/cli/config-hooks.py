import fppm.cli.utils as FppmUtils
import os
import subprocess

def getPython():
    try:
        output = subprocess.run(["which", "python"], capture_output=True, check=True)
        if output.returncode == 0:
            return output.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        try:
            output = subprocess.run(["which", "python3"], capture_output=True, check=True)
            if output.returncode == 0:
                return output.stdout.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            FppmUtils.print_error(f"[ERR]: Unable to find a Python interpreter. Ensure python or python3 is added to your path.")
            return 1

def pre_hook(script, fillable):
    locPython = getPython()
    
    if locPython == 1:
        return 1
    
    try:
        output = subprocess.run([locPython, script, "-f", fillable], capture_output=True, check=True)
        return output.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        FppmUtils.print_error(f"[ERR]: Error running pre-hook script: {e}")
        return 1
    
def post_hook(script, generated):
    locPython = getPython()
    
    if locPython == 1:
        return 1
    
    try:
        output = subprocess.run([locPython, script, "-g", generated], capture_output=True, check=True)
        return output.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        FppmUtils.print_error(f"[ERR]: Error running post-hook script: {e}")
        return 1
        