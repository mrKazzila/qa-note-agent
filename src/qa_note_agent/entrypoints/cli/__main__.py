from qa_note_agent.config.settings.logger import setup_logging, LoggingConfig

from qa_note_agent.presentation.cli.app import create_app


def main() -> None:
    """Run CLI application."""
    app = create_app()
    app()


if __name__ == "__main__":
    setup_logging(
        config=LoggingConfig(
            level="INFO",
            renderer="console",
            enable_diagnostics=False,
            use_utc_timestamps=True,
        ),
    )
    main()
