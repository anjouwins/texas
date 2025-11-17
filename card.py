from rank import Rank
from suit import Suit


class Card:
    """扑克牌类"""

    def __init__(self, rank: Rank, suit: Suit):
        """
        初始化扑克牌

        Args:
            rank: 牌的点数
            suit: 牌的花色
        """
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        """返回牌的字符串表示,展示数值或者JQKA简写"""
        if  self.rank.value <= 10:
            rank_str = str(self.rank.value)
        else:
            rank_str = self.rank.name[0]
        return f"{rank_str}{self.suit.value}"
    def __eq__(self, other):
        """判断两张牌是否相等"""
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        """返回牌的哈希值，用于在集合和字典中使用"""
        return hash((self.rank, self.suit))