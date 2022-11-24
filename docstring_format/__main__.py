import typer
from .base import ScriptFile


def format(file_path: str):
    script = ScriptFile(file_path)
    script.write_clean()


if __name__ == '__main__':
    typer.run(format)
