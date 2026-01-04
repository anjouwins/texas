import random
import math
import numpy as np
from typing import List, Tuple, Dict, Any, Set
from collections import defaultdict

from action import Action
from card import Card
from handEvaluator import HandEvaluator
from player import Player
from strategy import PokerStrategy


class GTOStrategy(PokerStrategy):
    """GTO (Game Theory Optimal) 策略实现"""

    def __init__(self, complexity: int = 2):
        """
        初始化GTO策略

        Args:
            complexity: 策略复杂度 (1-简单, 2-中等, 3-复杂)
        """
        self.complexity = complexity
        self.hand_ranges = self._initialize_hand_ranges()
        self.position_weights = self._initialize_position_weights()
        self.range_charts = self._initialize_range_charts()

    def decide(self, player: Player, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        使用GTO策略做出决策

        Args:
            player: 做出决策的玩家
            game_state: 当前游戏状态

        Returns:
            (行动, 金额) 元组
        """
        # 获取游戏阶段
        game_stage = self._get_game_stage(game_state['community_cards'])

        # 计算手牌强度
        hand_strength = self._calculate_gto_hand_strength(player.hand, game_state['community_cards'], game_stage)

        # 计算范围优势
        range_advantage = self._calculate_range_advantage(player.hand, game_stage)

        # 计算位置优势
        position_advantage = self._calculate_position_advantage(player, game_state)

        # 计算底池赔率
        pot_odds = self._calculate_pot_odds(player, game_state)

        # 计算隐含赔率
        implied_odds = self._calculate_implied_odds(player, game_state, game_stage)

        # 使用GTO混合策略决定行动
        action, amount = self._gto_mixed_strategy(
            player, game_state, hand_strength, range_advantage,
            position_advantage, pot_odds, implied_odds, game_stage
        )

        return action, amount

    def _initialize_hand_ranges(self) -> Dict[str, Set[Tuple[int, int, bool]]]:
        """初始化手牌范围表"""
        ranges = {
            # 翻牌前范围
            "UTG": set(), "MP": set(), "CO": set(), "BTN": set(), "SB": set(), "BB": set(),
            # 翻牌后范围
            "value_hands": set(), "bluff_hands": set(), "medium_hands": set()
        }

        # 生成所有可能的手牌组合 (rank1, rank2, suited)
        ranks = list(range(2, 15))  # 2到A
        for r1 in ranks:
            for r2 in ranks:
                if r1 >= r2:  # 避免重复
                    suited = True
                    ranges["UTG"].add((r1, r2, suited))
                    ranges["MP"].add((r1, r2, suited))
                    ranges["CO"].add((r1, r2, suited))
                    ranges["BTN"].add((r1, r2, suited))
                    ranges["SB"].add((r1, r2, suited))
                    ranges["BB"].add((r1, r2, suited))

                    # 非同花版本
                    suited = False
                    ranges["UTG"].add((r1, r2, suited))
                    ranges["MP"].add((r1, r2, suited))
                    ranges["CO"].add((r1, r2, suited))
                    ranges["BTN"].add((r1, r2, suited))
                    ranges["SB"].add((r1, r2, suited))
                    ranges["BB"].add((r1, r2, suited))

        return ranges

    def _initialize_position_weights(self) -> Dict[str, float]:
        """初始化位置权重"""
        return {
            "BTN": 1.2,  # 按钮位 - 最强位置
            "CO": 1.1,  # cutoff位
            "MP": 1.0,  # 中间位置
            "UTG": 0.9,  # 枪口位
            "SB": 0.8,  # 小盲位
            "BB": 0.7  # 大盲位
        }

    def _initialize_range_charts(self) -> Dict[str, Dict[str, List[Tuple[int, int, bool]]]]:
        """初始化GTO范围图表"""
        charts = {
            "preflop": {
                "UTG": [], "MP": [], "CO": [], "BTN": [], "SB": [], "BB": []
            },
            "flop": {
                "value_bet": [], "check_raise": [], "bluff": [], "check_call": [], "check_fold": []
            },
            "turn": {
                "value_bet": [], "check_raise": [], "bluff": [], "check_call": [], "check_fold": []
            },
            "river": {
                "value_bet": [], "check_raise": [], "bluff": [], "check_call": [], "check_fold": []
            }
        }

        # 这里应该填充实际的范围数据
        # 由于数据量很大，这里只做示例填充
        # 实际应用中应该从文件或数据库加载完整的GTO范围

        return charts

    def _get_game_stage(self, community_cards: List[Card]) -> str:
        """获取游戏阶段"""
        if len(community_cards) == 0:
            return "preflop"
        elif len(community_cards) == 3:
            return "flop"
        elif len(community_cards) == 4:
            return "turn"
        else:
            return "river"

    def _calculate_gto_hand_strength(self, hand: List[Card], community_cards: List[Card], stage: str) -> float:
        """
        计算GTO手牌强度

        Args:
            hand: 玩家手牌
            community_cards: 公共牌
            stage: 游戏阶段

        Returns:
            手牌强度 (0-1)
        """
        if len(hand) < 2:
            return 0.0

        # 基础手牌强度
        base_strength = self._calculate_raw_hand_strength(hand, community_cards)

        # 根据阶段调整
        stage_multiplier = {
            "preflop": 1.0,
            "flop": 1.2,
            "turn": 1.5,
            "river": 2.0
        }

        # 考虑手牌可玩性
        playability = self._calculate_hand_playability(hand, community_cards, stage)

        # 考虑阻断牌效应
        blocker_effect = self._calculate_blocker_effect(hand, stage)

        # 综合强度
        strength = base_strength * stage_multiplier[stage] * playability * blocker_effect

        return min(1.0, max(0.0, strength))

    def _calculate_raw_hand_strength(self, hand: List[Card], community_cards: List[Card]) -> float:
        """计算原始手牌强度"""
        if len(hand) < 2:
            return 0.0

        card1, card2 = hand

        # 对子
        if card1.rank == card2.rank:
            pair_strength = card1.rank.value / 14.0  # 对子越大越强
            return 0.6 + 0.4 * pair_strength

        # 同花
        suited = card1.suit == card2.suit

        # 连牌
        gap = abs(card1.rank.value - card2.rank.value)
        connected = gap <= 2

        # 高牌
        high_card = max(card1.rank.value, card2.rank.value) / 14.0

        base = 0.1

        # 同花加成
        if suited:
            base += 0.15

        # 连牌加成
        if connected:
            if gap == 0:  # 对子已处理
                pass
            elif gap == 1:
                base += 0.2
            elif gap == 2:
                base += 0.1

        # 高牌加成
        base += high_card * 0.3

        # 考虑公共牌
        if community_cards:
            all_cards = hand + community_cards
            hand_rank, kickers = HandEvaluator.evaluate_hand(all_cards)
            made_hand_strength = hand_rank / 9.0  # 0-1范围
            base = max(base, made_hand_strength * 0.7 + base * 0.3)

        return base

    def _calculate_hand_playability(self, hand: List[Card], community_cards: List[Card], stage: str) -> float:
        """计算手牌可玩性"""
        if len(hand) < 2:
            return 0.5

        card1, card2 = hand

        # 同花潜力
        suited = card1.suit == card2.suit
        flush_potential = 1.0 if suited else 0.6

        # 顺子潜力
        gap = abs(card1.rank.value - card2.rank.value)
        if gap <= 3:
            straight_potential = 1.0 - (gap * 0.2)
        else:
            straight_potential = 0.3

        # 根据阶段调整
        if stage == "preflop":
            return (flush_potential + straight_potential) / 2
        else:
            # 在翻牌后，考虑实际的听牌
            draw_potential = self._calculate_draw_potential(hand, community_cards)
            return (flush_potential + straight_potential + draw_potential) / 3

    def _calculate_draw_potential(self, hand: List[Card], community_cards: List[Card]) -> float:
        """计算听牌潜力"""
        if len(community_cards) < 3:
            return 0.5

        all_cards = hand + community_cards

        # 检查同花听牌
        suit_count = {}
        for card in all_cards:
            suit_count[card.suit] = suit_count.get(card.suit, 0) + 1

        flush_draw = max(suit_count.values()) == 4  # 需要一张成花

        # 检查顺子听牌
        ranks = sorted(set(card.rank.value for card in all_cards))
        straight_draw = False

        for i in range(len(ranks) - 3):
            if ranks[i + 3] - ranks[i] <= 4:
                straight_draw = True
                break

        # 检查两头顺听牌
        open_ended = False
        for i in range(len(ranks) - 4):
            if ranks[i + 4] - ranks[i] == 4:
                open_ended = True
                break

        if flush_draw and open_ended:
            return 0.9
        elif flush_draw or open_ended:
            return 0.7
        elif straight_draw:
            return 0.5
        else:
            return 0.3

    def _calculate_blocker_effect(self, hand: List[Card], stage: str) -> float:
        """计算阻断牌效应"""
        if len(hand) < 2:
            return 1.0

        card1, card2 = hand

        # 高牌阻断效应 - 持有高牌会减少对手持有强牌的概率
        blocker_value = 0.0

        # A和K是强的阻断牌
        if card1.rank.value >= 13 or card2.rank.value >= 13:  # K或A
            blocker_value += 0.2

        # 对子有额外的阻断效应
        if card1.rank == card2.rank:
            blocker_value += 0.1

        # 同花阻断
        if card1.suit == card2.suit:
            blocker_value += 0.05

        return 1.0 + blocker_value

    def _calculate_range_advantage(self, hand: List[Card], stage: str) -> float:
        """计算范围优势"""
        if len(hand) < 2:
            return 0.5

        card1, card2 = hand

        # 基于手牌在GTO范围中的位置计算范围优势
        hand_score = (card1.rank.value + card2.rank.value) / 2.0

        # 对子加成
        if card1.rank == card2.rank:
            hand_score += 5

        # 同花加成
        if card1.suit == card2.suit:
            hand_score += 2

        # 连牌加成
        gap = abs(card1.rank.value - card2.rank.value)
        if gap <= 2:
            hand_score += (3 - gap)

        # 归一化到0-1范围
        max_score = 20  # 最大可能得分 (A+A同花 = 14+14+5+2 = 35，但实际最大约20)
        advantage = min(1.0, hand_score / max_score)

        return advantage

    def _calculate_position_advantage(self, player: Player, game_state: Dict[str, Any]) -> float:
        """计算位置优势"""
        # 简化实现 - 实际应该基于确切的位置计算
        # 这里我们假设玩家在列表中的位置反映了实际位置

        players = [p for p in game_state.get('players', []) if not p.folded]
        if player not in players:
            return 0.5

        player_index = players.index(player)
        total_players = len(players)

        # 位置越好，优势越大 (按钮位最好)
        position_advantage = (total_players - player_index) / total_players

        return position_advantage

    def _calculate_pot_odds(self, player: Player, game_state: Dict[str, Any]) -> float:
        """计算底池赔率"""
        current_bet = game_state['current_bet']
        player_current_bet = player.current_bet
        call_amount = current_bet - player_current_bet

        if call_amount <= 0:
            return float('inf')  # 无需跟注时赔率无限大

        pot_size = game_state['pot']
        pot_odds = call_amount / (pot_size + call_amount)

        return pot_odds

    def _calculate_implied_odds(self, player: Player, game_state: Dict[str, Any], stage: str) -> float:
        """计算隐含赔率"""
        # 隐含赔率考虑未来可能赢得的额外筹码
        base_pot_odds = self._calculate_pot_odds(player, game_state)

        # 根据阶段调整隐含赔率
        stage_multiplier = {
            "preflop": 3.0,  # 翻牌前隐含赔率最高
            "flop": 2.0,  # 翻牌圈
            "turn": 1.5,  # 转牌圈
            "river": 1.0  # 河牌圈没有隐含赔率
        }

        implied_odds = base_pot_odds * stage_multiplier[stage]

        # 考虑手牌的可玩性
        hand_playability = self._calculate_hand_playability(player.hand, game_state['community_cards'], stage)
        implied_odds *= (0.5 + hand_playability * 0.5)

        return implied_odds

    def _gto_mixed_strategy(self, player: Player, game_state: Dict[str, Any],
                            hand_strength: float, range_advantage: float,
                            position_advantage: float, pot_odds: float,
                            implied_odds: float, stage: str) -> Tuple[Action, int]:
        """
        GTO混合策略决策

        Args:
            player: 玩家对象
            game_state: 游戏状态
            hand_strength: 手牌强度
            range_advantage: 范围优势
            position_advantage: 位置优势
            pot_odds: 底池赔率
            implied_odds: 隐含赔率
            stage: 游戏阶段

        Returns:
            (行动, 金额) 元组
        """
        current_bet = game_state['current_bet']
        player_current_bet = player.current_bet
        call_amount = current_bet - player_current_bet
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']

        # 计算综合决策分数
        decision_score = self._calculate_decision_score(
            hand_strength, range_advantage, position_advantage,
            pot_odds, implied_odds, stage
        )

        # 根据游戏阶段和情况使用不同的混合策略
        if stage == "preflop":
            return self._preflop_strategy(player, game_state, decision_score, call_amount, min_raise)
        else:
            return self._postflop_strategy(player, game_state, decision_score, call_amount, min_raise, stage)

    def _calculate_decision_score(self, hand_strength: float, range_advantage: float,
                                  position_advantage: float, pot_odds: float,
                                  implied_odds: float, stage: str) -> float:
        """计算综合决策分数"""
        # 权重分配
        weights = {
            "preflop": [0.3, 0.3, 0.2, 0.1, 0.1],  # 手牌强度, 范围优势, 位置, 底池赔率, 隐含赔率
            "flop": [0.4, 0.2, 0.2, 0.1, 0.1],
            "turn": [0.5, 0.2, 0.1, 0.1, 0.1],
            "river": [0.6, 0.2, 0.1, 0.1, 0.0]  # 河牌圈没有隐含赔率
        }

        w = weights[stage]

        # 归一化赔率 (赔率越低越好)
        normalized_pot_odds = 1.0 - min(1.0, pot_odds * 5)  # 假设最大赔率为0.2
        normalized_implied_odds = 1.0 - min(1.0, implied_odds * 3)  # 假设最大隐含赔率为0.33

        # 计算加权分数
        score = (hand_strength * w[0] +
                 range_advantage * w[1] +
                 position_advantage * w[2] +
                 normalized_pot_odds * w[3] +
                 normalized_implied_odds * w[4])

        return score

    def _preflop_strategy(self, player: Player, game_state: Dict[str, Any],
                          decision_score: float, call_amount: int, min_raise: int) -> Tuple[Action, int]:
        """翻牌前策略"""
        # 基于GTO的翻牌前范围策略

        if call_amount > 0:
            # 有人下注，需要决定是否跟注、加注或弃牌
            if decision_score > 0.7:
                # 强牌，加注
                raise_amount = self._calculate_raise_amount(player, game_state, decision_score, min_raise)
                return Action.RAISE, raise_amount
            elif decision_score > 0.4:
                # 中等牌力，跟注
                if call_amount <= player.chips:
                    return Action.CALL, call_amount
                else:
                    return Action.ALL_IN, player.chips
            else:
                # 弱牌，弃牌
                return Action.FOLD, 0
        else:
            # 无人下注，可以过牌或下注
            if decision_score > 0.6:
                # 强牌，下注
                bet_amount = self._calculate_bet_amount(player, game_state, decision_score, min_raise)
                return Action.RAISE, bet_amount
            else:
                # 中等或弱牌，过牌
                return Action.CHECK, 0

    def _postflop_strategy(self, player: Player, game_state: Dict[str, Any],
                           decision_score: float, call_amount: int,
                           min_raise: int, stage: str) -> Tuple[Action, int]:
        """翻牌后策略"""
        # 基于GTO的翻牌后策略，考虑范围、阻断牌和混合策略

        # 计算合适的下注尺度
        bet_sizing = self._calculate_bet_sizing(player, game_state, decision_score, stage)

        if call_amount > 0:
            # 有人下注
            if decision_score > 0.8:
                # 超强牌，加注
                raise_amount = self._calculate_raise_amount(player, game_state, decision_score, min_raise)
                # 使用混合策略，有时只是跟注来平衡范围
                if random.random() < 0.3:  # 30%概率只是跟注
                    if call_amount <= player.chips:
                        return Action.CALL, call_amount
                    else:
                        return Action.ALL_IN, player.chips
                else:
                    return Action.RAISE, raise_amount
            elif decision_score > 0.5:
                # 中等牌力，跟注
                if call_amount <= player.chips:
                    return Action.CALL, call_amount
                else:
                    return Action.ALL_IN, player.chips
            else:
                # 弱牌，弃牌
                # 但使用混合策略，有时会用听牌跟注
                hand_playability = self._calculate_hand_playability(
                    player.hand, game_state['community_cards'], stage
                )

                if hand_playability > 0.7 and random.random() < 0.2:  # 20%概率用听牌跟注
                    if call_amount <= player.chips:
                        return Action.CALL, call_amount
                    else:
                        return Action.ALL_IN, player.chips
                else:
                    return Action.FOLD, 0
        else:
            # 无人下注
            if decision_score > 0.7:
                # 强牌，下注
                bet_amount = self._calculate_bet_amount(player, game_state, decision_score, min_raise)
                # 使用混合策略，有时会过牌来平衡范围
                if random.random() < 0.2:  # 20%概率过牌
                    return Action.CHECK, 0
                else:
                    return Action.RAISE, bet_amount
            elif decision_score > 0.4:
                # 中等牌力，过牌
                return Action.CHECK, 0
            else:
                # 弱牌，过牌
                # 但使用混合策略，有时会诈唬
                if random.random() < 0.1:  # 10%概率诈唬
                    bet_amount = self._calculate_bluff_bet(player, game_state, min_raise)
                    return Action.RAISE, bet_amount
                else:
                    return Action.CHECK, 0

    def _calculate_bet_sizing(self, player: Player, game_state: Dict[str, Any],
                              decision_score: float, stage: str) -> Dict[str, float]:
        """计算下注尺度"""
        # GTO使用多种下注尺度来平衡策略
        pot_size = game_state['pot']

        # 不同情况下的下注尺度
        sizes = {
            "small": 0.33,  # 1/3底池
            "medium": 0.66,  # 2/3底池
            "large": 1.0,  # 满池
            "over": 1.5  # 超池
        }

        # 根据手牌强度和阶段选择下注尺度
        if decision_score > 0.8:
            # 超强牌，使用混合尺度
            if random.random() < 0.6:  # 60%概率使用中等尺度
                return {"size": sizes["medium"], "frequency": 0.6}
            elif random.random() < 0.8:  # 20%概率使用小尺度
                return {"size": sizes["small"], "frequency": 0.2}
            else:  # 20%概率使用大尺度
                return {"size": sizes["large"], "frequency": 0.2}
        elif decision_score > 0.6:
            # 强牌，主要使用中小尺度
            if random.random() < 0.7:  # 70%概率使用小尺度
                return {"size": sizes["small"], "frequency": 0.7}
            else:  # 30%概率使用中等尺度
                return {"size": sizes["medium"], "frequency": 0.3}
        else:
            # 诈唬，使用混合尺度
            if random.random() < 0.5:  # 50%概率使用小尺度
                return {"size": sizes["small"], "frequency": 0.5}
            else:  # 50%概率使用中等尺度
                return {"size": sizes["medium"], "frequency": 0.5}

    def _calculate_bet_amount(self, player: Player, game_state: Dict[str, Any],
                              decision_score: float, min_raise: int) -> int:
        """计算下注金额"""
        pot_size = game_state['pot']

        # 根据决策分数选择下注尺度
        if decision_score > 0.8:
            # 超强牌，使用较大下注
            bet_fraction = 0.75 + random.random() * 0.25  # 75%-100%底池
        elif decision_score > 0.6:
            # 强牌，使用中等下注
            bet_fraction = 0.5 + random.random() * 0.25  # 50%-75%底池
        else:
            # 诈唬或中等牌力，使用较小下注
            bet_fraction = 0.33 + random.random() * 0.17  # 33%-50%底池

        bet_amount = int(pot_size * bet_fraction)
        bet_amount = max(min_raise, bet_amount)
        bet_amount = min(bet_amount, player.chips)

        return bet_amount

    def _calculate_raise_amount(self, player: Player, game_state: Dict[str, Any],
                                decision_score: float, min_raise: int) -> int:
        """计算加注金额"""
        current_bet = game_state['current_bet']
        pot_size = game_state['pot']

        # 加注到当前下注的倍数
        if decision_score > 0.8:
            # 超强牌，较大加注
            raise_multiple = 3.0 + random.random()  # 3-4倍
        elif decision_score > 0.6:
            # 强牌，中等加注
            raise_multiple = 2.0 + random.random()  # 2-3倍
        else:
            # 诈唬或中等牌力，较小加注
            raise_multiple = 1.5 + random.random() * 0.5  # 1.5-2倍

        raise_amount = int(current_bet * raise_multiple)
        raise_amount = max(min_raise, raise_amount)
        raise_amount = min(raise_amount, player.chips)

        return raise_amount

    def _calculate_bluff_bet(self, player: Player, game_state: Dict[str, Any], min_raise: int) -> int:
        """计算诈唬下注金额"""
        pot_size = game_state['pot']

        # 诈唬通常使用较小下注
        bluff_fraction = 0.33 + random.random() * 0.17  # 33%-50%底池

        bluff_amount = int(pot_size * bluff_fraction)
        bluff_amount = max(min_raise, bluff_amount)
        bluff_amount = min(bluff_amount, player.chips)

        return bluff_amount


class MonteCarloGTOStrategy(GTOStrategy):
    """使用蒙特卡洛模拟的增强GTO策略"""

    def __init__(self, complexity: int = 3, simulations: int = 1000):
        """
        初始化蒙特卡洛GTO策略

        Args:
            complexity: 策略复杂度
            simulations: 蒙特卡洛模拟次数
        """
        super().__init__(complexity)
        self.simulations = simulations

    def decide(self, player: Player, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """使用蒙特卡洛模拟增强的GTO决策"""
        # 运行蒙特卡洛模拟
        action_ev = self._monte_carlo_simulation(player, game_state)

        # 选择期望价值最高的行动
        best_action = max(action_ev.items(), key=lambda x: x[1]['ev'])
        action_type = best_action[0]

        # 计算合适的金额
        if action_type == Action.RAISE:
            amount = self._calculate_optimal_raise(player, game_state, action_ev[action_type])
        else:
            amount = 0

        return action_type, amount

    def _monte_carlo_simulation(self, player: Player, game_state: Dict[str, Any]) -> Dict[Action, Dict[str, float]]:
        """蒙特卡洛模拟计算行动期望价值"""
        action_ev = {
            Action.FOLD: {"ev": 0.0, "frequency": 0.0},
            Action.CHECK: {"ev": 0.0, "frequency": 0.0},
            Action.CALL: {"ev": 0.0, "frequency": 0.0},
            Action.RAISE: {"ev": 0.0, "frequency": 0.0},
            Action.ALL_IN: {"ev": 0.0, "frequency": 0.0}
        }

        # 简化版的蒙特卡洛模拟
        # 实际实现应该模拟剩余牌和对手可能的范围

        for _ in range(self.simulations):
            # 模拟游戏结果
            ev_fold = self._simulate_fold(player, game_state)
            ev_check = self._simulate_check(player, game_state)
            ev_call = self._simulate_call(player, game_state)
            ev_raise = self._simulate_raise(player, game_state)
            ev_allin = self._simulate_allin(player, game_state)

            action_ev[Action.FOLD]["ev"] += ev_fold
            action_ev[Action.CHECK]["ev"] += ev_check
            action_ev[Action.CALL]["ev"] += ev_call
            action_ev[Action.RAISE]["ev"] += ev_raise
            action_ev[Action.ALL_IN]["ev"] += ev_allin

        # 计算平均EV
        for action in action_ev:
            action_ev[action]["ev"] /= self.simulations

        return action_ev

    def _simulate_fold(self, player: Player, game_state: Dict[str, Any]) -> float:
        """模拟弃牌的期望价值"""
        return 0.0  # 弃牌EV为0

    def _simulate_check(self, player: Player, game_state: Dict[str, Any]) -> float:
        """模拟过牌的期望价值"""
        # 基于手牌强度和位置计算
        stage = self._get_game_stage(game_state['community_cards'])
        hand_strength = self._calculate_gto_hand_strength(player.hand, game_state['community_cards'], stage)
        position_advantage = self._calculate_position_advantage(player, game_state)

        return hand_strength * position_advantage * game_state['pot'] * 0.1

    def _simulate_call(self, player: Player, game_state: Dict[str, Any]) -> float:
        """模拟跟注的期望价值"""
        call_amount = game_state['current_bet'] - player.current_bet
        if call_amount <= 0:
            return self._simulate_check(player, game_state)

        stage = self._get_game_stage(game_state['community_cards'])
        hand_strength = self._calculate_gto_hand_strength(player.hand, game_state['community_cards'], stage)
        pot_odds = self._calculate_pot_odds(player, game_state)

        # 简化计算
        ev = hand_strength * game_state['pot'] - (1 - hand_strength) * call_amount
        return ev

    def _simulate_raise(self, player: Player, game_state: Dict[str, Any]) -> float:
        """模拟加注的期望价值"""
        stage = self._get_game_stage(game_state['community_cards'])
        hand_strength = self._calculate_gto_hand_strength(player.hand, game_state['community_cards'], stage)
        range_advantage = self._calculate_range_advantage(player.hand, stage)

        # 基于手牌强度和范围优势计算
        fold_equity = 0.3  # 假设对手有30%概率弃牌
        raise_amount = self._calculate_raise_amount(player, game_state, hand_strength, game_state['min_raise'])

        ev = (fold_equity * game_state['pot'] +
              (1 - fold_equity) * (hand_strength * (game_state['pot'] + raise_amount) -
                                   (1 - hand_strength) * raise_amount))

        return ev

    def _simulate_allin(self, player: Player, game_state: Dict[str, Any]) -> float:
        """模拟全下的期望价值"""
        stage = self._get_game_stage(game_state['community_cards'])
        hand_strength = self._calculate_gto_hand_strength(player.hand, game_state['community_cards'], stage)

        # 全下EV计算
        fold_equity = 0.4  # 假设对手有40%概率弃牌
        allin_amount = player.chips

        ev = (fold_equity * game_state['pot'] +
              (1 - fold_equity) * (hand_strength * (game_state['pot'] + allin_amount) -
                                   (1 - hand_strength) * allin_amount))

        return ev

    def _calculate_optimal_raise(self, player: Player, game_state: Dict[str, Any],
                                 raise_data: Dict[str, float]) -> int:
        """计算最优加注金额"""
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']

        # 基于EV和频率计算最优加注尺度
        optimal_fraction = 0.5 + raise_data['ev'] * 0.5  # EV越高，加注越大
        raise_amount = int(pot_size * optimal_fraction)
        raise_amount = max(min_raise, raise_amount)
        raise_amount = min(raise_amount, player.chips)

        return raise_amount