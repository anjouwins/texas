from typing import List

from humanPlayer import HumanPlayer
from player import Player
from texasHoldem import TexasHoldem


class GameManager:
    """游戏管理器，负责管理多局游戏和玩家"""

    def __init__(self, initial_players: List[Player] = None):
        """
        初始化游戏管理器

        Args:
            initial_players: 初始玩家列表
        """
        self.players = initial_players or []
        self.game = None
        self.hands_played = 0

    def add_player(self, player: Player):
        """添加玩家"""
        self.players.append(player)

    def remove_player(self, player_name: str):
        """移除玩家"""
        self.players = [p for p in self.players if p.name != player_name]

    def start_game(self, small_blind: int = 10, big_blind: int = 20, max_hands: int = 100):
        """
        开始游戏

        Args:
            small_blind: 小盲注金额
            big_blind: 大盲注金额
            max_hands: 最大手牌数
        """
        if len(self.players) < 2:
            print("Need at least 2 players to start the game")
            return

        self.game = TexasHoldem(self.players, small_blind, big_blind)

        print("Starting Texas Hold'em Game!")
        print(f"Players: {', '.join(player.name for player in self.players)}")
        print(f"Blinds: ${small_blind}/${big_blind}")
        print(f"Maximum hands: {max_hands}")

        for hand_num in range(1, max_hands + 1):
            print(f"\n" * 5)
            print(f"\n{'=' * 50}")
            print(f"Hand #{hand_num}")
            print(f"{'=' * 50}")

            self.game.start_hand()
            self.hands_played += 1

            # 显示玩家筹码
            print("\nPlayer chips:")
            for player in self.players:
                print(f"  {player.name}: ${player.chips}")

            # 检查是否有玩家出局
            active_players = [p for p in self.players if p.chips > 0]
            if len(active_players) < 2:
                print(f"\nGame over! Only {len(active_players)} player(s) remaining.")
                break

            # 询问是否继续（如果有真人玩家）
            if any(isinstance(player, HumanPlayer) for player in self.players):
                continue_input = input("\nPress Enter to continue or 'q' to quit: ").strip().lower()
                if continue_input == 'q':
                    break

        # 显示最终结果
        self._display_final_results()

    def _display_final_results(self):
        """显示最终结果"""
        print(f"\n{'=' * 50}")
        print("FINAL RESULTS")
        print(f"{'=' * 50}")

        # 按筹码排序
        sorted_players = sorted(self.players, key=lambda p: p.chips, reverse=True)

        for i, player in enumerate(sorted_players, 1):
            print(f"{i}. {player.name}: ${player.chips}")

        print(f"\nTotal hands played: {self.hands_played}")
        print(f"Winner: {sorted_players[0].name}!")