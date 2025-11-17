import random

from card import Card
from rank import Rank
from suit import Suit


class Deck:
    """牌堆类，负责管理一副扑克牌"""

    def __init__(self):
        """初始化一副完整的52张扑克牌"""
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)

    def deal(self) -> Card:
        """
        从牌堆顶部发一张牌

        Returns:
            发出的牌，如果牌堆为空则返回None
        """
        return self.cards.pop() if self.cards else None

    def __len__(self):
        """返回牌堆中剩余的牌数"""
        return len(self.cards)
