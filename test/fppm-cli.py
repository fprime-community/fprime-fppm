# testing done with pytest
import fppm.cli.commands.new as cmd_new
import fppm.cli.commands.init as cmd_init
import fppm.cli.commands.registries as cmd_registries
from argparse import Namespace
import os
import shutil
import pytest

def setup_test_env():
    # make tmp directory here
    try:
        os.mkdir("tmp")
    except FileExistsError:
        pass
    
    os.chdir("tmp")
    
def teardown_test_env():
    # remove tmp directory here
    # verify that we are in the correct directory
    if os.getcwd().split("/")[-1] == "tmp":
        os.chdir("..")
        shutil.rmtree("tmp", ignore_errors=True)
        
def test_registries_add():
    setup_test_env()
    
    context1 = {
        "extra_context": {
            "project_name": "TESTING",
            "project_author": "Ali Mosallaei",
            "project_desc": "This is a test project"
        },
        "sac": "y"
    }
    
    os.mkdir("fprime")
    assert cmd_init.create_project_yaml_file(None, context1) == 0 # should pass
    print(f"[INFO]: Project.yaml created")
    
    cmd_registries.registries_add(Namespace(add="blah", project_yaml_path="project.yaml"), None) == 1 # should fail, invalid URL
    print(f"[INFO]: Test Registries.1 passed")
    
    cmd_registries.registries_add(Namespace(add="../static/broken-registry.yaml", project_yaml_path="project.yaml"), None) == 1 # should fail, not working registry
    print(f"[INFO]: Test Registries.2 passed")
    
    cmd_registries.registries_add(Namespace(add="../static/working-registry.yaml", project_yaml_path="project.yaml"), None) == 0 # should pass
    print(f"[INFO]: Test Registries.3 passed")
    
    # uncomment to test a remote registry
    # cmd_registries.registries_add(Namespace(add="http://localhost:5000/static/registry.yaml", project_yaml_path="project.yaml"), None) == 0 # should pass
    # print(f"[INFO]: Test Registries.4 passed")
    
    teardown_test_env()
            
def test_registries_validation():  
    assert cmd_registries.verify_registry("blah") == 1 # should fail, invalid URL
    print(f"[INFO]: Test Registries.1 passed")
    
    assert cmd_registries.verify_registry("static/broken-registry.yaml") == 1 # should fail, not working registry
    print(f"[INFO]: Test Registries.2 passed")
    
    assert cmd_registries.verify_registry("static/working-registry.yaml") != 1 # should pass
    print(f"[INFO]: Test Registries.3 passed")
    
    # uncomment to test a remote registry
    # assert cmd_registries.verify_registry("http://localhost:5000/static/registry.yaml") != 1 # should pass
    # print(f"[INFO]: Test Registries.4 passed")
    
def test_init():
    setup_test_env()
    
    assert cmd_init.create_project_yaml_file(None, None) == 1 # should fail, not in fprime directory
    print(f"[INFO]: Test Init.1 passed")
    
    context1 = {
        "extra_context": {
            "project_name": "TESTING",
            "project_author": "Ali Mosallaei",
            "project_desc": "This is a test project"
        },
        "sac": "y"
    }
    
    os.mkdir("fprime")
    assert cmd_init.create_project_yaml_file(None, context1) == 0 # should pass
    print(f"[INFO]: Test Init.2 passed")
    
    os.remove("project.yaml")
    context1["extra_context"]["project_name"] = "TESTING 2"
    
    try:
        cmd_init.create_project_yaml_file(None, context1) == 0 # should fail, invalid name
        assert False
    except:
        print(f"[INFO]: Test Init.3 passed")
    
    teardown_test_env()

def test_new_with_args():
    setup_test_env()
    
    context1 = {
        "extra_context": {
            "package_actual_name": '@mosallaei/testing',
            "package_name": 'testing',
            "author": "Ali Mosallaei",
            "package_desc": "This is a test package"
        },
        "inputs": {
            "git": "n"
        }
    }
    
    args = Namespace(
        command = "new",
        git_url = "blah"
    )
    
    assert cmd_new.create_new_package_yml(args, context1) == 1 # should fail; git URL is invalid
    print(f"[INFO]: Test New.1 passed")
    
    args.git_url = None
    assert cmd_new.create_new_package_yml(args, context1) == 0 # should pass
    print(f"[INFO]: Test New.2 passed")
    
    args.git_url = "https://github.com/mosa11aei/fprime-fppm"
    assert cmd_new.create_new_package_yml(args, context1) == 1 # should fail, same name directory
    print(f"[INFO]: Test New.3 passed")
    
    context1["extra_context"]["package_name"] = "testing2"
    assert cmd_new.create_new_package_yml(args, context1) == 0 # should pass
    print(f"[INFO]: Test New.4 passed")
    
    context1["extra_context"]["package_name"] = "testing 3"
    try:
        cmd_new.create_new_package_yml(args, context1) # should fail, invalid name
        assert False
    except:
        print(f"[INFO]: Test New.5 passed")
    
    teardown_test_env()    
    