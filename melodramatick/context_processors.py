from melodramatick.version import __version__


def melodramatick_version(request):
    return {
        "MELODRAMATICK_VERSION": __version__,
    }
