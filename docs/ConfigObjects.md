# Config objects: An overview

Config objects are any files in a package that are used for configuring the package by the end user. The benefit with the implementation of config objects is that any file extension can be a config object, even `fpp` files! The only requirement is that the file must be listed within the `package.yaml`, and that special [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/) syntax is used.

## package.yaml

Within the `package.yaml` file, a variable called `config_objects` can be created that includes a list of all of the config objects in the package, with relative paths. For example:

```yaml
# in package.yaml
...

config_objects:
  - Telemetry/{{cookiecutter.td_name}}TopologyDefs.hpp
  - Telemetry/{{cookiecutter.main_top}}Packets.xml
  - Telemetry/Telemetry.fpp
```

## "cookiecutter" syntax

As you can see in the above example, cookiecutter syntax can be used within the file name, and also within the file itself. Variables are determined by `{{ cookiecutter.<VARIABLE_NAME> }}`, primarily so that the cookiecutter Python framework can be used to fill in the files.

Let's take a look at an example config object, `{{cookiecutter.td_name}}TopologyDefs.hpp`. The file includes:

```cpp
@! begin config description
td_name is the name of the topology that is instantiated in your main deployment.
@! end config description

#ifndef TELEMETRY_DEFS_HPP
#define TELEMETRY_DEFS_HPP

...

#endif
```

This file is simple, as the only variable is in the file name. However, variables can also exist in the file itself. Additionally, you may notice the `@! begin config description` and `@! end config description` which denote a block of text which will be displayed to the user in the *fillable*, which is the yaml file users will use to edit the variables.

With this config object, running `fppm config --generate` on this package results in the following yaml file, otherwise known as the fillable:

```yaml
# === START METADATA: DO NOT EDIT ===

__package_path: _fprime_packages/mosallaei.TlmPacketizer
__config_object: Telemetry/{{cookiecutter.td_name}}TopologyDefs.hpp

# === END METADATA ===

# === BEGIN DESCRIPTION ===
# td_name is the name of the topology that is instantiated in your main deployment.
# === END DESCRIPTION ===

# Context: FILE NAME (line 0)
td_name: << FILL IN >>
```

The user can then complete this file, and run `fppm config --apply` on the package to apply this yaml file and cookiecutter to create the final output file. The user should be told where the output files should go, and the best place to put this would be in the package design document.