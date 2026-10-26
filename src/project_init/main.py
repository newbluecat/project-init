"""CLI for initializing projects and syncing them with a GitHub repository."""

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import keyring
import keyring.errors

from project_init._python_builder import init_python


def run_cmd(cmd: list[str], cwd: Path | str | None = None) -> None:
    """Execute a shell command and exits on failure."""
    try:
        subprocess.run(cmd, check=True, text=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def check_global() -> None:
    """Verify that globally required command line tools are installed."""
    if shutil.which("git") is None:
        print("Error: 'git' is not installed or not in PATH. Please install it first.")
        sys.exit(1)


def create_github_repo(name: str, description: str, *, private: bool, token: str) -> str | None:
    """Create a GitHub repository via API and returns the clone URL."""
    url: str = "https://api.github.com/user/repos"
    headers: dict[str, str] = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    data: dict[str, str | bool] = {
        "name": name,
        "description": description,
        "private": private,
    }

    req: urllib.request.Request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            resp_data: dict[str, object] = json.loads(response.read().decode("utf-8"))
            clone_url: object = resp_data.get("clone_url")

            if isinstance(clone_url, str):
                return clone_url
            return None
    except urllib.error.HTTPError as e:
        print(f"Failed to create GitHub repo. HTTP {e.code}: {e.read().decode('utf-8')}")
        return None


def save_token(token: str) -> None:
    """Save the GitHub token securely to the OS keyring."""
    try:
        keyring.set_password("project-init", "github_token", token)
    except keyring.errors.NoKeyringError:
        print("Warning: No OS keyring found. Token will not be saved.")
    except keyring.errors.PasswordSetError:
        print("Warning: Keyring refused to save the token (is the vault locked?)")
    except keyring.errors.KeyringError as e:
        print(f"Warning: Keyring operation failed: {e}")

    # there may be unexpected OS vault crashes that aren't caught with other exceptions
    except Exception as e:
        print(f"Warning: Unexpected OS error while accessing keyring: {e}")


def load_token() -> str | None:
    """Load the GitHub token securely from the OS keyring."""
    try:
        return keyring.get_password("project-init", "github_token")
    except keyring.errors.KeyringError:
        return None


def handle_python(args: argparse.Namespace) -> None:
    """Pass correct arguments from namespace to init_python."""
    init_python(args.name, args.description)


def main() -> None:
    """Run project-init with args."""
    common_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        add_help=False,
        usage="project-init [lang] [OPTIONS]",
    )
    common_parser.add_argument("name", type=str, help="Name of project and repo")
    common_parser.add_argument("-d", "--description", type=str, default="A new project :)", help="Project description")
    common_parser.add_argument(
        "--private",
        action="store_true",
        help="Upload to private GitHub repo",
    )
    common_parser.add_argument("-t", "--token", type=str, help="GitHub API token")

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="project-init",
        description="Initialize and project and link it to a GitHub repo.",
    )

    subparsers = parser.add_subparsers(required=True, help="Target language")

    parser_python: argparse.ArgumentParser = subparsers.add_parser(
        "python",
        parents=[common_parser],
        help="Initialize a Python project with uv",
    )
    parser_python.set_defaults(func=handle_python)

    args: argparse.Namespace = parser.parse_args()

    if args.token is not None:
        token = args.token
        save_token(token)
    else:
        token = load_token()

    if token is None:
        print("Error: GitHub token missing.")
        print("Provide it via -t/--token on first run to save it permanently.")
        sys.exit(1)

    check_global()
    args.func(args)

    name: str = args.name
    desc: str = args.description
    project_dir: Path = Path(name).resolve()

    git_dir: Path = project_dir / ".git"
    if not git_dir.exists():
        run_cmd(["git", "init"], cwd=project_dir)

    clone_url: str | None = create_github_repo(name, desc, private=args.private, token=token)
    if clone_url is None:
        print("Aborting git push due to GitHub API failure.")
        sys.exit(1)

    print("Committing and pushing to GitHub...")
    run_cmd(["git", "add", "."], cwd=project_dir)
    run_cmd(["git", "commit", "-m", "Initial commit"], cwd=project_dir)
    run_cmd(["git", "branch", "-M", "main"], cwd=project_dir)
    run_cmd(["git", "remote", "add", "origin", clone_url], cwd=project_dir)
    run_cmd(["git", "push", "-u", "origin", "main"], cwd=project_dir)

    print(f"Done! Project '{name}' is ready locally and on GitHub.")


if __name__ == "__main__":
    main()
