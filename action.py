from enum import Enum


class Action(Enum):
    """玩家行动枚举"""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"
