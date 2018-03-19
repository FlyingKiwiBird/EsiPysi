try:
    from .esipysi import EsiPysi
    from .op import EsiOp
    from .auth import EsiAuth

except ImportError:

    pass

__version__ = '0.3.1'
__name__ = 'EsiPysi'

import logging