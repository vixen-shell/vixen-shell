"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell library.
License           : GPL3
"""

from .errorHandling import ErrorHandling

ErrorHandling.init("vx_library")

from .manager import Manager
