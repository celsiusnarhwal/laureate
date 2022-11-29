import re
from pathlib import Path

import click
import requests
import toml

from .templates import FORMULA_TEMPLATE


def get_package_info(package: str, version: str):
    response = requests.get(f"https://pypi.org/pypi/{package}/{version}/json")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Laureate couldn't get package info for {package} {version}.")


def main(output: Path, groups: set):
    with Path.cwd():
        pyproject = toml.load("pyproject.toml")
        lockfile = toml.load("poetry.lock")
        tool_poetry = pyproject["tool"]["poetry"]
        dependencies = []

        root_pkg = {
            "name": tool_poetry["name"],
            "version": tool_poetry["version"],
            "description": tool_poetry.get("description") or "",
            "homepage": tool_poetry.get("homepage") or "",
            "python": "python" + str(int(float(re.search(r"\d.*", tool_poetry["dependencies"]["python"]).group())))
        }

        root_pkg_info = get_package_info(root_pkg["name"], root_pkg["version"])
        root_pkg["url"] = root_pkg_info["urls"][0]["url"]
        root_pkg["checksum"] = root_pkg_info["urls"][0]["digests"]["sha256"]

        for dependency in lockfile["package"]:
            if dependency["category"] in groups:
                pkg = {
                    "name": dependency["name"],
                    "url": get_package_info(dependency["name"], dependency["version"])["urls"][0]["url"],
                    "checksum": get_package_info(dependency["name"], dependency["version"])["urls"][0]["digests"][
                        "sha256"]
                }

                dependencies.append(pkg)

        formula = FORMULA_TEMPLATE.render(package=root_pkg, resources=dependencies)

        (output / f"{root_pkg['name']}.rb").write_text(formula)


@click.command()
@click.option("-o", "--output", "output", type=click.Path(exists=True, file_okay=False),
              help="The directory to save the formula to. Defaults to the current directory.")
@click.option("-i", "--include", "include", multiple=True, help="A group to include.")
@click.option("-e", "--exclude", "exclude", multiple=True, help="A group to exclude.")
@click.option("-v", "--version", "version", is_flag=True, help="See laureate's version.")
@click.option("--license", "show_license", is_flag=True, help="See laureate's license.")
def cli(output: str = None, include: tuple = None, exclude: tuple = None, version: bool = False,
        show_license: bool = False):
    """
    Generate a Homebrew formula for a Poetry project.
    """
    if version:
        print(toml.load("pyproject.toml")["tool"]["poetry"]["version"])
    elif show_license:
        print((Path(__file__).parent / "LICENSE.md").read_text())
    else:
        output = Path(output) if output else Path.cwd()

        include = set(include) if include else set()
        exclude = set(exclude) if exclude else set()
        include.add("main")

        main(output, include.difference(exclude))


if __name__ == '__main__':
    cli()
