from fppm.cli.utils import is_valid_name

name = "{{ cookiecutter.package_name }}"

if is_valid_name(name) != "valid":
    raise ValueError(
        f"Unacceptable deployment name: {name}. Do not use spaces or special characters"
    )