from collections import Counter
from collections import deque
import random
from rich import print

'''
    版本：1.0
    上帝视角版本（只能1人多角来玩）
'''

class Player:
    """
        代表一个游戏玩家的类，玩家可以
        speak : 说出猜的数字
        get_response : 获得来自游戏的信息
    """
    def __init__(self, *args):
        # args 是卡牌的编号
        self.last_speak = 0
        self.hp = 6
        self.card_num = 5
        self.name  = input("input player name\n")
        self.cards = list(args)
        self.owl_card = dict()

    def draw(self, card):
        self.cards.append(card)
        self.card_num += 1

    def get_owl_card(self, card):
        self.owl_card.append(card)

    def speak(self):
        """
            猜一个数字
            Args:
                flag : 是否是第一次猜数字
            Returns:
                num  : 玩家猜对的数字
        """
        # 如果之前有speak的话 说明不是第一次猜了
        if self.last_speak:
            ans = int(input('是否继续猜，1是继续，0是放弃'))
            if ans == 0:
                # 手牌补满
                self.last_speak = 0
                return None, 5 - self.card_num
        speak_number = int(input(f'猜卡牌，输入一个数字，从{self.last_speak + 1} 到 8\n'))

        assert 1 <= speak_number <= 8
        # 如果猜对了，继续猜，或者不猜
        if speak_number in self.cards:
            self.cards.remove(speak_number)
            self.card_num -= 1
            self.last_speak = speak_number - 1 # 这里是为了和self.last_speak + 1的设定统一
            return speak_number, self.card_num
        else:
            self.hp -= 1
            self.last_speak = 0
            return self.hp <= 0, False


    def __repr__(self):
        return f'该玩家的姓名是 {self.name}，该玩家手上的卡牌有{self.cards}\n'


