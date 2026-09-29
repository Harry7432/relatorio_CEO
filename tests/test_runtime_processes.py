import hashlib
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
BASE_DIGEST = "sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6"
RUN_DOCKER_SMOKE = os.getenv("RUN_DOCKER_SMOKE") == "1"


def run(*command: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def test_python_and_dependency_inputs_are_pinned() -> None:
    assert (ROOT / ".python-version").read_text().strip() == "3.13.14"

    for lock_name in ("requirements.txt", "requirements-dev.txt"):
        lock = (ROOT / lock_name).read_text()
        requirements = [
            line
            for line in lock.splitlines()
            if line and not line[0].isspace() and not line.startswith(("#", "--"))
        ]
        assert requirements
        assert all("==" in requirement for requirement in requirements)
        assert "--hash=sha256:" in lock


def test_build_artifact_contract_is_recorded_verbatim() -> None:
    model = (ROOT / "specs/003-production-runtime/data-model.md").read_text()
    constraints = {
        "source_revision": "Commit ou revisao unica, obrigatoria e nao secreta.",
        "python_version": "Exatamente `3.13.14` nesta feature.",
        "base_image_digest": "Digest SHA-256 obrigatorio da imagem base.",
        "dependency_lock_digest": "Hash do lock de producao versionado.",
        "image_digest": "Digest imutavel produzido pelo build.",
    }

    for field, constraint in constraints.items():
        assert f"`{field}`" in model
        assert constraint in model


def test_dockerfile_defines_reproducible_non_root_artifact() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()

    assert f"python:3.13.14-slim@{BASE_DIGEST}" in dockerfile
    assert "--require-hashes" in dockerfile
    assert "--only-binary=:all:" in dockerfile
    assert "ARG SOURCE_REVISION" in dockerfile
    assert "ARG DEPENDENCY_LOCK_DIGEST" in dockerfile
    assert "org.opencontainers.image.revision" in dockerfile
    assert "io.relatorio-ceo.dependency-lock-digest" in dockerfile
    assert re.search(r"^USER\s+(?!root\b)\S+", dockerfile, re.MULTILINE)
    assert not re.search(r"^(CMD|ENTRYPOINT)\s", dockerfile, re.MULTILINE)


def test_docker_context_excludes_local_and_sensitive_files() -> None:
    patterns = set((ROOT / ".dockerignore").read_text().splitlines())
    required = {
        ".env*",
        ".git/",
        ".venv/",
        "__pycache__/",
        "*.log*",
        "*.key",
        "credentials*",
        "tests/",
        "specs/",
    }
    assert required <= patterns
    assert "example.invalid" in (ROOT / ".env.example").read_text()


def test_compose_selects_three_roles_from_one_artifact() -> None:
    compose = (ROOT / "compose.yaml").read_text()

    assert "x-app:" in compose
    assert re.search(r"^\s{2}api:\s*$", compose, re.MULTILINE)
    assert re.search(r"^\s{2}worker-runner:\s*$", compose, re.MULTILINE)
    assert re.search(r"^\s{2}frontend:\s*$", compose, re.MULTILINE)
    assert re.search(r"^\s{2}frontend-react:\s*$", compose, re.MULTILINE)
    assert "python -m uvicorn src.api:app --host 0.0.0.0 --port 8000" in compose
    assert "python -m src.sync_service" not in compose
    assert "python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501" in compose
    assert compose.count("restart: unless-stopped") >= 3

    worker = compose.split("  worker-runner:", 1)[1].split("  frontend-react:", 1)[0]
    assert "ports:" not in worker
    assert "expose:" not in worker
    assert 'command: python -c "from threading import Event; Event().wait()"' in worker


def test_roles_are_independent_and_worker_invocations_are_explicit() -> None:
    compose = (ROOT / "compose.yaml").read_text()

    assert "python -m src.sync_service" not in compose
    assert "schedule:" not in compose
    assert "ports:" not in compose.split("  worker-runner:", 1)[1].split(
        "  frontend-react:", 1
    )[0]
    assert compose.count("restart: unless-stopped") >= 3


def test_feature_adds_no_schema_or_migration_artifacts() -> None:
    excluded = {".git", ".venv", "venv"}
    forbidden = [
        path
        for path in ROOT.rglob("*")
        if not any(part in excluded for part in path.parts)
        and (path.suffix.lower() in {".sql", ".ddl"} or "migrations" in path.parts)
    ]
    assert forbidden == []


@pytest.mark.skipif(not RUN_DOCKER_SMOKE, reason="set RUN_DOCKER_SMOKE=1")
def test_compose_configuration_is_valid() -> None:
    config = run("docker", "compose", "--env-file", ".env.example", "config")
    assert config.returncode == 0, config.stderr
    assert "services:" in config.stdout


@pytest.mark.skipif(not RUN_DOCKER_SMOKE, reason="set RUN_DOCKER_SMOKE=1")
def test_two_clean_builds_have_equivalent_runtime_artifacts(tmp_path: Path) -> None:
    revision = run("git", "rev-parse", "HEAD").stdout.strip()
    lock_digest = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
    tags = ("relatorio-ceo:mvp-a", "relatorio-ceo:mvp-b")

    try:
        for tag in tags:
            build = run(
                "docker",
                "build",
                "--no-cache",
                "--platform",
                "linux/amd64",
                "--build-arg",
                f"SOURCE_REVISION={revision}",
                "--build-arg",
                f"DEPENDENCY_LOCK_DIGEST={lock_digest}",
                "--tag",
                tag,
                ".",
                timeout=900,
            )
            assert build.returncode == 0, build.stderr

        inventories = [
            run("docker", "run", "--rm", tag, "python", "-m", "pip", "freeze", "--all")
            for tag in tags
        ]
        assert all(result.returncode == 0 for result in inventories)
        assert inventories[0].stdout == inventories[1].stdout

        for tag in tags:
            python_version = run(
                "docker", "run", "--rm", tag, "python", "--version"
            )
            assert python_version.returncode == 0
            assert "Python 3.13.14" in python_version.stdout

            user = run("docker", "run", "--rm", tag, "id", "-u")
            assert user.returncode == 0
            assert user.stdout.strip() != "0"

            inspect = run(
                "docker",
                "image",
                "inspect",
                tag,
                "--format",
                "{{json .Config.Labels}}",
            )
            assert revision in inspect.stdout
            assert lock_digest in inspect.stdout

            context = run(
                "docker",
                "run",
                "--rm",
                tag,
                "sh",
                "-c",
                "test ! -e /app/.env && test ! -e /app/.git && "
                "test ! -e /app/.venv && test ! -e /app/tests && "
                "test ! -e /app/specs && "
                "test -z \"$(find /app -type f "
                "\\( -name '*.log' -o -name '*.key' -o -name '*.pem' \\) -print -quit)\" && "
                "test -z \"$(find /app -type d "
                "\\( -name '__pycache__' -o -name '.pytest_cache' \\) -print -quit)\"",
            )
            assert context.returncode == 0, context.stderr

        request_block = re.search(
            r"(?ms)^requests==.*?(?=^[a-zA-Z0-9_.-]+==|\Z)",
            (ROOT / "requirements.txt").read_text(),
        )
        assert request_block
        tampered = re.sub(
            r"sha256:[0-9a-f]{64}",
            "sha256:" + ("0" * 64),
            request_block.group(0),
        )
        tampered_lock = tmp_path / "tampered.txt"
        tampered_lock.parent.mkdir(parents=True, exist_ok=True)
        tampered_lock.write_text(tampered)
        rejected = run(
            "docker",
            "run",
            "--rm",
            "--mount",
            f"type=bind,source={tampered_lock.parent.resolve()},target=/input,readonly",
            f"python:3.13.14-slim@{BASE_DIGEST}",
            "python",
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--require-hashes",
            "-r",
            "/input/tampered.txt",
            timeout=300,
        )
        assert rejected.returncode != 0
        assert "HASHES" in (rejected.stdout + rejected.stderr).upper()
    finally:
        if shutil.which("docker"):
            run("docker", "image", "rm", "--force", *tags, timeout=120)


@pytest.mark.skipif(not RUN_DOCKER_SMOKE, reason="set RUN_DOCKER_SMOKE=1")
def test_each_role_starts_or_fails_explicitly_within_thirty_seconds() -> None:
    image = "relatorio-ceo:mvp-role-check"
    revision = run("git", "rev-parse", "HEAD").stdout.strip()
    lock_digest = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
    build = run(
        "docker",
        "build",
        "--platform",
        "linux/amd64",
        "--build-arg",
        f"SOURCE_REVISION={revision}",
        "--build-arg",
        f"DEPENDENCY_LOCK_DIGEST={lock_digest}",
        "--tag",
        image,
        ".",
        timeout=900,
    )
    assert build.returncode == 0, build.stderr

    containers: list[str] = []
    try:
        role_commands = {
            "api": [
                "python",
                "-m",
                "uvicorn",
                "src.api:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
            "worker": ["python", "-c", "from threading import Event; Event().wait()"],
            "frontend": [
                "python",
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.address=0.0.0.0",
                "--server.port=8501",
            ],
        }
        for role, command in role_commands.items():
            name = f"relatorio-ceo-mvp-{role}"
            containers.append(name)
            run("docker", "rm", "--force", name)
            started = run("docker", "run", "--detach", "--name", name, image, *command)
            assert started.returncode == 0, started.stderr

        time.sleep(5)
        for name in containers:
            status = run("docker", "inspect", "--format", "{{.State.Status}}", name)
            assert status.returncode == 0
            assert status.stdout.strip() == "running"
    finally:
        for name in containers:
            run("docker", "rm", "--force", name)
        run("docker", "image", "rm", "--force", image)
