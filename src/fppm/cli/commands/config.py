import os
import shutil
from pathlib import Path
import yaml
import json
from glob import glob
import fppm.cli.commands.registries as cmd_registries
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
import fppm.cli.utils as FppmUtils
import fppm.cli.config_hooks as ConfigHooks


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
        print(
            f"{FppmUtils.bcolors.FAIL}[ERR]: Config object [{configObject}] is not in the correct format. Please use './' to denote the relative path.{FppmUtils.bcolors.ENDC}"
        )
        return 1

    with open(packagePath + "/" + configObject, "r") as configObjectFile:
        configObjectContent = configObjectFile.read()

    # find all cookiecutter variables
    cookiecutterVariables = []
    configDescription = ""

    if "{{" in configObject and "}}" in configObject:
        variable = configObject.split("{{")[1].split("}}")[0].strip().split(".")[1]
        cookiecutterVariables.append(
            {"context": "FILE NAME", "variable": variable, "line": 0}
        )
        
    metadataVars = {
        'output': None,
        'pre_hook': None,
        'post_hook': None
    }

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
        
        if "@! output = " in line:
            metadataVars['output'] = line.split("@! output = ")[1].strip()
            continue
        
        if "@! pre_hook = " in line:
            metadataVars['pre_hook'] = line.split("@! pre_hook = ")[1].strip()
            if '.py' not in metadataVars['pre_hook']:
                metadataVars['pre_hook'] = None
            continue
        
        if "@! post_hook = " in line:
            metadataVars['post_hook'] = line.split("@! post_hook = ")[1].strip()
            if '.py' not in metadataVars['post_hook']:
                metadataVars['post_hook'] = None
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

            cookiecutterVariables.append(
                {"context": line.strip(), "variable": variable, "line": lineNumber + 1}
            )

            # append other variables in the line
            for var in line.split("{{")[1:]:
                variable = var.split("}}")[0].strip().split(".")[1]
                lineNumber = configObjectContent.split("\n").index(line)

                doNotAdd = False

                for vars in cookiecutterVariables:
                    if vars["variable"] in variable:
                        doNotAdd = True

                if doNotAdd:
                    continue

                cookiecutterVariables.append(
                    {
                        "context": line.strip(),
                        "variable": variable,
                        "line": lineNumber + 1,
                    }
                )

    return (cookiecutterVariables, configDescription, metadataVars)


def create_fillable(variables, description, metavars, configObject, packagePath, fillablesPath):
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
        if metavars['output'] is not None:
            fillableFile.write("\n# === METADATA VARIABLES: Do not edit if you don't know what you're doing! ===\n\n")
            fillableFile.write(f"__output: {metavars['output']}\n")
        if metavars['pre_hook'] is not None:
            fillableFile.write(f"__pre_hook: {metavars['pre_hook']}\n")
        if metavars['post_hook'] is not None:
            fillableFile.write(f"__post_hook: {metavars['post_hook']}\n")
        fillableFile.write("\n# === END METADATA ===\n\n")

        if description != "" and description is not None:
            fillableFile.write("# === BEGIN DESCRIPTION ===\n")
            fillableFile.write(description)
            fillableFile.write("# === END DESCRIPTION ===\n\n")

        if len(variables) == 0:
            fillableFile.write("# No variables configurable in this file.\n")
            return

        for variable in variables:
            fillableFile.write(
                f"# Context: {variable['context']} (line {variable['line']})\n"
            )
            fillableFile.write(f"{variable['variable']}: << FILL IN >>\n\n")

    print(f"{FppmUtils.bcolors.OKGREEN}[DONE]: Created fillable for config object [{configObject}].{FppmUtils.bcolors.ENDC}")