class Game:
    """
        最初的游戏版本，猫头鹰的数目是 4 个
        Args:
            player_num : 参加游戏的人数
    """
    def __init__(self, player_num):
        # 我感觉如果这些变量多了的话，可以写到一个字典里面去
        # 游戏人数和游戏玩家名字和游戏玩家实例
        self.player_num   = player_num
        self.player_name  = list()
        self.player_list  = list()
        self.player_point = list()
        # 游戏是否结束与回合是否结束
        self.endgame      = False
        self.endround     = False
        self.endepoch     = False
        # 卡牌池
        self.pool         = None
        # 弃牌堆
        self.garbage      = None
        # 猫头鹰卡牌池
        self.owl_pool     = None
        # 游戏中牌堆卡牌的数量
        self.card_num     = None

    def start_game(self):
        """
            游戏开始
        """
        # 开始准备一个新的epoch
        self._prepare_new_epoch()
        # 如果游戏没有结束，就开下一回合
        while not self.endgame:
            self._epoch()

    def _epoch(self):
        '''
            一局游戏
            因为这个游戏是积分制的，所以一场游戏可能有多个epoch
        '''
        self.curr_player_index = self.start_player_index
        while not self.endepoch:
            self._round()
            self.curr_player_index = (self.curr_player_index + 1) % self.player_num

    def _round(self):
        '''
            一个回合，一个玩家进行行动
            1 一个玩家说一个数字，如果他手上有这张牌，那么就执行这张牌的效果，这张卡就会要被打出丢入弃牌堆
            2 接着可以继续说一个数字或者停止说
            如果继续说一个数字，流程就转1
            如果停止说的话那么就把手牌补回5张
            3 1中说的数字是手上没有的话，那么就扣掉一点血，然后回合结束，如果hp到0了的话，那么游戏结束开始计分
        '''
        while not self.endround:
            index = self.curr_player_index
            player = self.player_list[index]
            # 说出一个数字
            card, res = player.speak()
            # 根据speak的返回值 然后进行_effect效果执行
            if res:
                self._effect(card)

    def _prepare_new_epoch(self):
        """
            游戏开始时，准备游戏
        """
        # 初始化牌堆
        self.pool     = deque([i for i in range(1, 9) for j in range(i)])
        self.garbage  = list()
        self.card_num = len(self.pool)
        self.owl_pool = {1:None, 2:None, 3:None, 4:None}

        # 洗牌
        random.shuffle(self.pool)

        # 首先拿出猫头鹰卡
        for i in range(1, 5):
            self.owl_pool[i] = self.pool.popleft()
            self.card_num -= 1

        # 初始化参加游戏的玩家
        for _ in range(self.player_num):
            cards = [self.pool.popleft() for _ in range(5)]
            self.card_num -= 5
            self.player_list.append(Player(*cards))
        # 决定起始玩家 random int 是取两头闭的
        for player in self.player_list:
            self.player_name.append(player.name)
        self.start_player_index = random.randint(0, self.player_num - 1)
        self.__test()

    def _effect_card1(self, flag):
        '''
            古代巨龙的效果是:
                如果猜错了，掷色子，掷到几自己就扣几点血（1~6）
                如果猜对了，掷色子，掷到几其余玩家就扣几点血（1~6）
        '''
        value = random.randint(1, 6)
        if not flag: # 如果猜错了的话
            target_player = self.player_list[self.curr_player_index]
        else: # 猜对了的情况
            pass

    def _effect_card2(self):
        '''
            暗黑幽灵的效果是:
                其他所有玩家失去一点hp，自己回复一点hp
        '''
        for i in range(self.player_num):
            target_player = self.player_list[i]
            if i == self.curr_player_index:
                target_player.hp = max(target_player.hp + 1, 6)
            else:
                target_player.hp -= 1
        self._check_epoch_end()

    def _effect_card3(self):
        '''
            甜蜜的梦的效果是:
                回复掷一次色子点数的生命值
        '''
        value = random.randint(1, 6)
        target_player = self.player_list[self.curr_player_index]
        target_player.hp = max(target_player.hp + 1, 6)

    def _effect_card4(self):
        '''
            猫头鹰的效果是:
                私下查看一个猫头鹰备用魔法石，盖在自己面前
                在该轮结束时，每有一个盖着的魔法石额外加1分
        '''
        pass

    def _effect_card5(self):
        '''
            闪电暴风雨的效果是:
                左边和右边的玩家hp - 1
        '''
        left_index = (self.curr_player_index - 1) % self.player_num
        right_index = (self.curr_player_index + 1) % self.player_num
        left_player = self.player_list[left_index]
        right_player = self.player_list[right_index]
        left_player.hp -= 1
        right_player.hp -= 1
        self._check_epoch_end()

    def _effect_card6(self):
        '''
            暴风雪的效果是:
                左手边的玩家hp - 1
        '''
        left_index = (self.curr_player_index - 1) % self.player_num
        left_player = self.player_list[left_index]
        left_player.hp -= 1
        self._check_epoch_end()

    def _effect_card7(self):
        '''
            火球的效果是:
                右手边的玩家hp - 1
        '''
        right_index = (self.curr_player_index - 1) % self.player_num
        right_player = self.player_list[right_index]
        right_player.hp -= 1
        self._check_epoch_end()

    def _effect_card8(self):
        '''
            魔法药水的效果是:
                回复一点hp
        '''
        target_player = self.player_list[self.curr_player_index]
        target_player.hp = max(target_player.hp + 1, 6)

    def _effect(self, card):
        """
            执行卡牌的效果
        """
        return None

    def _check_epoch_end(self):
        """
            查看epoch是否结束，如果结束了，那么就开始计分
        """
        pass

    def _calculate_point(self):
        """
            计分
        """
        pass

    def __test(self):
        '''
            测试函数，用来测试时间结点上面的某一点是否正确（通过打印成员函数）
        '''
        print(f'剩余卡牌为: {self.pool}')
        print(f'选出来的猫头鹰卡为: {self.owl_pool}')
        print(f'剩余卡牌数量为:  {self.card_num}')
        print(f'参加游戏的玩家: {self.player_list}')
        print(f'参加游戏的玩家的个数: {self.player_num}')
        print(f'起始玩家的索引: {self.start_player_index}')
        print(f'游戏是否结束: {self.endgame}')
        print(f'一轮是否结束: {self.endepoch}')

if __name__ == '__main__':
    g = Game(player_num=4)
    g.start_game()
