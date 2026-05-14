from importlib.metadata import PackageNotFoundError, version


def melodramatick_version(request):
    try:
        package_version = "v" + version("melodramatick")
    except PackageNotFoundError:
        package_version = "development"
    return {
        "MELODRAMATICK_VERSION": package_version
    }
