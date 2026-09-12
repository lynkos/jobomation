# Contributing to Jobomation
Thank you for your interest in contributing to Jobomation.

Jobomation is currently in early development, so parts of the architecture and APIs may change as the project evolves. Contributions of code, tests, documentation, design proposals, and bug reports are welcome.

## Getting Started
Before starting:

1. Check the [issue tracker](https://github.com/lynkos/jobomation/issues) for an existing issue related to your proposed change
2. Comment on the issue before starting work so that it can be coordinated and duplicate work can be avoided
3. If an issue is already assigned, please coordinate with the assignee before working on it
4. For substantial features, architectural changes, or issues that are still exploratory, discuss the proposed design in the issue before beginning implementation

Small bug fixes, documentation improvements, and other narrowly scoped changes generally do not require a separate design discussion.

### Development Setup
> [!IMPORTANT]
> These instructions require [Anaconda](https://docs.continuum.io/free/anaconda/install) **OR** [Miniconda](https://docs.conda.io/projects/miniconda/en/latest). Install one before proceeding if Conda is not already available.

1. Confirm Conda is installed
   ```
   conda --version
   ```

2. [Fork the `jobomation` repository](https://github.com/lynkos/jobomation/fork)

3. Enter the directory you want your fork of `jobomation` to be cloned in
   ```sh
   cd ~/path/to/directory
   ```

4. Clone and enter your fork of `jobomation`
   ```sh
   git clone https://github.com/<your-username>/jobomation.git && cd jobomation
   ```

5. Create Conda environment (`job_env`) from [`environment.yml`](../environment.yml)
   ```sh
   conda env create -f environment.yml
   ```

6. Activate Conda environment (`job_env`)
   ```sh
   conda activate job_env
   ```

7. Install `jobomation` and its dependencies
   ```sh
   python -m pip install -e ".[dev]"
   ```

### Testing
To run all tests:
   ```sh
   pytest -v
   ```

You can run a specific test module for a single subsystem, e.g. [`models.py`](../src/jobomation/models.py):
   ```sh
   pytest tests/test_models.py -v
   ```

Tests should be deterministic and should not depend on live external services when those interactions can instead be represented using mocks or saved fixtures.

## Making Changes
Create a branch with a descriptive name (e.g. `feature/new-functionality` or `bugfix/issue-123`) from the latest `main` branch before making your changes.

Keep changes focused on a single issue or logical unit of work. Avoid unrelated refactoring or formatting changes in the same pull request.

When modifying existing functionality:

* Follow the existing code structure and conventions
* Add or update tests for behavior affected by the change
* Respect the project's existing separation between collection, persistence, filtering, evaluation, ranking, and presentation layers unless the proposed change specifically involves revisiting that architecture
* Update documentation when changing user-facing behavior, configuration, public interfaces, or architecture

For architectural context and planned functionality, see [`docs/DESIGN.md`](DESIGN.md).

### Pull Requests
Before creating a pull request, please verify that your changes meet all relevant criteria in the pull request template.

Pull requests should be reviewable and linked to the issue they address when applicable. They should also explain both **what changed** and **why**. The pull request template will prompt you for the necessary information.

Small, focused pull requests are preferred over large changes containing multiple unrelated features. If additional work is discovered while implementing an issue, consider opening a separate issue or pull request rather than expanding the current PR substantially.

Draft pull requests are welcome for work in progress, especially when early feedback on an implementation or design would be useful.

### Review
A maintainer may request changes before a pull request is merged. When addressing review feedback, update the existing pull request rather than opening a replacement.

Avoid force-pushing after review has begun unless necessary, since rewriting history can make changes harder to review.

Not every proposed implementation is guaranteed to be merged, particularly while parts of Jobomation's architecture are still evolving. Discussing substantial design decisions before implementation can help avoid unnecessary work.

### Creating Issues
Before opening a new issue, please search [existing issues](https://github.com/lynkos/jobomation/issues) to see whether the topic has already been discussed.

#### Bug Reports
Bug reports should include enough information to reproduce the problem where possible.

#### Proposed Features
Feature proposals should describe:

* The problem or use case
* The proposed behavior
* Why the feature belongs in Jobomation
* Relevant implementation or architectural considerations, if known

Large features may be broken into smaller design and implementation issues before development begins.

## License
By contributing to Jobomation, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE.md).