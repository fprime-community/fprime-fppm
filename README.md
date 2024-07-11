# fppm - A Package and Dependency Manager for F'

F Prime packages (otherwise known as [libraries](https://nasa.github.io/fprime/HowTo/develop-fprime-libraries.html)) are a way for packaging components, topologies, and/or other F Prime-related elements to prepare for distribution. `fppm` aims to be the method of delivery for these packages.

This tool hopes to make it simpler to share, install and set up F Prime packages across different projects. More and more we notice that many subsystems for flight are being reused in the spirit of "heritage", and thus being able to distribute reusable bits of code is a powerful ability.

`fppm` is provided as a command line tool, with packages being version controlled using Git, and installation being dependent on *registries*. More information on these concepts is provided in the [documentation](./docs/) for this tool.

## Installation

To get started with `fppm`, you can install it onto your system using pip:

```bash
pip install fprime-fppm
```

### Development

To develop `fppm`, it is recommended to install the "test" optional dependencies as well, as that will install the `black` formatter and `pytest`:

```bash
pip install fprime-fppm[test]
```

The `black` formatter should be ran on your branch when making a pull request to this repo. You can also clone this repo for local development, and then install it to your system using:

```bash
pip install --editable .
```