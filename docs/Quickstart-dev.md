# Quickstart for Package Developers

This document is a quickstart guide for developers who would like to build F Prime packages and release them. We will use an example where a subtopology and component are elements of this package, along with some config objects.

## Initialization

To initialize a new package, first make sure that `fppm` is [installed](../README.md), and then run:

```bash
# if you have a remote git reposiotory created
fppm new --git-url <remote-url>

# if you would like to set up a remote repo later
fppm new
```

Answer the prompts appropriately, especially the *shortname*. All packages are associated with a shortname, which is in the form of `<namespace>/<PackageName>`. Please refer to the [registry documentation](./Registries.md) for detailed information about shortnames. You should notice that a new directory titled by the name of your package is created. 

## Package contents

In that folder, you may notice that the following files exist:

```bash
YourPackage/
├── docs/
│   └── pdd.md
├── CMakeLists.txt
├── library.cmake
├── package.yaml
└── README.md
```

The `package.yaml` file contains crucial information about your package. Ensure that all `package_info` fields are appropriately completed, including the `repo` field. `fppm` expects that all packages are version controlled using a remote Git repo, and are installable via `git` into a project. Additionally, fill in the `fprime_info` fields, indicating what version(s) of F Prime the package has been developed and tested on.

The `docs/` folder is an important folder that contains your package's design document. This file should be completed with ample detail so that users of your package can best understand the inner workings of your package.

The `library.cmake` and `CMakeLists.txt` allow you to link your topology/component source files. Usually, these files contain the same information if you add subdirectories in your package as "fprime subdirectories", but can also set the CMake source list as required.

```cmake
# adding subdirectory
add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/...")

# setting the source list
set(SOURCE_FILES
    "${CMAKE_CURRENT_LIST_DIR}/..."
    "${CMAKE_CURRENT_LIST_DIR}/..."
    ...
)

register_fprime_module()
```

To add a subtopology to the package, you can use `fprime-tools`. If you choose to go this route, your package must be next to a version of an F Prime project.

```bash
# in the devel version of fprime-tools
fprime-util new --subtopology
```

You can also add components to the package by using `fprime-tools`:

```bash
fprime-util new --component
```

Lastly, you can add "config objects", which are files that users can utilize to configure your package. Config objects have certain syntax, and need to be specifically identified in the `package.yaml` file. Please reference the [config objects document](./ConfigObjects.md) for more information.

## Distribution

Once ready to distribute your package, you will need to commit your package to a remote repo, and obtain either a *tag* or *commit hash* as the "stable" version of your package. You will also need to create a ["registry"](./Registries.md) which will host and advertise your package to other fppm users.

> Note that it is possible to install a package without adding it to a registry. Information for that can be seen in the [User's Quickstart guide](./Quickstart-user.md). 

As linked previously, please visit the [registry document](./Registries.md) to learn more about how to set up a registry and the appropriate syntax.

Once your package is version controlled and added to a registry, it is ready for distribution! You should provide end users with the link to the registry that hosts your package, as well as installation/configuration instructions. The template `README.md` file in your package provides a useful place to do this.