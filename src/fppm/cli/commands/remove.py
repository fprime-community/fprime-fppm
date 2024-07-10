import fppm.cli.commands.registries as cmd_registries
import glob
import shutil
import os

def remove_package(args, context):
    projectYamlPath = "./project.yaml"
    
    if args.project_yaml_path is not None:
        projectYamlPath = args.project_yaml_path
        
    packageFolder = args.package.replace("/", ".")
    
    print(f"[INFO]: Removing package [{args.package}]...")
    
    try:
        existingPackage = glob.glob(f"_fprime_packages/{packageFolder}*")
    except Exception as e:
        print(f"[ERR]: Error checking for existing package [{args.package}]: {e}")
        return 1
    
    for package in existingPackage:
        try:
            shutil.rmtree(package)
        except Exception as e:
            print(f"[ERR]: Error removing package [{args.package}]: {e}")
            return 1
        
    with open(f"_fprime_packages/CMakeLists.txt", "r") as f:
        lines = f.readlines()
        
    with open(f"_fprime_packages/CMakeLists.txt", "w") as f:
        for line in lines:
            if packageFolder not in line:
                f.write(line)
                
    fillables = glob.glob(f"{packageFolder}.fillables")
    
    if len(fillables) > 0:
        if input(f"[???] Remove the fillables directory for package [{args.package}]: ") == "y":
            try:
                shutil.rmtree(fillables[0])
            except Exception as e:
                print(f"[ERR]: Error removing fillables directory for package [{args.package}]: {e}")
                return 1
            
    print(f"[INFO]: Updating project.yaml file...")
    
    projectYamlPath, projectYamlContent = cmd_registries.open_project_yaml(projectYamlPath)
    
    if projectYamlContent == 1:
        return 1
    
    if projectYamlContent.get("packages") is not None:
        for package in projectYamlContent["packages"]:
            if package["name"] == args.package:
                projectYamlContent["packages"].remove(package)
                break
    else:
        print(f"[ERR]: No packages found in project.yaml file.")
        return 1
        
    write = cmd_registries.write_to_project_yaml(projectYamlPath, projectYamlContent)
                
    print(f"[DONE]: Removed package [{args.package}]")
    
        
    