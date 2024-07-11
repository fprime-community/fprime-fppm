# CLI Commands

This file provides an overview of all of the commands that are available with `fppm`. All sections flow down from `fppm`, which is the command prefix. So `fppm > install > --package` = `fppm install --package`.

## `install`

This command installs a package or all packages referenced inside a `project.yaml` file.

### `--package` or `-p`

**Required**: False \
**Takes**: String (package shortname) \
**Desc**: Installs a package given a shortname

#### `--version` or `-v`

**Required**: False \
**Takes**: String (tag or commit hash) \
**Desc**: Install a specific version of the package.

#### `--project-yaml-path`

**Required**: False \
**Takes**: String (path/to/project.yaml) \
**Desc**: Specifies location to project.yaml. Defaults to `./project.yaml`.

### `--project`

**Required**: False \
**Takes**: N/A, boolean flag \
**Desc**: Installs all packages referenced in a provided `project.yaml` file.

#### `--project-yaml-path`

**Required**: False \
**Takes**: String (path/to/project.yaml) \
**Desc**: Specifies location to project.yaml. Defaults to `./project.yaml`.

## `registries`

This command deals with registries, and specifically modifying the `project.yaml` to add registries.

### `--validate` or `-v`

**Required**: False \
**Takes**: N/A, boolean flag \
**Desc**: Validates the registries in the project.yaml file.

#### `--project-yaml-path`

**Required**: False \
**Takes**: String (path/to/project.yaml) \
**Desc**: Specifies location to project.yaml. Defaults to `./project.yaml`.

### `--add` or `-a`

**Required**: False \
**Takes**: String (url or path/to/registry.yaml) \
**Desc**: Adds a registry to the project.yaml file.

#### `--project-yaml-path`

**Required**: False \
**Takes**: String (path/to/project.yaml) \
**Desc**: Specifies location to project.yaml. Defaults to `./project.yaml`.

## `new`

This creates a new directory for an F Prime package.

### `--git-url`

**Required**: False \
**Takes**: URL \
**Desc**: Remote repo URL to initialize your package with.

## `init`

Initializes an existing F Prime project with the appropriate file and contents required to work with F Prime packages.

## `remove`

Remove an F Prime package.

### `--package` or `-p`

**Required**: False \
**Takes**: String (package shortname) \
**Desc**: Removes the package with this shortname

#### `--project-yaml-path`

**Required**: False \
**Takes**: String (path/to/project.yaml) \
**Desc**: Specifies location to project.yaml. Defaults to `./project.yaml`.

## `config`

This command works with config objects for packages.

### `--generate` or `-g`

**Required**: False \
**Takes**: String (package shortname) \
**Desc**: Generate the fillable files for the config objects given the package.

#### `--project-yaml-path`

**Required**: False \
**Takes**: String (path/to/project.yaml) \
**Desc**: Specifies location to project.yaml. Defaults to `./project.yaml`.

### `--apply ` or `-a`

**Required**: False \
**Takes**: String (package shortname) \
**Desc**: Apply the fillables using cookiecutter to generate output files.