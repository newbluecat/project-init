import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path | None = None) -> None:
    """Execute a shell command and exits on failure."""
    try:
        subprocess.run(cmd, check=True, text=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        sys.exit(e.returncode)


def check_python() -> None:
    """Verify that globally required command line tools are installed."""
    if shutil.which("uv") is None:
        print("Error: 'uv' is not installed or not in PATH. Please install it first.")
        sys.exit(1)


def init_python(name: str, desc: str) -> None:
    """Initialize a Python project with uv and description."""
    check_python()

    print(f"Initializing Python (uv) project: {name}...")
    run_cmd(["uv", "init", name])

    project_dir: Path = Path(name).resolve()
    toml_path: Path = project_dir / "pyproject.toml"

    if toml_path.exists():
        content: str = toml_path.read_text()
        extras = (
            "\n[tool.ruff]\n"
            "line-length = 120\n"
            "\n"
            "[tool.ruff.lint]\n"
            'select = ["ALL"]\n'
            "[tool.ruff.lint.pydocstyle]\n"
            'convention = "pep257"\n'
        )

        content = content.replace(
            'description = "Add your description here"',
            f'description = "{desc}"',
        )
        content += extras

        toml_path.write_text(content)
        shutil.copyfile("~/Projects/extras/.gitignore-python", project_dir)

        print("Updated pyproject.toml with description.")
