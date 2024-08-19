"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api library.
License           : GPL3
"""

import sys


def run_shell():
    from .api import api
    from .servers import ApiServer

    sys.path.extend(
        [
            "/usr/share/vixen/root_utils",
            "/usr/share/vixen/features",
        ],
    )

    ApiServer.start(api)
