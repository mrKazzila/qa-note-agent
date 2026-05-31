from qa_note_agent.config.settings.logger import setup_logging, LoggingConfig


def app() -> None:
    print("Hello world")


if __name__ == "__main__":
    setup_logging(
        config=LoggingConfig(
            level="INFO",
            renderer="console",
            enable_diagnostics=False,
            use_utc_timestamps=True,
        ),
    )
    app()
