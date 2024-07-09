import validators
import requests
import yaml
import os

def shortname_to_git(project_yaml_path, shortname: str):
    # shortnames must be in the format "namespace/package"
    if "/" not in shortname:
        print(f"[ERR]: Invalid shortname [{shortname}]: must be in the format 'namespace/package'.")
        return 1
    
    pathToPackage = shortname.split("/")
    
    projectYamlPath, projectYamlContent = open_project_yaml(project_yaml_path)
    if projectYamlContent == 1:
        return 1
    
    allLocatedPackages = []
    
    for registry in projectYamlContent.get("registries"):
        yamlContent = get_registry(registry)
        if yamlContent == 1:
            return 1
        
        for namespace in yamlContent.get("namespaces"):
            if pathToPackage[0] in namespace.keys():
                for packages in namespace.get(pathToPackage[0]):
                    if pathToPackage[1] in packages.keys():
                        allLocatedPackages.append({
                            "registry": registry,
                            "publisher": yamlContent.get("publisher"),
                            "info": packages.get(pathToPackage[1])
                        })
                    else:
                        pass
            else:
                pass
            
    if len(allLocatedPackages) == 0:
        print(f"[ERR]: No packages found with shortname [{shortname}] in any registry.")
        return 1
            
        
    if len(allLocatedPackages) > 1:
        print(f"[INFO]: Multiple packages found with shortname [{shortname}]. Please specify which one you want.")
        for i in range(len(allLocatedPackages)):
            print(f"[{i+1}]: {allLocatedPackages[i].get('registry')} (published by: {allLocatedPackages[i].get('publisher')}")
        
        try:
            userChoice = int(input("[???] Please choose a package: "))
            if userChoice < 1 or userChoice > len(allLocatedPackages):
                print(f"[ERR]: Invalid choice.")
                return 1
            else:
                return allLocatedPackages[userChoice-1]
        except ValueError:
            print(f"[ERR]: Invalid choice.")
            return 1
    else:
        return allLocatedPackages[0]
    
def get_registry(registry_url):
    isRemoteYaml = False
    if registry_url is not None:
        # localhost bypass: it should still fail if invalid later on
        if validators.url(registry_url) or "localhost" in registry_url: 
            if registry_url.endswith(".yaml"):  # https://stackoverflow.com/a/21059164
                isRemoteYaml = True
            else:
                print(f"[ERR]: Invalid URL [{registry_url}]: link must end in .yaml")
                return 1
        else:
            # may be a relative path
            if os.path.exists(registry_url):
                isRemoteYaml = False
            else:
                print(
                    f"[ERR]: Invalid URL [{registry_url}]: link (local) does not exist or URL is malformed."
                )
                return 1
    else:
        print(f"[ERR]: No URL provided. You should never see this exact error message.")
        return 1

    getYamlContent = None
    try:
        if isRemoteYaml:
            getYamlContent = requests.get(registry_url, allow_redirects=True)
        else:
            with open(registry_url, "r") as f:
                getYamlContent = yaml.safe_load(f)
    except requests.exceptions.RequestException as e:
        print(f"[ERR]: Error obtaining registry [{registry_url}]: {e}")
        return 1

    try:
        if isRemoteYaml:
            getYamlContent = yaml.safe_load(getYamlContent.content.decode("utf-8"))
    except yaml.YAMLError as e:
        print(f"[ERR]: Error parsing YAML content of registry [{registry_url}]: {e}")
        return 1
    
    if getYamlContent is None:
        print(f"[ERR]: No content found in registry [{registry_url}].")
        return 1
    
    return getYamlContent

