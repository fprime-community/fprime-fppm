import os
import shutil
from pathlib import Path
import yaml
import json
from glob import glob
import fppm.cli.commands.registries as cmd_registries
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

def pull_cookiecutter_variables(configObject, packagePath):
    """
    Extracts cookiecutter variables from config object files
    
    Args:
        configObject (str): Path to the config object file
        packagePath (str): Path to the package folder
        
    Returns:
        list: List of cookiecutter variables
    """
    
    if "./" in configObject:
        configObject = configObject.replace("./", "")
    elif "/" in configObject[0]:
        print(f"[ERR]: Config object [{configObject}] is not in the correct format. Please use './' to denote the relative path.")
        return 1
        
    with open(packagePath + "/" + configObject, "r") as configObjectFile:
        configObjectContent = configObjectFile.read()
        
    # find all cookiecutter variables
    cookiecutterVariables = []
    configDescription = ""
    
    if "{{" in configObject and "}}" in configObject:
        variable = configObject.split("{{")[1].split("}}")[0].strip().split(".")[1]
        cookiecutterVariables.append({
            "context": "FILE NAME",
            "variable": variable,
            "line": 0
        })
    
    configDesc = False
    for line in configObjectContent.split("\n"):
        if "@! begin config description" in line:
            configDesc = True
            continue
        
        if "@! end config description" in line:
            configDesc = False
            continue
            
        if configDesc:
            configDescription += "# " + line.strip() + "\n"
            continue
        
        if "{{" in line and "}}" in line:
            # append the variable name
            variable = line.split("{{")[1].split("}}")[0].strip().split(".")[1]
            lineNumber = configObjectContent.split("\n").index(line)
            
            doNotAdd = False
            
            for vars in cookiecutterVariables:
                if vars["variable"] in variable:
                    doNotAdd = True
            
            if doNotAdd:
                continue
            
            cookiecutterVariables.append({
                "context": line.strip(),
                "variable": variable,
                "line": lineNumber + 1
            })
            
            # append other variables in the line
            for var in line.split("{{")[1:]:
                variable = var.split("}}")[0].strip().split(".")[1]
                lineNumber = configObjectContent.split("\n").index(line)
                
                doNotAdd = False
                
                for vars in cookiecutterVariables:
                    print(vars["variable"], variable)
                    if vars["variable"] in variable:
                        doNotAdd = True
                    
                if doNotAdd:
                    continue
                
                cookiecutterVariables.append({
                    "context": line.strip(),
                    "variable": variable,
                    "line": lineNumber + 1
                })
            
    return (cookiecutterVariables, configDescription)

def create_fillable(variables, description, configObject, packagePath, fillablesPath):
    """
    Creates a fillable object file for a config object
    
    Args:
        variables (list): List of cookiecutter variables
        configObject (str): Path to the config object file
        packagePath (str): Path to the package folder
        fillablesPath (str): Path to the fillables
        
    Returns:
        None
    """
    
    fillableName = configObject.split("/")[-1]
    fillableName += ".fillable.yaml"
    
    with open(fillablesPath + "/" + fillableName, "w") as fillableFile:
        fillableFile.write("# === START METADATA: DO NOT EDIT ===\n\n")
        fillableFile.write(f"__package_path: {packagePath}\n")
        fillableFile.write(f"__config_object: {configObject}\n")
        fillableFile.write("\n# === END METADATA ===\n\n")
        
        if description != "" and description is not None:
            fillableFile.write("# === BEGIN DESCRIPTION ===\n")
            fillableFile.write(description)
            fillableFile.write("# === END DESCRIPTION ===\n\n")
        
        for variable in variables:
            fillableFile.write(f"# Context: {variable['context']} (line {variable['line']})\n")
            fillableFile.write(f"{variable['variable']}: << FILL IN >>\n\n")
            
    print(f"[DONE]: Created fillable for config object [{configObject}].")
    
def update_gitignore():
    """
    Update gitignore to not include the fillables directory
    
    Args:
        None
        
    Returns:
        None
    """
    
    if os.path.exists(".gitignore"):
        try:
            gitignoreIsUpdated = False
            with open(".gitignore", "r") as gitignore:
                if "*.fillables" in gitignore.read():
                    gitignoreIsUpdated = True
            
            if gitignoreIsUpdated == False:
                with open(".gitignore", "a") as gitignore:
                    gitignore.write("\n# F' package fillables")
                    gitignore.write("\n/*.fillables/")
        except Exception as e:
            print(f"[ERR]: Error adding *.fillables to .gitignore file: {e}")
            return 1     
    
def generate_config_fillables(args, context):
    packageFolder = args.generate.replace("/", ".")
    update_gitignore()
    
    if os.path.exists(f"_fprime_packages/{packageFolder}") == False:
        print(f"[ERR]: Package [{args.generate}] not found. Please install the package first.")
        return 1
    
    # open package yaml
    packageYamlPath = f"_fprime_packages/{packageFolder}/package.yaml"
    packageYamlPath, packageYamlContent = cmd_registries.open_project_yaml(packageYamlPath)
    
    if 'config_objects' not in packageYamlContent:
        print(f"[INFO]: No config objects found for package [{args.generate}].")
        return 0
    
    for configObject in packageYamlContent['config_objects']:
        print(f"[INFO]: Generating config fillable for object [{configObject}]...")
        vars, desc = pull_cookiecutter_variables(configObject, f"_fprime_packages/{packageFolder}")
        
        if vars == 1:
            return 1
        
        try:
            os.mkdir(f"{packageFolder}.fillables")
        except FileExistsError:
            pass
        
        create_fillable(vars, desc, configObject, f"_fprime_packages/{packageFolder}", f"{packageFolder}.fillables")
        
    print(f"[DONE]: Generated all fillables at [{packageFolder}.fillables].")
    return 0

