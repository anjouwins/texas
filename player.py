from typing import List

from card import Card


class Player:
    """玩家基类"""

    def __init__(self, name: str, chips: int = 1000):
        """
        初始化玩家

        Args:
            name: 玩家名称
            chips: 初始筹码数量
        """
        self.name = name
        self.chips = chips
        self.hand = []
        #当前已下注额度
        self.current_bet = 0
        #是否弃牌
        self.folded = False
        #是否allin
        self.all_in = False

    def reset_hand(self):
        """重置玩家手牌状态，开始新的一轮"""
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False

    def bet(self, amount: int) -> int:
        """
        玩家下注

        Args:
            amount: 下注金额

        Returns:
            实际下注金额（可能少于请求金额，如果筹码不足）
        """
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.current_bet += actual_bet

        # 如果下注后没有筹码了，标记为全下
        if self.chips == 0:
            self.all_in = True

        return actual_bet

    def receive_cards(self, cards: List[Card]):
        """
        接收发牌

        Args:
            cards: 发给玩家的牌
        """
        self.hand.extend(cards)

    def is_active(self) -> bool:
        """
        检查玩家是否仍在游戏中（未弃牌且未全下）

        Returns:
            如果玩家仍在游戏中返回True，否则返回False
        """
        return not self.folded and not self.all_in

    def __repr__(self):
        """返回玩家的字符串表示"""
        return f"{self.name} (${self.chips})"