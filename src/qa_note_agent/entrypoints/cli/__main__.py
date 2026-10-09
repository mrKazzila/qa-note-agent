from qa_note_agent.config.settings import create_settings
from qa_note_agent.entrypoints.cli.bootstrap import create_application
from qa_note_agent.presentation.cli.error_handling import handle_errors


def main() -> None:
    """Run CLI application."""
    settings = create_settings()
    app = create_application(settings=settings)

    with handle_errors(debug=settings.debug):
        app(standalone_mode=False)


if __name__ == "__main__":
    main()
