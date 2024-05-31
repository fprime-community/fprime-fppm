import validators
import requests
import yaml

# stubs for readability
def verify_registry(registry_url) -> int : ...
def open_project_yaml(project_yaml_path) -> tuple : ...
def write_to_project_yaml(projectYamlPath, projectYamlContent) -> int : ...
def registries_add(args, context) -> int : ...
def registries_validate(args, context) -> int : ...
def registries_entrypoint(args, context) -> int : ...

def verify_registry(registry_url) -> int:
    if registry_url is not None:
        if validators.url(registry_url):
            if registry_url.endswith(".yaml"): # https://stackoverflow.com/a/21059164
                pass
            else:
                print(f"[ERR]: Invalid URL [{registry_url}]: link must end in .yaml")
                return 1
        else:
            print(f"[ERR]: Invalid URL [{registry_url}]: generally malformed.")
            return 1
    else:
        print(f"[ERR]: No URL provided. You should never see this exact error message.")
        return 1
    
    getYamlContent = None
    try:
        getYamlContent = requests.get(registry_url, allow_redirects=True)
    except requests.exceptions.RequestException as e:
        print(f"[ERR]: Error remotely obtaining registry [{registry_url}]: {e}")
        return 1
    
    try:
        getYamlContent = yaml.safe_load(getYamlContent.content.decode("utf-8"))
    except yaml.YAMLError as e:
        print(f"[ERR]: Error parsing YAML content of registry [{registry_url}]: {e}")
        return 1
    
    if getYamlContent is None:
        print(f"[ERR]: No content found in registry [{registry_url}].")
        return 1
    
    verificationsOfYaml = [
        hasattr('name') and getYamlContent['name'] is not None,
        hasattr('description') and getYamlContent['description'] is not None,
        hasattr('publisher') and getYamlContent['publisher'] is not None,
        hasattr('updated-on') and getYamlContent['updated-on'] is not None,
        getYamlContent['namespaces'] is not None
    ]
    
    if all(verificationsOfYaml):
        return getYamlContent
    else:
        print(f"""
[ERR]: Registry [{registry_url}] does not contain all necessary fields, which are:

- name
- description
- publisher
- updated-on
- namespaces
    ...where there must be at least 1 namespace.
              """)
        return 1
    
def open_project_yaml(project_yaml_path) -> tuple:
    projectYamlPath = None
    projectYamlContent = None
    
    if project_yaml_path is not None:
        # verify that the project.yml file exists
        print(f"[INFO]: Opening project.yaml file at {project_yaml_path}")
        with open(project_yaml_path, 'r') as f:
            try:
                projectYamlContent = yaml.safe_load(f)
                projectYamlPath = project_yaml_path
            except yaml.YAMLError as e:
                print(f"[ERR]: Error parsing project.yaml file: {e}")
                return (1,1)
    else:
        print(f"[INFO]: Opening project.yml file at ./project.yaml")
        with open('project.yaml', 'r') as f:
            try:
                projectYamlContent = yaml.safe_load(f)
                projectYamlPath = './project.yaml'
            except yaml.YAMLError as e:
                print(f"[ERR]: Error parsing project.yaml file: {e}")
                return (1,1) 
            
    return (projectYamlPath, projectYamlContent)

def write_to_project_yaml(projectYamlPath, projectYamlContent) -> int:
    with open(projectYamlPath, 'w') as f:
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
        return 1 # invalid
    
    projectYamlPath, projectYamlContent = open_project_yaml(args.project_yaml_path)
    if projectYamlContent == 1:
        return 1
            
    if projectYamlContent['registries'] is None:
        projectYamlContent['registries'] = [args.add]
    else:
        if args.add not in projectYamlContent['registries']:
            projectYamlContent['registries'].append(args.add)
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
    
    if projectYamlContent['registries'] is None:
        print(f"[ERR]: No registries found in project.yaml file.")
        return 1
    
    validRegistries = []

    for registry in projectYamlContent['registries']:
        print(f"[INFO]: Validating registry: {registry}")
        yamlContent = verify_registry(registry)
        if yamlContent == 1:
            print(f"[ERR]: Registry [{registry}] is invalid.")
        else:
            validRegistries.append(registry)
            
    projectYamlContent['registries'] = validRegistries
    
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