def update_gitignore():
    """
    Update gitignore to not include the fillables directory. Not used in this file.

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
            print(f"{FppmUtils.bcolors.FAIL}[ERR]: Error adding *.fillables to .gitignore file: {e}{FppmUtils.bcolors.ENDC}")
            return 1


def generate_config_fillables(args, context):
    packageFolder = args.generate.replace("/", ".")

    if os.path.exists(f"_fprime_packages/{packageFolder}") == False:
        print(
            f"{FppmUtils.bcolors.FAIL}[ERR]: Package [{args.generate}] not found. Please install the package first.{FppmUtils.bcolors.ENDC}"
        )
        return 1

    # open package yaml
    packageYamlPath = f"_fprime_packages/{packageFolder}/package.yaml"
    packageYamlPath, packageYamlContent = cmd_registries.open_project_yaml(
        packageYamlPath
    )

    if "config_objects" not in packageYamlContent:
        print(f"[INFO]: No config objects found for package [{args.generate}].")
        return 0

    for configObject in packageYamlContent["config_objects"]:
        print(f"[INFO]: Generating config fillable for object [{configObject}]...")
        vars, desc, metavars = pull_cookiecutter_variables(
            configObject, f"_fprime_packages/{packageFolder}"
        )

        if vars == 1:
            return 1

        try:
            os.mkdir(f"{packageFolder}.fillables")
        except FileExistsError:
            pass
        
        if len(vars) == 0 and desc == "" and metavars['output'] is None:
            settings = FppmUtils.openSettingsIni(Path("settings.ini"))
            configDir = str(settings['config_directory'])
            
            if "fprime" in configDir.split("/"):
                print(f"{FppmUtils.bcolors.FAIL}[ERR]: No output directory specified for config object [{configObject}], and F Prime config folder not configured in settings.ini.{FppmUtils.bcolors.ENDC}")
                return 1
            else:
                shutil.copy(
                    f"_fprime_packages/{packageFolder}/{configObject}",
                    f"{configDir}"
                )
                print(f"{FppmUtils.bcolors.OKGREEN}[DONE]: Moved config object [{configObject}] to [{configDir}].{FppmUtils.bcolors.ENDC}")
            
                if ".fpp" in configObject:
                    print(f"{FppmUtils.bcolors.WARNING}[WARN]: Output file {configObject} is an FPP file; remember to add it as a source in CMakeLists.txt.{FppmUtils.bcolors.ENDC}")
                    
                continue

        create_fillable(
            vars,
            desc,
            metavars,
            configObject,
            f"_fprime_packages/{packageFolder}",
            f"{packageFolder}.fillables",
        )

    print(f"{FppmUtils.bcolors.OKGREEN}[DONE]: Generated all fillables at [{packageFolder}.fillables].{FppmUtils.bcolors.ENDC}")
    return 0


def cleanup():
    if os.path.exists("__TMP__"):
        shutil.rmtree("__TMP__", ignore_errors=True)

    fillable_cookiecutters = glob("__fillable_*")

    for fillable_cookiecutter in fillable_cookiecutters:
        shutil.rmtree(fillable_cookiecutter, ignore_errors=True)


def apply_config_fillables(args, context):
    cleanup()
    if os.path.exists("__TMP__"):
        shutil.rmtree("__TMP__", ignore_errors=True)

    packageFolder = args.apply.replace("/", ".")

    if os.path.exists(f"_fprime_packages/{packageFolder}") == False:
        print(
            f"{FppmUtils.bcolors.FAIL}[ERR]: Package [{args.apply}] not found. Please install the package first.{FppmUtils.bcolors.ENDC}"
        )
        return 1

    if os.path.exists(f"{packageFolder}.fillables") == False:
        print(
            f"{FppmUtils.bcolors.FAIL}[ERR]: Fillables for package [{args.apply}] not found. Please generate the fillables first.{FppmUtils.bcolors.ENDC}"
        )
        return 1

    fillables = glob(f"{packageFolder}.fillables/*.fillable.yaml")

    for fillable in fillables:
        print(f"[INFO]: Applying fillable [{fillable}]...")

        with open(fillable, "r") as fillableFile:
            fillableContent = yaml.safe_load(fillableFile)

        if fillableContent == None:
            print(f"{FppmUtils.bcolors.FAIL}[ERR]: Error parsing fillable [{fillable}].{FppmUtils.bcolors.ENDC}")
            return 1

        if fillableContent["__package_path"] != f"_fprime_packages/{packageFolder}":
            print(
                f"{FppmUtils.bcolors.FAIL}[ERR]: Fillable [{fillable}] does not belong to package [{packageFolder}].{FppmUtils.bcolors.ENDC}"
            )
            return 1

        fillableContent["__config_object"] = fillableContent["__config_object"].replace(
            "./", ""
        )

        pathToMainFile = (
            fillableContent["__package_path"] + "/" + fillableContent["__config_object"]
        )

        if (
            "{{" in fillableContent["__config_object"]
            and "}}" in fillableContent["__config_object"]
        ):
            tempName = (
                fillableContent["__config_object"].split("{{")[1].split("}}")[0].strip()
            )
        else:
            tempName = fillableContent["__config_object"].split("/")[-1]

        extraContext = {"temporary___": "__fillable_" + tempName}

        if os.path.exists(tempName):
            shutil.rmtree(tempName, ignore_errors=True)
            
        metaVarContent = {}

        for key in fillableContent.keys():
            if "__" not in key[0:2]:
                extraContext[key] = fillableContent[key]
            else:
                metaVarContent[key] = fillableContent[key]
                
        if "__pre_hook" in metaVarContent.keys():
            totalPath = str(Path(f"_fprime_packages/{packageFolder}/{metaVarContent['__pre_hook']}").absolute())
            
            if os.path.exists(totalPath) == False:
                FppmUtils.print_error(f"[ERR]: Pre-hook script [{metaVarContent['__pre_hook']}] not found.")
            else:
                pre_hook_output = ConfigHooks.pre_hook(totalPath, str(Path(fillable).absolute()))
                
                if pre_hook_output == 1:
                    return 1
                
                FppmUtils.print_warning(f"[INFO]: Pre-hook printed: {pre_hook_output}")
                

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
                pathToMainFile, extra_context=extraContext, no_input=True
            )
        except OutputDirExistsException as e:
            print(f"{FppmUtils.bcolors.FAIL}[ERR]: {e}{FppmUtils.bcolors.ENDC}")
            return 1

        try:
            os.mkdir(f"{packageFolder}.fillables/out")
        except FileExistsError:
            pass

        # move all files in the generated directory to the out directory

        for file in os.listdir(actual_cookiecutter):
            if ".fpp" in file:
                FppmUtils.print_warning(
                    f"[!!!] Output file {file} is an FPP file; remember to add it as a source in CMakeLists.txt."
                )

            with open(f"{actual_cookiecutter}/{file}", "r") as fileContent:
                content = fileContent.read()

            if "@! begin config description" in content:
                # remove the description
                idxStart = content.index("@! begin config description")
                idxEnd = content.index("@! end config description")

                content = (
                    content[:idxStart] + content[idxEnd + 26 :]
                )  # length of "@! end config description"

            if "@! output = " in content:
                # remove the output metadata
                idxStart = content.index("@! output = ")
                idxEnd = content.index("\n", idxStart)

                content = content[:idxStart] + content[idxEnd:]

            if "@! pre_hook = " in content:
                # remove the pre_hook metadata
                idxStart = content.index("@! pre_hook = ")
                idxEnd = content.index("\n", idxStart)

                content = content[:idxStart] + content[idxEnd:]
                    
            if "@! post_hook = " in content:
                # remove the post_hook metadata
                idxStart = content.index("@! post_hook = ")
                idxEnd = content.index("\n", idxStart)

                content = content[:idxStart] + content[idxEnd:]

            with open(f"{actual_cookiecutter}/{file}", "w") as fileContent:
                fileContent.write(content)
                
            if "__post_hook" in metaVarContent.keys():
                totalPath = str(Path(f"_fprime_packages/{packageFolder}/{metaVarContent['__post_hook']}").absolute())
                
                if os.path.exists(totalPath) == False:
                    FppmUtils.print_error(f"[ERR]: Post-hook script [{metaVarContent['__post_hook']}] not found.")
                else:
                    post_hook_output = ConfigHooks.post_hook(totalPath, str(Path(f"{actual_cookiecutter}/{file}").absolute()))
                    
                    if post_hook_output == 1:
                        return 1
                    
                    FppmUtils.print_warning(f"[INFO]: Post-hook printed: {post_hook_output}")
                            
            if "__output" in metaVarContent.keys():
                if os.path.exists(f"{metaVarContent['__output']}/{file}"):
                    prompt = FppmUtils.prompt(
                        f"[INFO]: File [{file}] already exists in the output directory. Overwrite? [y/n]: ", ["y", "n"]
                    )
                    
                    if prompt.lower() == "n":
                        shutil.move(
                            f"{actual_cookiecutter}/{file}", f"{packageFolder}.fillables/out"
                        )
                        continue
                    elif prompt.lower() == "y":
                        os.remove(f"{fillableContent['__output']}/{file}")
                        shutil.move(
                            f"{actual_cookiecutter}/{file}", metaVarContent['__output']
                        )
                else:
                    shutil.move(
                        f"{actual_cookiecutter}/{file}", metaVarContent['__output']
                    )
            else:
                if os.path.exists(f"{packageFolder}.fillables/out/{file}"):
                    prompt = FppmUtils.prompt(
                        f"[INFO]: File [{file}] already exists in the output directory. Overwrite? [y/n]: ", ["y", "n"]
                    )
                    
                    if prompt.lower() == "n":
                        os.remove(f"{actual_cookiecutter}/{file}")
                        continue
                    elif prompt.lower() == "y":
                        os.remove(f"{packageFolder}.fillables/out/{file}")
                        shutil.move(
                            f"{actual_cookiecutter}/{file}", f"{packageFolder}.fillables/out"
                        )

        shutil.rmtree(actual_cookiecutter, ignore_errors=True)
        shutil.rmtree(f"__TMP__", ignore_errors=True)

        print(f"{FppmUtils.bcolors.OKGREEN}[DONE]: Applied fillable [{fillable}].{FppmUtils.bcolors.ENDC}")

    print(
        f"{FppmUtils.bcolors.OKGREEN}[DONE]: Applied all fillables.{FppmUtils.bcolors.ENDC}"
    )
    cleanup()
    return 0


def config_entry(args, context):
    if args.generate is not None:
        print(f"[INFO]: Generating config fillables...")
        return generate_config_fillables(args, context)
    elif args.apply is not None:
        print(f"[INFO]: Applying config fillables...")
        return apply_config_fillables(args, context)
