import sys
from subprocess import CalledProcessError, check_call, call, DEVNULL


def _check_call_quiet(commands: list[str], *, shell: bool=False) -> None:
    try:
        check_call(commands, shell=shell)
    except CalledProcessError as error:
        sys.exit(error.returncode)


def format() -> None:
    _check_call_quiet(["black", "--check", "--diff", "src/", "tests/"])
    _check_call_quiet(["isort", "--check", "--diff", "src", "tests"])
    _check_call_quiet(
        "find src/ -name *.html | xargs djhtml --tabwidth 2 --check",
        shell=True,
    )


def reformat() -> None:
    _check_call_quiet(["black", "src/", "tests/"])
    _check_call_quiet(["isort", "src", "tests"])
    _check_call_quiet(
        "find src/ -name *.html | xargs djhtml --tabwidth 2 --in-place",
        shell=True,
    )


def lint() -> None:
    _check_call_quiet(["mypy", "src/backend/", "tests/"])
    _check_call_quiet(["flake8", "src/", "tests/"])
    _check_call_quiet(["vulture", "src/"])
    _check_call_quiet(["bandit", "-r", "src/"])


def test() -> None:
    recreate_db("tozo_test")
    _check_call_quiet(["pytest", "tests/", *sys.argv[1:]])


def create_db(database: str = "tozo") -> None:
    call(
        ["psql", "-U", "postgres", "-c", "CREATE USER tozo LOGIN PASSWORD 'tozo' CREATEDB"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )
    call(
        ["psql", "-U", "postgres", "-c", f"CREATE DATABASE {database}"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )


def drop_db(database: str = "tozo") -> None:
    call(
        ["psql", "-U", "postgres", "-c", f"DROP DATABASE {database}"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )
    call(
        ["psql", "-U", "postgres", "-c", "DROP USER tozo"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )


def recreate_db(database: str = "tozo") -> None:
    drop_db(database)
    create_db(database)


def test_ci() -> None:
    _check_call_quiet(["pytest", "tests/", *sys.argv[1:]])
