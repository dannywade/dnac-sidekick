# Contributing to DNAC Sidekick

This project welcomes contributions in the form of Pull Requests. For clear bug-fixes / typos etc. just submit a PR. For new features or if there is any doubt in how to fix a bug, feel free to open an issue.

## Prerequisites

DNAC Sidekick uses poetry for packaging and dependency management. To start developing, install Poetry using the recommended method.

Next, you'll need to create a fork (your own personal copy) of the DNAC Sidekick repository, and clone that fork on to your local machine. GitHub offers a great tutorial for this process here. After following this guide, you'll have a local copy of the project installed.

Enter the directory containing your copy of DNAC Sidekick.

Poetry can be used to create an isolated virtual environment for the project:

`poetry shell`

The first time we run poetry shell, such an isolated environment is created and forever associated with our project. Any time we wish to enter this virtual environment again, we simply run poetry shell again.

Now we can install the dependencies of DNAC Sidekick into the virtual environment:

`poetry install`

If you choose not to use poetry (not recommended), you may also create a virtual environment using the old fashion Python `venv` module and install the package locally using `make install` or using the following command:

`pip install -e .`

The rest of this guide assumes you're inside the virtual environment. If you're having difficulty running any of the commands that follow, ensure you're inside the virtual environment by running `poetry shell` or `source venv/bin/activate`.

## Developing

At this point, you're ready to start developing. Before each commit, you should:
- Run the tests and ensure they pass (`make test`)
- Format the code using black (`make format`)

These steps are described in the following sections.

## Tests

Run tests with the following command:

`make test`

Or if you don't have make, run the following command from the root of the project directory:

`pytest tests -v --cov=./dnac_sidekick`

New code should ideally have tests and not break existing tests.

The "Coverage Report" that gets printed to the terminal after the tests run can be used to identify lines of code that haven't been covered by tests. If any of the new lines you've added or modified appear in this report, you should strongly consider adding tests which exercise them.

## Code Formatting

DNAC Sidekick uses black for code formatting. I recommend setting up black in your editor to format on save.

To run black from the command line, use `make format-check` to check your formatting, and use `make format` to format and make changes to the files.

## Creating A Pull Request

Once your happy with your change and have ensured that all steps above have been followed (and checks have passed), you can create a pull request. GitHub offers a guide on how to do this. Please ensure that you include a good description of what your change does in your pull request, and link it to any relevant issues or discussions.

When you create your pull request, we'll run the checks described earlier. If they fail, please attempt to fix them as we're unlikely to be able to review your code until then. If you've exhausted all options on trying to fix a failing check, feel free to leave a note saying so in the pull request and someone may be able to offer assistance.

## Code Review

After the checks in your pull request pass, someone will review your code. There may be some discussion and, in most cases, a few iterations will be required to find a solution that works best.

When the pull request is approved, it will be merged into the main branch. Your change will only be available to users the next time DNAC Sidekick is released.

<hr>

Credit to the [Rich](https://github.com/Textualize/rich) project for their well-written contributing document, which was used to help write this document.