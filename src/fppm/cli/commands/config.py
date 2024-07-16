import os
import shutil
from pathlib import Path
import json
from glob import glob
import fppm.cli.commands.registries as cmd_registries
import fprime.fbuild.settings as Settings

def openSettingsIni():
    settings_file = Path("settings.ini")
    
    try:
        with open(settings_file, 'r') as file:
            settings = file.read()
    except FileNotFoundError:
        print(f'[ERR]: {settings_file} not found. Make sure you are in the root of your project.')
        return None
    
    settings = Settings.IniSettings.load(settings_file)
    return settings

def generate_config_fillables(args, context):
    packageFolder = args.generate.replace("/", ".")

    if os.path.exists(f"_fprime_packages/{packageFolder}") == False:
        print(
            f"[ERR]: Package [{args.generate}] not found. Please install the package first."
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
        if ".fpp" not in configObject:
            print(
                f"[ERR]: Config object [{configObject}] is not an FPP file. Skipping..."
            )
            continue
        
        print(f"[INFO]: Generating config file for object [{configObject}]...")
        
        settings = openSettingsIni()
        
        if settings is None:
            return 1
        
        configPath = str(settings['config_directory'])
                
        if configPath.split("/")[-2] == "fprime":
            print(f"[ERR]: Config directory is not set to a custom one. Please set the config directory in settings.ini.")
            return 1
        else:
            shutil.copy(configObject, configPath)
            print(f"[!!, DONE]: Copied config object [{configObject}] to [{configPath}]. Remember to add it to the source list in {str(settings['config_file'])}/CMakeLists.txt.")
        
    print(f"[DONE]: Generated all fillables at [{packageFolder}.fillables].")
    return 0


def config_entry(args, context):
    if args.generate is not None:
        print(f"[INFO]: Generating config fillables...")
        return generate_config_fillables(args, context)
