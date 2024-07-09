import validators
import os
import fppm.cli.commands.registries as cmd_registries
import glob
import subprocess
from argparse import Namespace

def setup_ephemeral():
    existsAlready = os.path.exists("_fprime_packages")
    
    try:
        os.mkdir("_fprime_packages")
    except FileExistsError:
        pass
    
    if existsAlready == False:
        if input("[???]: Would you like to add the _fprime_packages directory to your .gitignore file? (y/n): ") == "y":
            # look for a .gitignore file
            if os.path.exists(".gitignore"):
                try:
                    gitignoreIsUpdated = False
                    with open(".gitignore", "r") as gitignore:
                        if "_fprime_packages" in gitignore.read():
                            gitignoreIsUpdated = True
                    
                    if gitignoreIsUpdated == False:
                        with open(".gitignore", "a") as gitignore:
                            gitignore.write("\n# F' packages")
                            gitignore.write("\n/_fprime_packages/")
                except Exception as e:
                    print(f"[ERR]: Error adding _fprime_packages to .gitignore file: {e}")
                    return 1  
                
def add_package_to_cmake(folderName):
    if os.path.exists("_fprime_packages"):
        pass
    else:
        setup_ephemeral()
        
    lineToAdd = 'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}'
    lineToAdd += f'/{folderName}")\n'
    
    if os.path.exists("_fprime_packages/CMakeLists.txt"):
        
        if lineToAdd in open("_fprime_packages/CMakeLists.txt").read():
            pass
        else:
            with open("_fprime_packages/CMakeLists.txt", "a") as cmake:
                cmake.write(lineToAdd)
            
    else:
        with open("_fprime_packages/CMakeLists.txt", "w") as cmake:
            cmake.write(lineToAdd)
            
    cmakeFiles = glob.glob("*.cmake")[0]
    cmakeLineToAdd = 'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/_fprime_packages")\n'
    
    if cmakeLineToAdd in open(cmakeFiles).read():
        return 0

    if input(f"[???]: Would you like to include the _fprime_packages CMakeLists.txt file to {cmakeFiles}? (y/n): ") == "y":
        with open(cmakeFiles, "a") as cmake:
            cmake.write(cmakeLineToAdd)
            
    print(f"[DONE]: Added _fprime_packages to {cmakeFiles}")
    return 0

def install_project_yaml(args, context):
    projectYamlPath = "./project.yaml"
    
    if args.project_yaml_path is not None:
        projectYamlPath = args.project_yaml_path
        
    print(f"[INFO]: Finding packages in project.yaml file at {projectYamlPath}...")
        
    path, content = cmd_registries.open_project_yaml(projectYamlPath)
    
    if content['packages'] is None:
        print(f"[ERR]: No packages found in project.yaml file.")
        return 1
    
    for package in content['packages']:
        print(f"[INFO]: Installing package [{package['name']}]...")
        install_package(Namespace(package=package['name'], version=package['version'], project_yaml_path=projectYamlPath), {})

def install_package(args, context):
    if args.package is None and args.version is None:
        return install_project_yaml(args, context)
    
    package = None
    if validators.url(args.package) != True:
        # check the registries
        print(f"[INFO]: Checking registries for package [{args.package}]...")
        
        if args.project_yaml_path is not None or args.project_yaml_path != "":
            projectYamlPath = args.project_yaml_path
        else:
            projectYamlPath = "./project.yaml"
            
        
        package = cmd_registries.shortname_to_git(projectYamlPath, args.package)
        if package == 1:
            return 1
                
        print(f"[INFO]: Located package in {package['registry']} (published by: {package['publisher']})")
        setup_ephemeral()
    
        packageFolderName = args.package.replace("/", ".")
        existingPackage = None
        try:
            existingPackage = glob.glob(f"_fprime_packages/{packageFolderName}*")
        except Exception as e:
            print(f"[ERR]: Error checking for existing package: {e}")
            return 1
            
        packageVersion = None
        if args.version is not None:
            packageVersion = args.version
        else:
            if package['info']['stable'] is not None:
                packageVersion = package['info']['stable']
            else:
                print(f"[ERR]: No stable version found for package [{args.package}]. Please provide a package version to install.")
                return 1
                        
        if existingPackage is not None and len(existingPackage) > 0:
            print(f"[INFO]: Package [{args.package}] already exists in _fprime_packages. Changing version...")
            try:
                os.chdir(existingPackage[0])
                subprocess.check_call(["git", "fetch"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if "v" == packageVersion[0]:
                    subprocess.check_call(["git", "checkout", f"tags/{packageVersion}", "--branch", package['info']['branch']], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                else:
                    subprocess.check_call(["git", "checkout", f"{packageVersion}"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                
                os.chdir("../../")
                versionTextTernary = "version" if "v" == packageVersion[0] else "commit hash"
                print(f"[DONE]: Changed installed package [{args.package}] to {versionTextTernary} {packageVersion}")
            except Exception as e:
                print(f"[ERR]: Error changing package version: {e}")
                return 1
        else:
            # clone the package
            print(f"[INFO]: Cloning package [{args.package}]...")
            
            try:    
                subprocess.check_call(["git", "clone", package['info']['git'], f"_fprime_packages/{packageFolderName}"],stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                os.chdir(f"_fprime_packages/{packageFolderName}")
                
                if "v" == packageVersion[0]:
                    subprocess.check_call(["git", "checkout", f"tags/{packageVersion}", "--branch", package['info']['branch']], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                else:
                    subprocess.check_call(["git", "checkout", f"{packageVersion}"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                    
                os.chdir("../../")
                versionTextTernary = "version" if "v" == packageVersion[0] else "commit hash"
                
                print(f"[DONE]: Installed package [{args.package}] at {versionTextTernary} {packageVersion}")
            except Exception as e:
                print(f"[ERR]: Error cloning package: {e}")
                return 1
            
        # add version to end of package folder
        packagePath = f"_fprime_packages/{packageFolderName}" if existingPackage is None or len(existingPackage) == 0 else existingPackage[0]
        
        try:
            os.rename(packagePath, f"_fprime_packages/{packageFolderName}")
        except Exception as e:
            print(f"[ERR]: Error renaming package folder: {e}")
            return 1
        
        # add package to project.yaml
        try:
            projectYamlPath, projectYamlContent = cmd_registries.open_project_yaml(projectYamlPath)
            if projectYamlContent == 1:
                return 1
            
            if projectYamlContent.get("packages") is None:
                projectYamlContent["packages"] = []
                
            alreadyExists = False
            for package in projectYamlContent["packages"]:
                if package["name"] == args.package:
                    package["version"] = packageVersion
                    alreadyExists = True
            
            if alreadyExists == False:
                projectYamlContent["packages"].append({"name": args.package, "version": packageVersion})
                print(f"[DONE]: Added package [{args.package}] to project.yaml file.")
            else:
                print(f"[DONE]: Updated package [{args.package}] to version {packageVersion} in project.yaml file.")
            
            write = cmd_registries.write_to_project_yaml(projectYamlPath, projectYamlContent)
            if write == 1:
                return 1
            
            addToCmake = add_package_to_cmake(packageFolderName)
                
            if addToCmake == 1:
                    return 1
            
        except Exception as e:
            print(f"[ERR]: Error adding package to project.yaml: {e}")
            return 1
    else:
        pass    