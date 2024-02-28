from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = (
        "Creates a Django app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        app_name = options.pop("name")
        target = options.pop("directory")
        options["template"] = "app_template"
        super().handle("app", app_name, target, **options)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--work",
            help="Name of core work model for app.",
        )
        parser.add_argument(
            "--colour-hex",
            help="Colour theme for app. e.g. '#ecdff2'"
        )
