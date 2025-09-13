import os
from pathlib import Path

_location = os.path.dirname(__file__)


def template_path():
    return os.path.join(Path(_location).parent, 'templates')
