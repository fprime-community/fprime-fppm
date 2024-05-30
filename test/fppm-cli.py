# testing done with pytest
import fppm.cli.commands.new as cmd_new
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
    
    