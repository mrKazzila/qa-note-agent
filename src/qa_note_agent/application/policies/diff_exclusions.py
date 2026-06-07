from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiffExcludeRule:
    pattern: str
    reason: str


DEFAULT_DIFF_EXCLUDE_RULES: tuple[DiffExcludeRule, ...] = (
    # Python
    DiffExcludeRule("uv.lock", "python_lockfile"),
    DiffExcludeRule("poetry.lock", "python_lockfile"),
    DiffExcludeRule("Pipfile.lock", "python_lockfile"),
    DiffExcludeRule("pdm.lock", "python_lockfile"),

    # JavaScript / TypeScript / Node
    DiffExcludeRule("package-lock.json", "node_lockfile"),
    DiffExcludeRule("npm-shrinkwrap.json", "node_lockfile"),
    DiffExcludeRule("yarn.lock", "node_lockfile"),
    DiffExcludeRule("pnpm-lock.yaml", "node_lockfile"),
    DiffExcludeRule("bun.lock", "node_lockfile"),
    DiffExcludeRule("bun.lockb", "node_lockfile"),
    DiffExcludeRule("deno.lock", "deno_lockfile"),

    # Rust
    DiffExcludeRule("Cargo.lock", "rust_lockfile"),

    # Go
    DiffExcludeRule("go.sum", "go_checksum_file"),

    # Java / Kotlin / Gradle / Maven
    DiffExcludeRule("gradle.lockfile", "gradle_lockfile"),
    DiffExcludeRule("dependencies.lock", "dependency_lockfile"),

    # PHP
    DiffExcludeRule("composer.lock", "php_lockfile"),

    # Ruby
    DiffExcludeRule("Gemfile.lock", "ruby_lockfile"),

    # .NET
    DiffExcludeRule("packages.lock.json", "dotnet_lockfile"),
    DiffExcludeRule("project.assets.json", "dotnet_generated_assets"),

    # Swift
    DiffExcludeRule("Package.resolved", "swift_lockfile"),

    # Dart / Flutter
    DiffExcludeRule("pubspec.lock", "dart_lockfile"),

    # Elixir / Erlang
    DiffExcludeRule("mix.lock", "elixir_lockfile"),
    DiffExcludeRule("rebar.lock", "erlang_lockfile"),

    # R / Nix / Terraform
    DiffExcludeRule("renv.lock", "r_lockfile"),
    DiffExcludeRule("flake.lock", "nix_lockfile"),
    DiffExcludeRule(".terraform.lock.hcl", "terraform_lockfile"),

    # Generated files
    DiffExcludeRule("*.generated.*", "generated_file"),
    DiffExcludeRule("*.gen.*", "generated_file"),
    DiffExcludeRule("*.pb.*", "protobuf_generated_file"),
    DiffExcludeRule("*_pb2.py", "python_protobuf_generated_file"),
    DiffExcludeRule("*_pb2_grpc.py", "python_grpc_generated_file"),
    DiffExcludeRule("**/generated/**", "generated_directory"),
    DiffExcludeRule("**/gen/**", "generated_directory"),
    DiffExcludeRule("**/__generated__/**", "generated_directory"),

    # Vendored / build directories
    DiffExcludeRule("vendor/**", "vendored_dependency"),
    DiffExcludeRule("**/vendor/**", "vendored_dependency"),
    DiffExcludeRule("node_modules/**", "vendored_dependency"),
    DiffExcludeRule("**/node_modules/**", "vendored_dependency"),
    DiffExcludeRule(".venv/**", "virtualenv"),
    DiffExcludeRule("venv/**", "virtualenv"),
    DiffExcludeRule("dist/**", "build_artifact"),
    DiffExcludeRule("build/**", "build_artifact"),
    DiffExcludeRule("out/**", "build_artifact"),
    DiffExcludeRule(".next/**", "frontend_build_artifact"),

    # Snapshots / reports
    DiffExcludeRule("**/__snapshots__/**", "test_snapshot"),
    DiffExcludeRule("*.snap", "test_snapshot"),
    DiffExcludeRule("coverage/**", "coverage_artifact"),
    DiffExcludeRule("**/coverage/**", "coverage_artifact"),
    DiffExcludeRule("htmlcov/**", "coverage_artifact"),
    DiffExcludeRule("playwright-report/**", "test_report"),

    # Binary / media / archives
    DiffExcludeRule("*.png", "binary_or_media_file"),
    DiffExcludeRule("*.jpg", "binary_or_media_file"),
    DiffExcludeRule("*.jpeg", "binary_or_media_file"),
    DiffExcludeRule("*.gif", "binary_or_media_file"),
    DiffExcludeRule("*.webp", "binary_or_media_file"),
    DiffExcludeRule("*.ico", "binary_or_media_file"),
    DiffExcludeRule("*.pdf", "binary_or_document_file"),
    DiffExcludeRule("*.zip", "archive_file"),
    DiffExcludeRule("*.tar", "archive_file"),
    DiffExcludeRule("*.gz", "archive_file"),
    DiffExcludeRule("*.tgz", "archive_file"),
)


DEFAULT_DIFF_EXCLUDE_PATTERNS: tuple[str, ...] = tuple(
    rule.pattern for rule in DEFAULT_DIFF_EXCLUDE_RULES
)
