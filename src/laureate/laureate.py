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


def main(output: Path, groups: set, wheel: bool):
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

        if wheel:
            dist_info = next(filter(lambda x: x["packagetype"] == "bdist_wheel", root_pkg_info["urls"]))
        else:
            dist_info = next(filter(lambda x: x["packagetype"] == "sdist", root_pkg_info["urls"]))

        root_pkg["url"] = dist_info["url"]
        root_pkg["checksum"] = dist_info["digests"]["sha256"]

        for dependency in lockfile["package"]:
            if dependency["category"] in groups:
                pkg = {
                    "name": dependency["name"],
                }

                pkg_info = get_package_info(pkg["name"], dependency["version"])

                if wheel:
                    dist_info = next(filter(lambda url: url["packagetype"] == "bdist_wheel", pkg_info["urls"]))
                else:
                    dist_info = next(filter(lambda url: url["packagetype"] == "sdist", pkg_info["urls"]))

                pkg["url"] = dist_info["url"]
                pkg["checksum"] = dist_info["digests"]["sha256"]


                dependencies.append(pkg)

        formula = FORMULA_TEMPLATE.render(package=root_pkg, resources=dependencies)

        (output / f"{root_pkg['name']}.rb").write_text(formula)


@click.command()
@click.option("-o", "--output", "output", type=click.Path(exists=True, file_okay=False),
              help="The directory to save the formula to. Defaults to the current directory.")
@click.option("-i", "--include", "include", multiple=True, help="A group to include.")
@click.option("-e", "--exclude", "exclude", multiple=True, help="A group to exclude.")
@click.option("-w", "--wheel", "wheel", is_flag=True, help="Use wheels instead of sdists.")
@click.option("--license", "show_license", is_flag=True, help="See laureate's license.")
def cli(output: str = None, include: tuple = None, exclude: tuple = None, wheel: bool =False,
        show_license: bool = False):
    """
    Generate a Homebrew formula for a Poetry project
    """
    if show_license:
        print((Path(__file__).parent / "LICENSE.md").read_text())
    else:
        output = Path(output) if output else Path.cwd()

        include = set(include) if include else set()
        exclude = set(exclude) if exclude else set()
        include.add("main")

        main(output, include.difference(exclude), wheel)


if __name__ == '__main__':
    cli()
