from typing import List, Tuple

from card import Card
from rank import Rank


class HandEvaluator:
    """手牌评估器，用于评估扑克手牌的强度"""

    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[int, List[int]]:
        """
        评估手牌强度

        Args:
            cards: 要评估的牌列表（至少5张）

        Returns:
            (手牌等级, 踢子列表) 元组
            手牌等级: 9=皇家同花顺, 8=同花顺, 7=四条, 6=葫芦, 5=同花, 4=顺子, 3=三条, 2=两对, 1=一对, 0=高牌
            踢子列表: 用于比较同等级手牌的牌值列表
        """
        if len(cards) < 5:
            return 0, []

        # 按花色和点数分组
        rank_count = {}
        suit_count = {}

        for card in cards:
            rank_count[card.rank] = rank_count.get(card.rank, 0) + 1
            suit_count[card.suit] = suit_count.get(card.suit, 0) + 1

        # 检查同花
        flush_suit = None
        for suit, count in suit_count.items():
            if count >= 5:
                flush_suit = suit
                break

        # 同花牌
        flush_cards = [card for card in cards if card.suit == flush_suit] if flush_suit else []

        # 检查顺子
        sorted_ranks = sorted(set(card.rank.value for card in cards), reverse=True)
        straight_high = None

        # 检查A-5顺子（A作为1使用）
        if (Rank.ACE.value in sorted_ranks and
                Rank.TWO.value in sorted_ranks and
                Rank.THREE.value in sorted_ranks and
                Rank.FOUR.value in sorted_ranks and
                Rank.FIVE.value in sorted_ranks):
            straight_high = Rank.FIVE.value

        # 检查普通顺子
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i] - sorted_ranks[i + 4] == 4:
                straight_high = sorted_ranks[i]
                break

        # 同花顺
        if flush_suit and straight_high:
            straight_flush_cards = [card for card in flush_cards if
                                    card.rank.value <= straight_high and card.rank.value >= straight_high - 4]
            if len(straight_flush_cards) >= 5:
                # 皇家同花顺
                if straight_high == Rank.ACE.value:
                    return 9, [straight_high]
                return 8, [straight_high]

        # 四条
        four_of_a_kind = None
        for rank, count in rank_count.items():
            if count == 4:
                four_of_a_kind = rank.value
                break

        if four_of_a_kind:
            kickers = [rank.value for rank in rank_count if rank.value != four_of_a_kind]
            kickers.sort(reverse=True)
            return 7, [four_of_a_kind] + kickers[:1]

        # 葫芦
        three_of_a_kind = None
        pairs = []
        for rank, count in rank_count.items():
            if count == 3:
                three_of_a_kind = rank.value
            elif count == 2:
                pairs.append(rank.value)

        pairs.sort(reverse=True)

        if three_of_a_kind and pairs:
            return 6, [three_of_a_kind, pairs[0]]

        # 同花
        if flush_suit:
            flush_ranks = [card.rank.value for card in flush_cards]
            flush_ranks.sort(reverse=True)
            return 5, flush_ranks[:5]

        # 顺子
        if straight_high:
            return 4, [straight_high]

        # 三条
        if three_of_a_kind:
            kickers = [rank.value for rank in rank_count if rank.value != three_of_a_kind]
            kickers.sort(reverse=True)
            return 3, [three_of_a_kind] + kickers[:2]

        # 两对
        if len(pairs) >= 2:
            pairs.sort(reverse=True)
            kickers = [rank.value for rank in rank_count if rank.value not in pairs[:2]]
            kickers.sort(reverse=True)
            return 2, pairs[:2] + kickers[:1]

        # 一对
        if pairs:
            kickers = [rank.value for rank in rank_count if rank.value != pairs[0]]
            kickers.sort(reverse=True)
            return 1, [pairs[0]] + kickers[:3]

        # 高牌
        high_cards = sorted([card.rank.value for card in cards], reverse=True)
        return 0, high_cards[:5]

    @staticmethod
    def compare_hands(hand1: Tuple[int, List[int]], hand2: Tuple[int, List[int]]) -> int:
        """
        比较两手牌的强度

        Args:
            hand1: 第一手牌的(等级, 踢子)元组
            hand2: 第二手牌的(等级, 踢子)元组

        Returns:
            -1: hand1 < hand2
            0: hand1 == hand2
            1: hand1 > hand2
        """
        rank1, kickers1 = hand1
        rank2, kickers2 = hand2

        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1
        else:
            # 等级相同，比较踢子
            for k1, k2 in zip(kickers1, kickers2):
                if k1 > k2:
                    return 1
                elif k1 < k2:
                    return -1
            return 0
