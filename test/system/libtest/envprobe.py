import os


def envprobe_location():
    """The location where Envprobe is "installed" to."""
    return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../.."))
