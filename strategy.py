from action import Action
from typing import Dict, Any, Tuple, List

from card import Card
from player import Player


class PokerStrategy:
    """扑克策略基类，所有AI策略都应继承此类"""

    def decide(self, player: Player, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        做出决策的抽象方法，子类必须实现

        Args:
            player: 做出决策的玩家
            game_state: 当前游戏状态

        Returns:
            (行动, 金额) 元组
        """
        raise NotImplementedError("Subclasses must implement this method")

    def _calculate_hand_strength(self, hand: List[Card], community_cards: List[Card]) -> float:
        """
        计算手牌强度 (0-1之间的值)

        Args:
            hand: 玩家的手牌
            community_cards: 公共牌

        Returns:
            手牌强度估计值，0表示最弱，1表示最强
        """
        if len(hand) < 2:
            return 0.0

        # 简单的手牌强度评估
        card1, card2 = hand

        # 对子
        if card1.rank == card2.rank:
            base_strength = 0.8
        # 同花
        elif card1.suit == card2.suit:
            base_strength = 0.3
        # 连牌
        elif abs(card1.rank.value - card2.rank.value) == 1:
            base_strength = 0.2
        else:
            base_strength = 0.1

        # 高牌加成
        high_card_bonus = max(card1.rank.value, card2.rank.value) / 100

        return min(1.0, base_strength + high_card_bonus)

class BasicStrategy(PokerStrategy):
    """基础AI策略"""

    def decide(self, player: Player, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        使用基础策略做出决策

        Args:
            player: 做出决策的玩家
            game_state: 当前游戏状态

        Returns:
            (行动, 金额) 元组
        """
        hand_strength = self._calculate_hand_strength(player.hand, game_state['community_cards'])

        # 获取当前下注信息
        current_bet = game_state['current_bet']
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']

        # 如果已经有人下注
        if current_bet > player.current_bet:
            call_amount = current_bet - player.current_bet

            # 手牌很强时加注
            if hand_strength > 0.7 and player.chips > call_amount + min_raise:
                raise_amount = min(int(pot_size * 0.5), player.chips)
                return Action.RAISE, max(min_raise, raise_amount)

            # 手牌中等时跟注
            elif hand_strength > 0.3 and player.chips >= call_amount:
                return Action.CALL, call_amount

            # 手牌很弱时弃牌
            else:
                return Action.FOLD, 0

        # 如果没有人下注或只是跟注
        else:
            # 手牌很强时下注
            if hand_strength > 0.6:
                bet_amount = min(int(pot_size * 0.3), player.chips)
                return Action.RAISE, max(min_raise, bet_amount)

            # 手牌中等时过牌
            elif hand_strength > 0.2:
                return Action.CHECK, 0

            # 手牌很弱时过牌
            else:
                return Action.CHECK, 0


class AggressiveStrategy(PokerStrategy):
    """激进策略"""

    def decide(self, player: Player, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        使用激进策略做出决策

        Args:
            player: 做出决策的玩家
            game_state: 当前游戏状态

        Returns:
            (行动, 金额) 元组
        """
        hand_strength = self._calculate_hand_strength(player.hand, game_state['community_cards'])

        current_bet = game_state['current_bet']
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']

        if current_bet > player.current_bet:
            call_amount = current_bet - player.current_bet

            # 更激进的加注条件
            if hand_strength > 0.5 and player.chips > call_amount + min_raise:
                raise_amount = min(int(pot_size * 0.75), player.chips)
                return Action.RAISE, max(min_raise, raise_amount)

            elif hand_strength > 0.2 and player.chips >= call_amount:
                return Action.CALL, call_amount

            else:
                return Action.FOLD, 0

        else:
            # 更激进的加注条件
            if hand_strength > 0.4:
                bet_amount = min(int(pot_size * 0.5), player.chips)
                return Action.RAISE, max(min_raise, bet_amount)

            else:
                return Action.CHECK, 0


class ConservativeStrategy(PokerStrategy):
    """保守策略"""

    def decide(self, player: Player, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        使用保守策略做出决策

        Args:
            player: 做出决策的玩家
            game_state: 当前游戏状态

        Returns:
            (行动, 金额) 元组
        """
        hand_strength = self._calculate_hand_strength(player.hand, game_state['community_cards'])

        current_bet = game_state['current_bet']
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']

        if current_bet > player.current_bet:
            call_amount = current_bet - player.current_bet

            # 更保守的跟注条件
            if hand_strength > 0.6 and player.chips > call_amount + min_raise:
                raise_amount = min(int(pot_size * 0.3), player.chips)
                return Action.RAISE, max(min_raise, raise_amount)

            elif hand_strength > 0.4 and player.chips >= call_amount:
                return Action.CALL, call_amount

            else:
                return Action.FOLD, 0

        else:
            # 更保守的加注条件
            if hand_strength > 0.7:
                bet_amount = min(int(pot_size * 0.2), player.chips)
                return Action.RAISE, max(min_raise, bet_amount)

            else:
                return Action.CHECK, 0