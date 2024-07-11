# Registries in fppm

In this tool, packages are distributed in the form of distributed registries. The benefit of this is that a single developer can release all of their packages under a single registry with a single, unique namespace. This allows package names to not have to be unique, as may be the case with something like UART drivers for different platforms.

Additionally, since F Prime is a framework that has been utilized at different levels of industry and academia, it may be the case that an organization would like to protect their components from the public by providing a (for example) VPN-based registry.

## Registry file structure

All fppm registry files are recommended to be named `registry.yaml`, however it is not enforced. The registry file includes details about the registry owner, as well as namespaces and their related packages. The required metadata for the registry file is included here:

```yaml
# in registry.yaml, all fields required

name: "SampleRegistry"
publisher: "F Prime"
description: "Sample F Prime Package Registry"
updated-on: 10 JUL 2024
```

Then, each namespace is listed under the "namespace" key. Each namespace can contain a list of packages. Each package contains its full shortname, the remote repo link, and the version for the "stable" package. Versions can either be git tags (like those attached to releases), or commit hashes. In the case of commit hashes, a "branch" key must also be included. 

A complete registry file then looks like:

```yaml
name: "SampleRegistry"
publisher: "F Prime"
description: "Sample F Prime Package Registry"
updated-on: 10 JUL 2024

namespaces:
  - MyNamespace:
    - RandomPackage:
        git: https://github.com/random/package  
        stable: abcdefg
        branch: main
```

In this example, `MyNamespace` is the namespace of the package, and `RandomPackage` is the package itself. Thus, the shortname for `RandomPackage`, and what is required to install the package, is `MyNamespace/RandomPackage`. 

One registry file can include multiple namespaces, which may be useful if you have a "devel" set of packages, and a "release" set of packages. This entire file can then be distributed to users who may use your packages. It is recommended that this file is hosted on the web, such that the file can remain up to date for the user as you make changes.

## Adding the registry to a project

In an fppm-enabled project (one that has a proper `project.yaml` file) one can run:

```bash
fppm registries --add <url or path/to/registry.yaml>
```

to add your registry to their project. An example registry with valid packages can be seen hosted at [this link](https://mosa11aei.github.io/fppm-registry/static/registry.yaml).