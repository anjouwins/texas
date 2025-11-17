from argparse import Action
from typing import Dict, Any, Tuple

from player import Player


class HumanPlayer(Player):
    """人类玩家类，通过控制台输入进行决策"""

    def make_decision(self, game_state: Dict[str, Any]) -> Tuple[Action, int]:
        """
        人类玩家通过控制台输入做出决策

        Args:
            game_state: 当前游戏状态信息

        Returns:
            (行动, 金额) 元组
        """
        print(f"\n{self.name}'s turn.")
        print(f"Your chips: ${self.chips}")
        print(f"Your hand: {self.hand}")
        print(f"Community cards: {game_state['community_cards']}")
        print(f"Current bet: ${game_state['current_bet']}")
        print(f"Pot size: ${game_state['pot']}")

        while True:
            try:
                action_input = input("Enter action (fold(f)/check(ck)/call(ca)/raise(r)/all_in(a)): ").strip().lower()

                if action_input == "fold" or action_input == "f":
                    return Action.FOLD, 0
                elif action_input == "check" or action_input == "ck":
                    return Action.CHECK, 0
                elif action_input == "call" or action_input == "ca":
                    call_amount = game_state['current_bet'] - self.current_bet
                    if call_amount > self.chips:
                        return Action.ALL_IN, self.chips
                    return Action.CALL, call_amount
                elif action_input == "raise" or action_input == "r":
                    min_raise = game_state['min_raise']
                    amount = int(input(f"Enter raise amount (minimum ${min_raise}): "))
                    if amount < min_raise:
                        print(f"Raise amount must be at least ${min_raise}")
                        continue
                    if amount > self.chips:
                        print("You don't have enough chips. Going all-in instead.")
                        return Action.ALL_IN, self.chips
                    return Action.RAISE, amount
                elif action_input == "all_in" or action_input == "a":
                    return Action.ALL_IN, self.chips
                else:
                    print("Invalid action. Please enter fold, check, call, raise, or all_in.")
            except ValueError:
                print("Invalid input. Please enter a valid number for raise amount.")