import validators
import os
import fppm.cli.commands.registries as cmd_registries
import glob
import subprocess

def setup_ephemeral():
    try:
        os.mkdir(".fprime.packages")
    except FileExistsError:
        pass
    
    # look for a .gitignore file
    if os.path.exists(".gitignore"):
        try:
            gitignoreIsUpdated = False
            with open(".gitignore", "r") as gitignore:
                if ".fprime.packages" in gitignore.read():
                    gitignoreIsUpdated = True
            
            if gitignoreIsUpdated == False:
                with open(".gitignore", "a") as gitignore:
                    gitignore.write("\n# F' packages")
                    gitignore.write("\n/.fprime.packages/")
        except Exception as e:
            print(f"[ERR]: Error adding .fprime.packages to .gitignore file: {e}")
            return 1  

def install_package(args, context):
    package = None
    if validators.url(args.package) != True:
        # check the registries
        print(f"[INFO]: Checking registries for package [{args.package}]...")
        
        package = cmd_registries.shortname_to_git("./project.yaml", args.package)
        if package == 1:
            return 1
                
        print(f"[INFO]: Located package in {package['registry']} (published by: {package['publisher']})")
        setup_ephemeral()
    
        packageFolderName = args.package.replace("/", ".")
        existingPackage = None
        try:
            existingPackage = glob.glob(f".fprime.packages/{packageFolderName}*")
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
            print(f"[INFO]: Package [{args.package}] already exists in .fprime.packages. Changing version...")
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
                subprocess.check_call(["git", "clone", package['info']['git'], f".fprime.packages/{packageFolderName}"],stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                os.chdir(f".fprime.packages/{packageFolderName}")
                
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
        packagePath = f".fprime.packages/{packageFolderName}" if existingPackage is None or len(existingPackage) == 0 else existingPackage[0]
        
        try:
            os.rename(packagePath, f".fprime.packages/{packageFolderName}@{packageVersion}")
        except Exception as e:
            print(f"[ERR]: Error renaming package folder: {e}")
            return 1
        
        # add package to project.yaml
        try:
            projectYamlPath, projectYamlContent = cmd_registries.open_project_yaml("./project.yaml")
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
        except Exception as e:
            print(f"[ERR]: Error adding package to project.yaml: {e}")
            return 1
    else:
        pass    