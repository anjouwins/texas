from gameManager import GameManager
from humanPlayer import HumanPlayer


def AIPlayer(param, param1, param2):
    pass


if __name__ == "__main__":
    # 创建游戏管理器
    manager = GameManager()

    # 添加玩家
    manager.add_player(AIPlayer("AI 1 ", 1000, BasicStrategy()))
    manager.add_player(AIPlayer("AI 2 ", 1000, AggressiveStrategy()))
    manager.add_player(AIPlayer("AI 3 ", 1000, ConservativeStrategy()))
    playerName = input("\nPress Enter your name to start the game: ")
    manager.add_player(HumanPlayer(playerName, 1000))

    # 开始游戏
    manager.start_game(small_blind=10, big_blind=20, max_hands=10)