def verify_registry(registry_url) -> int:
    getYamlContent = get_registry(registry_url)
    if getYamlContent == 1:
        return 1

    yamlKeys = getYamlContent.keys()
    verificationsOfYaml = [
        "name" in yamlKeys and getYamlContent.get("name") is not None,
        "description" in yamlKeys and getYamlContent.get("description") is not None,
        "publisher" in yamlKeys and getYamlContent.get("publisher") is not None,
        "updated-on" in yamlKeys and getYamlContent.get("updated-on") is not None,
        getYamlContent.get("namespaces") is not None,
    ]
    
    if all(verificationsOfYaml):
        return getYamlContent
    else:
        print(
            f"""
[ERR]: Registry [{registry_url}] does not contain all necessary fields, which are:

- name
- description
- publisher
- updated-on
- namespaces
    ...where there must be at least 1 namespace.
              """
        )
        return 1


def open_project_yaml(project_yaml_path) -> tuple:
    projectYamlPath = None
    projectYamlContent = None

    if project_yaml_path is not None:
        # verify that the project.yml file exists
        print(f"[INFO]: Opening {project_yaml_path}...")
        with open(project_yaml_path, "r") as f:
            try:
                projectYamlContent = yaml.safe_load(f)
                projectYamlPath = project_yaml_path
            except yaml.YAMLError as e:
                print(f"[ERR]: Error parsing file: {e}")
                return (1, 1)
    else:
        print(f"[INFO]: Opening ./project.yaml...")
        with open("project.yaml", "r") as f:
            try:
                projectYamlContent = yaml.safe_load(f)
                projectYamlPath = "./project.yaml"
            except yaml.YAMLError as e:
                print(f"[ERR]: Error parsing project.yaml file: {e}")
                return (1, 1)

    return (projectYamlPath, projectYamlContent)


def write_to_project_yaml(projectYamlPath, projectYamlContent) -> int:
    with open(projectYamlPath, "w") as f:
        try:
            yaml.dump(projectYamlContent, f, default_flow_style=False)
        except yaml.YAMLError as e:
            print(f"[ERR]: Error writing to project.yaml file: {e}")
            return 1
    return 0


def registries_add(args, context) -> int:
    # verify a valid link was passed in
    yamlContent = verify_registry(args.add)
    if yamlContent == 1:
        return 1  # invalid

    projectYamlPath, projectYamlContent = open_project_yaml(args.project_yaml_path)
    if projectYamlContent == 1:
        return 1

    if projectYamlContent.get("registries") is None:
        projectYamlContent["registries"] = [args.add]
    else:
        if args.add not in projectYamlContent["registries"]:
            projectYamlContent["registries"].append(args.add)
        else:
            print(f"[ERR]: Registry already exists in project.yaml file.")
            return 1
    
    write = write_to_project_yaml(projectYamlPath, projectYamlContent)
    if write == 1:
        return 1

    print(f"[DONE]: Added registry [{args.add}] to project.yaml file.")
    return 0


def registries_validate(args, context) -> int:
    projectYamlPath, projectYamlContent = open_project_yaml(args.project_yaml_path)
    if projectYamlContent == 1:
        return 1

    if projectYamlContent["registries"] is None:
        print(f"[ERR]: No registries found in project.yaml file.")
        return 1

    validRegistries = []

    for registry in projectYamlContent.get("registries"):
        print(f"[INFO]: Validating registry: {registry}")
        yamlContent = verify_registry(registry)
        if yamlContent == 1:
            print(f"[ERR]: Registry [{registry}] is invalid.")
        else:
            validRegistries.append(registry)

    projectYamlContent["registries"] = validRegistries

    write = write_to_project_yaml(projectYamlPath, projectYamlContent)
    if write == 1:
        return 1

    print(f"[DONE]: Validated all registries in project.yaml file.")


def registries_entrypoint(args, context) -> int:
    if args.validate:
        print(f"[INFO]: Validating package registries...")
        return registries_validate(args, context)
    elif args.add:
        print(f"[INFO]: Adding new package registry: {args.add}")
        return registries_add(args, context)
    else:
        print(f"[ERR]: No arguments provided. Please provide a command.")
        return 1
