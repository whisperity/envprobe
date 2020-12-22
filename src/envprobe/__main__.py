"""
The entry point if Envprobe is run as `python(3?) -m envprobe`.
"""
import os
import sys

from .main import handle_mode

if __name__ == '__main__':
    abs_path = os.path.dirname(os.path.abspath(__file__))  # .../src/envprobe
    ret = handle_mode(os.path.dirname(abs_path))  # .../src
    sys.exit(ret)
