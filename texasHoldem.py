from typing import List, Tuple

from card import Card
from deck import Deck
from handEvaluator import HandEvaluator
from player import Player


class TexasHoldem:
    """德州扑克主游戏类"""

    def __init__(self, players: List[Player], small_blind: int = 10, big_blind: int = 20):
        """
        初始化德州扑克游戏

        Args:
            players: 玩家列表
            small_blind: 小盲注金额
            big_blind: 大盲注金额
            deck:牌堆
        """
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = big_blind
        self.dealer_position = 0
        self.hand_evaluator = HandEvaluator()
        self.hand_history = []

    def start_hand(self):
        """开始新的一手牌"""
        # 重置游戏状态
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = self.big_blind

        # 重置玩家状态
        for player in self.players:
            player.reset_hand()

        # 发牌
        self._deal_hole_cards()

        # 下盲注
        self._post_blinds()

        # 进行下注轮次
        self._run_betting_rounds()

        # 摊牌并分配底池
        winners = self._determine_winner()
        self._distribute_pot(winners)

        # 记录手牌历史
        self._record_hand_history(winners)

        # 更新庄家位置
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

    def _deal_hole_cards(self):
        """发底牌"""
        for _ in range(2):
            for player in self.players:
                if not player.folded:
                    player.receive_cards([self.deck.deal()])

    def _post_blinds(self):
        """下盲注"""
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)

        small_blind_player = self.players[sb_pos]
        big_blind_player = self.players[bb_pos]

        # 下小盲注
        sb_bet = small_blind_player.bet(self.small_blind)
        self.pot += sb_bet
        self.current_bet = sb_bet

        # 下大盲注
        bb_bet = big_blind_player.bet(self.big_blind)
        self.pot += bb_bet
        self.current_bet = bb_bet

        print(f"Blinds: {small_blind_player.name} posts small blind ${sb_bet}, "
              f"{big_blind_player.name} posts big blind ${bb_bet}")

    def _run_betting_rounds(self):
        """运行所有下注轮次"""
        betting_rounds = [
            ("Pre-flop", 0),
            ("Flop", 3),
            ("Turn", 1),
            ("River", 1)
        ]

        for round_name, community_cards_count in betting_rounds:
            # 如果只剩一个活跃玩家，提前结束
            if self._active_players_count() <= 1:
                break

            print(f"\n--- {round_name} ---")

            # 发公共牌（除了翻牌前）
            if community_cards_count > 0:
                self._deal_community_cards(community_cards_count)

            # 进行下注轮
            self._betting_round()

    def _deal_community_cards(self, count: int):
        """发公共牌"""
        for _ in range(count):
            card = self.deck.deal()
            self.community_cards.append(card)

        print(f"Community cards: {self.community_cards}")

    def _betting_round(self):
        """一轮下注"""
        start_pos = (self.dealer_position + 3) % len(self.players)  # 大盲注后开始

        # 重置当前轮下注
        for player in self.players:
            if not player.folded:
                player.current_bet = 0

        # 下注轮次
        last_raiser = None
        current_pos = start_pos
        actions_taken = 0

        while actions_taken < len(self.players) or (last_raiser is not None and current_pos != last_raiser):
            player = self.players[current_pos]

            if not player.folded and not player.all_in:
                # 获取游戏状态
                game_state = {
                    'community_cards': self.community_cards,
                    'current_bet': self.current_bet,
                    'min_raise': self.min_raise,
                    'pot': self.pot
                }

                # 玩家决策
                if hasattr(player, 'make_decision'):
                    action, amount = player.make_decision(game_state)
                else:
                    # 默认策略
                    strategy = BasicStrategy()
                    action, amount = strategy.decide(player, game_state)

                # 执行行动
                self._execute_action(player, action, amount)

                # 记录最后一个加注者
                if action == Action.RAISE or action == Action.ALL_IN:
                    last_raiser = current_pos

            current_pos = (current_pos + 1) % len(self.players)
            actions_taken += 1

        # 重置当前下注
        self.current_bet = 0
        self.min_raise = self.big_blind

    def _execute_action(self, player: Player, action: Action, amount: int):
        """执行玩家行动"""
        if action == Action.FOLD:
            player.folded = True
            print(f"\n{player.name} folds")

        elif action == Action.CHECK:
            # 检查只有在没有下注或已经跟注的情况下才有效
            if self.current_bet > player.current_bet:
                # 无效的检查，转换为弃牌
                player.folded = True
                print(f"\n{player.name} cannot check, folds instead")
            else:
                print(f"\n{player.name} checks")

        elif action == Action.CALL:
            call_amount = self.current_bet - player.current_bet
            actual_call = player.bet(call_amount)
            self.pot += actual_call
            print(f"\n{player.name} calls ${actual_call}")

        elif action == Action.RAISE:
            # 确保加注金额有效
            total_bet = player.current_bet + amount
            if total_bet <= self.current_bet:
                # 无效的加注，转换为跟注
                call_amount = self.current_bet - player.current_bet
                actual_call = player.bet(call_amount)
                self.pot += actual_call
                print(f"\n{player.name} calls ${actual_call} (invalid raise)")
            else:
                # 有效的加注
                actual_raise = player.bet(amount)
                self.pot += actual_raise
                self.current_bet = total_bet
                self.min_raise = amount
                print(f"\n{player.name} raises to ${total_bet}")

        elif action == Action.ALL_IN:
            all_in_amount = player.chips
            player.bet(all_in_amount)
            self.pot += all_in_amount

            total_bet = player.current_bet
            if total_bet > self.current_bet:
                self.current_bet = total_bet
                self.min_raise = total_bet - self.current_bet
                print(f"\n{player.name} goes all-in with ${all_in_amount}")
            else:
                print(f"\n{player.name} calls all-in with ${all_in_amount}")

    def _active_players_count(self) -> int:
        """计算未弃牌的玩家数量"""
        return sum(1 for player in self.players if not player.folded)

    def _determine_winner(self) -> List[Tuple[Player, List[Card]]]:
        """确定获胜者"""
        active_players = [(player, player.hand) for player in self.players if not player.folded]

        if len(active_players) == 0:
            return []

        # 如果只有一个活跃玩家，他自动获胜
        if len(active_players) == 1:
            return [(active_players[0][0], active_players[0][1])]

        # 评估每个玩家的牌力
        player_hands = []
        for player, hand in active_players:
            all_cards = hand + self.community_cards
            hand_rank, kickers = self.hand_evaluator.evaluate_hand(all_cards)
            player_hands.append((player, hand_rank, kickers, all_cards))

        # 找出最佳手牌
        best_hand_rank = max(hand_rank for _, hand_rank, _, _ in player_hands)
        best_players = [(player, cards) for player, hand_rank, _, cards in player_hands if hand_rank == best_hand_rank]

        # 如果有平局，比较踢子
        if len(best_players) > 1:
            # 获取最佳踢子
            best_kickers = []
            for _, hand_rank, kickers, _ in player_hands:
                if hand_rank == best_hand_rank:
                    if not best_kickers or kickers > best_kickers:
                        best_kickers = kickers

            best_players = [(player, cards) for player, hand_rank, kickers, cards in player_hands
                            if hand_rank == best_hand_rank and kickers == best_kickers]

        return best_players

    def _distribute_pot(self, winners: List[Tuple[Player, List[Card]]]):
        """分配底池"""
        if not winners:
            print("No winners - all players folded")
            return

        # 简化实现：平分底池
        share = self.pot // len(winners)
        remainder = self.pot % len(winners)

        for i, (winner, _) in enumerate(winners):
            amount = share + (1 if i < remainder else 0)
            winner.chips += amount
            print(f"{winner.name} wins ${amount} with {winner.hand}")

        self.pot = 0

    def _record_hand_history(self, winners: List[Tuple[Player, List[Card]]]):
        """记录手牌历史"""
        hand_record = {
            'community_cards': self.community_cards.copy(),
            'winners': [(winner.name, winner.hand.copy()) for winner, _ in winners],
            'pot': self.pot
        }
        self.hand_history.append(hand_record)

    def get_game_stats(self) -> Dict[str, Any]:
        """获取游戏统计信息"""
        return {
            'total_hands': len(self.hand_history),
            'players': [{'name': player.name, 'chips': player.chips} for player in self.players],
            'current_dealer': self.players[self.dealer_position].name
        }