def cleanup():
    if os.path.exists("__TMP__"):
        shutil.rmtree("__TMP__", ignore_errors=True)
        
    fillable_cookiecutters = glob("__fillable_*")
    
    for fillable_cookiecutter in fillable_cookiecutters:
        shutil.rmtree(fillable_cookiecutter, ignore_errors=True)

def apply_config_fillables(args, context):
    if os.path.exists("__TMP__"):
        shutil.rmtree("__TMP__", ignore_errors=True)
        
    packageFolder = args.apply.replace("/", ".")
    
    if os.path.exists(f"_fprime_packages/{packageFolder}") == False:
        print(f"[ERR]: Package [{args.apply}] not found. Please install the package first.")
        return 1
    
    if os.path.exists(f"{packageFolder}.fillables") == False:
        print(f"[ERR]: Fillables for package [{args.apply}] not found. Please generate the fillables first.")
        return 1
    
    fillables = glob(f"{packageFolder}.fillables/*.fillable.yaml")
    
    for fillable in fillables:
        print(f"[INFO]: Applying fillable [{fillable}]...")
        
        with open(fillable, "r") as fillableFile:
            fillableContent = yaml.safe_load(fillableFile)
            
        if fillableContent == None:
            print(f"[ERR]: Error parsing fillable [{fillable}].")
            return 1
        
        if fillableContent['__package_path'] != f"_fprime_packages/{packageFolder}":
            print(f"[ERR]: Fillable [{fillable}] does not belong to package [{packageFolder}].")
            return 1
        
        fillableContent['__config_object'] = fillableContent['__config_object'].replace("./", "")
        
        pathToMainFile = fillableContent['__package_path'] + "/" + fillableContent['__config_object']
        
        if "{{" in fillableContent['__config_object'] and "}}" in fillableContent['__config_object']:
            tempName = fillableContent['__config_object'].split("{{")[1].split("}}")[0].strip()
        else:
            tempName = fillableContent['__config_object'].split("/")[-1]
        
        extraContext = {
            "temporary___": "__fillable_" + tempName
        }
        
        if os.path.exists(tempName):
            shutil.rmtree(tempName, ignore_errors=True)
        
        for key in fillableContent.keys():
            if "__" not in key[0:2]:
                extraContext[key] = fillableContent[key]
                
        cookiecutter_name = "{{ cookiecutter.temporary___ }}"
                
        try:
            os.mkdir("__TMP__")
        except FileExistsError:
            pass
        
        try:
            os.mkdir(f"__TMP__/{cookiecutter_name}")
        except FileExistsError:
            pass
        
        shutil.copy(pathToMainFile, f"__TMP__/{cookiecutter_name}")
        
        with open(f"__TMP__/cookiecutter.json", "w") as cookiecutterFile:
            json.dump(extraContext, cookiecutterFile)
            
        # get absolute path of the file
        pathToMainFile = str(Path(f"__TMP__"))
        pathToMainFile = os.getcwd() + "/" + pathToMainFile
        
        try:
            actual_cookiecutter = cookiecutter(
                pathToMainFile,
                extra_context=extraContext,
                no_input=True
            )
        except OutputDirExistsException as e:
            print(f"[ERR]: {e}")
            return 1
        
        try:
            os.mkdir(f"{packageFolder}.fillables/out")
        except FileExistsError:
            pass
                    
        # move all files in the generated directory to the out directory
        
        for file in os.listdir(actual_cookiecutter):
            if ".fpp" in file:
                print(f"\n[!!!] Output file {file} is an FPP file; remember to add it as a source in CMakeLists.txt. \n")
                
            with open(f"{actual_cookiecutter}/{file}", "r") as fileContent:
                content = fileContent.read()
                
            if "@! begin config description" in content:
                # remove the description
                idxStart = content.index("@! begin config description")
                idxEnd = content.index("@! end config description")
                
                content = content[:idxStart] + content[idxEnd+26:] # length of "@! end config description"
                
                with open(f"{actual_cookiecutter}/{file}", "w") as fileContent:
                    fileContent.write(content)
                
            shutil.move(f"{actual_cookiecutter}/{file}", f"{packageFolder}.fillables/out")
            
        shutil.rmtree(actual_cookiecutter, ignore_errors=True)
        shutil.rmtree(f"__TMP__", ignore_errors=True)
            
        print(f"[DONE]: Applied fillable [{fillable}].")
        
    print(f"[DONE]: Applied all fillables. Find the generated files in the [{packageFolder}.fillables/out] directory.")
    cleanup()
    return 0
        
def config_entry(args, context):
    if args.generate is not None:
        print(f"[INFO]: Generating config fillables...")
        return generate_config_fillables(args, context)
    elif args.apply is not None:
        print(f"[INFO]: Applying config fillables...")
        return apply_config_fillables(args, context)
    