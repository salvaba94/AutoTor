from .autotor_base import TorRequests
from .autotor_ip import TorIP


"""
Define what is going to be imported as public with "from autotor import *"
"""
__all__ = ["TorRequests", "TorIP"]
