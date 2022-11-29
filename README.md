# laureate

laureate generates [Homebrew](https://brew.sh) formulae for Python projects that use [Poetry](https://python-poetry.org).

## Installation

```bash
poetry add laureate
```

## Requirements

laureate can only generate formulae for packages that meet the following criteria:

- The package must be published on PyPI.
- `pyproject.toml` and `poetry.lock` must be present in the directory where laureate is run.
- `pyproject.toml` must specify values for `tool.poetry.name`, `tool.poetry.version`,
  and `tool.poetry.dependencies.python`.
    - `tool.poetry.name` must be a case-insensitive match with the package's name on PyPI.
    - `tool.poetry.version` must match a version of the package that has been published on PyPI.

## Usage

```
Usage: laureate.py [OPTIONS]

  Generate a Homebrew formula for a Poetry project.

Options:
  -o, --output DIRECTORY  The directory to save the formula to. Defaults to the current directory.
  -i, --include TEXT      A group to include.
  -e, --exclude TEXT      A group to exclude.
  --license               See Laureate's license.
  --help                  Show this message and exit.
```

The simplest usage is just:

```bash
laureate
```

which will generate a complete formula for your project in the currrent directory with the name
`<project-name>.rb`.

### `--include` and `--exclude`

If you have multiple groups of dependencies specified in `pyproject.toml`, you can use `--include` and `--exclude` to
control which ones make it into the formula. By default, the `main` group (everything in `tool.poetry.dependencies`) is
included and all other groups are excluded.

Note that:
- Groups specified in `--include` are included in *addition* to `main`. If you wish to exclude
  `main`, you must do so explicitly with ``--exclude``.
- ``--exclude`` takes precedence over ``--include``. Groups specificed in both will be excluded.

#### Example Usage

```bash
# Include the "dev" group.
laureate --include dev

# Include the "dev" and "docs" groups.
laureate --include dev --include docs

# Include the "dev" and "docs" groups, but exclude "main".
laureate --include dev --include docs --exclude main
```


## Differences from homebrew-pypi-poet

laureate pulls information about your package and its dependencies directly from `pyproject.toml`, `poetry.lock`, and
PyPI, eliminating the need to first install your package and its dependencies in a virtual environment before generating
the formula. For generating complete formulae, laurate is far faster and easier to use than homebrew-pypi-poet for this
reason alone.

However, laureate is also far less featured than homebrew-pypi-poet. It *only* supports generating complete formulae;
homebrew-pypi-poet can generate resource stanzas for individual packages and allows for the specification
of additional packages to generate stanzas for at invocation time. laureate also strictly only works with Poetry
projects, whereas homebrew-pypi-poet does not care about your package manager of choice.

laureate was created to fill my own development needs and is being released in the hopes that others may find it useful.
If you require more flexibility than simply generating a complete Homebrew formula for a Poetry project, use
homebrew-pypi-poet.

## License

laureate is licensed under the [MIT License](https://github.com/celsiusnarhwal/laureate/blob/HEAD/LICENSE.md).