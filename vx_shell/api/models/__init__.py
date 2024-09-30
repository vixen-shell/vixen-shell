"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : vixen shell api globals library.
License           : GPL3
"""

from .ModelResponses import ModelResponses


class Models:
    class Commons:
        from .models import Commons_Error as Error

    class Features:
        from .models import Features_Base as Base
        from .models import Features_Names as Names
        from .models import Features_State as State
        from .models import Features_LogListener as LogListener

    class Frames:
        from .models import Frames_Base as Base
        from .models import Frames_Ids as Ids
        from .models import Frames_Properties as Properties

    class Log:
        from .models import Log_Log as Log
        from .models import Log_Logs as Logs

    class Os:
        from .models import Os_ExecInfo as ExecInfo
