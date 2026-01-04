from typing import Dict, Any, Tuple

from action import Action
from player import Player
from strategy import BasicStrategy


class AIPlayer(Player):
    """AI玩家类，使用策略进行决策"""

    def __init__(self, name: str, chips: int = 1000, strategy=None):
        """
        初始化AI玩家

        Args:
            name: 玩家名称
            chips: 初始筹码数量
            strategy: AI策略对象，如果为None则使用基础策略
        """
        super().__init__(name, chips)
        self.strategy = strategy or BasicStrategy()

    def make_decision(self, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        AI玩家做出决策

        Args:
            game_state: 当前游戏状态信息

        Returns:
            (行动, 金额) 元组
        """
        return self.strategy.decide(self, game_state)