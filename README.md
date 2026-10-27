# project-init

An opinionated command-line tool that automates the creation of (Python) projects. It scaffolds a new project using uv, injects a custom .gitignore, creates a remote GitHub repository via the GitHub API, and automatically commits and pushes the initial code.

## Prerequisites

### Global Dependencies (needed for all projects)

- **Git:** Must be installed and configured with a name and email globally or with a local .gitconfig.
    - Name set with `git config --global user.name`
    - Email set with `git config --global user.email`

- **GitHub SSH:** Your machine must be configured to communicate with GitHub with SSH, as this script pushes using the `git@github.com` remote URL to avoid password prompts.

- **GitHub Fine-grained API Token:** Must be configured with the following permissions:
    - **Resource owner:** Your personal GitHub account.
    - **Repository access:** "All repositories" (Required because the script creates a repository that does not exist yet).
    - **Repository permissions:**
        - **Repository creation:** Read and write (Or "Administration" if you are on an older GitHub Enterprise server).
        - **Contents:** Read and write.

### Python Dependencies

- uv: Must be installed, used for initializing the project structure.

## Installation

Get it from [releases](https://github.com/newbluecat/project-init/releases).

## Assumptions

This project was primarily made for me, and so there are things that I like that are hardcoded into the project.

- The tool relies on the `keyring` Python library. Depending on your Linux distribution, you may need to ensure a backend like gnome-keyring or KWallet is installed and unlocked on your machine for the token to save correctly.

### Python

- The script automatically appends specific Ruff linting configurations (e.g., line-length to 120, PEP257 convention) to the bottom of the generated pyproject.toml. If you change your preferred linting rules, you must modify the _python_build.py file and reinstall the tool.

> [!NOTE]
> TBD: Set ~/.config to contain template files instead.

- The script assumes you have a custom .gitignore template located exactly at ~/Projects/extras. If this file exists, it will overwrite the default uv gitignore. If it does not exist, the script falls back to the default uv .gitignore.

## Usage

> [!NOTE]
> The first time you run the tool, pass your GitHub token using the -t flag. The tool uses Python's `keyring` library to securely save this token to your operating system's native credential manager.
>
> ```text
> /path/to/project-init python my-new-project -d "Project description" -t github_token
> ```
>
> Since the token has now been saved, you can omit it from future runs.
>
> ```text
> /path/to/project-init python my-new-project -d "Project description"
> ```

| Option / Flag         | Description                                                                        |
|-----------------------|------------------------------------------------------------------------------------|
| `-d`, `--description` | Sets the project description for the initialized project and remote repository.    |
| `-p`, `--private`     | Marks the created GitHub repository as private rather than public.                 |
| `-t`, `--token`       | Accepts the GitHub PAT to store securely in the operating system's native keyring. |
