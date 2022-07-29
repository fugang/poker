import sys


from clint.arguments import Args   
import random

from card_base import Card, HandCards, PickupCard
from clint.textui import puts, colored, indent
from utils import logger


class PlayError(Exception):
    pass
    

class PlayerBroken(Exception):
    pass    

class Player:
    def __init__(self, name, amount=200, role="AI"):
        self.name = name
        self.hands = []
        self.amount = amount
        self.role = role
        self.active = True
        self._show = False
        self.pick_hand = None
        self.max_hand = None
        self.progress_amount = [0, 0, 0, 0]
            
    def check_amount(self, amount):
        if self.amount < amount:
            raise PlayerBroken()       
    
    def color_name(self):
        if self.role == "human":
            return colored.yellow(f"{self.name}")
        else:
            return colored.white(f"{self.name}")
            
    def pre_flop(self, roulette, bet, two_cards, position):
        if len(two_cards) != 2:
            raise PlayError
        ss1 = colored.magenta(f"player[")
        ss2 = self.color_name()
        ss3 = colored.magenta(f"]pre_flop. bet ${bet}")
        puts(ss1 + ss2 + ss3)
        self.hands.extend(two_cards)
        self.amount -= bet
        self.progress_amount[roulette.rounder-1] = bet
        roulette.update_player(self.name, bet, position)
        roulette.update_bet(bet)
        logger.info("player=%s preflop. bet=$%s, left=$%s", self.name, bet, self.amount)
        
        
    def flop(self, three_cards):
        self.rounder = 2
        if len(three_cards) != 3:
            raise PlayError("error round")    
        self.hands.extend(three_cards)
                
    def turn(self, card):
        self.rounder = 3
        self.hands.append(card)
        
    def river(self, card):
        self.rounder = 4
        self.hands.append(card)
        
    def fold(self):
        self.active = False
    
    def get_current_amount(self, roulette):
        if roulette.rounder != 0:
            return self.progress_amount[roulette.rounder - 1]
        else:
            raise PlayError("check amount error")
              
    def check(self, roulette):
        if roulette.bet == 0:
            extra = 0
        else:
            cur_amount = self.get_current_amount(roulette)
            if cur_amount < roulette.bet:
                extra = roulette.bet - cur_amount
            else:
                extra = 0
        self.amount -= extra
        roulette.update_player(self.name, extra)
        ss1 = colored.magenta(f"player[")
        ss2 = self.color_name()
        ss3 = colored.magenta(f"] check")
        puts(ss1 + ss2 + ss3)
        logger.info("player=%s do check. amount=$%s", self.name, self.amount)
        return extra
        
    def call(self, roulette):
        if roulette.bet == 0:
            extra = 0
        else:
            cur_amount = self.get_current_amount(roulette)
            if cur_amount < roulette.bet:
                extra = roulette.bet - cur_amount
            else:
                extra = 0
        self.amount -= extra
        roulette.update_player(self.name, extra)
        ss1 = colored.magenta(f"player[")
        ss2 = self.color_name()
        ss3 = colored.magenta(f"] call")
        puts(ss1 + ss2 + ss3)
        logger.info("player=%s do call. amount=$%s", self.name, self.amount)
        return extra
        
    def bet(self, roulette, extra):
        self.amount -= extra
        roulette.update_player(self.name, extra)
        roulette.update_bet(extra)
        ss1 = colored.magenta(f"player[")
        ss2 = self.color_name()
        ss3 = colored.magenta(f"] bet. bet ${extra}")
        puts(ss1 + ss2 + ss3)
        logger.info("player=%s do bet. bet=$%s, amount=$%s", self.name, extra, self.amount)
        return extra
        
    def do_raise(self, roulette):
        if roulette.rounder in [1, 2]:
            extra = roulette.bet + roulette.times * roulette.blind
        else:
            extra = roulette.bet + roulette.times * roulette.big_blind
        self.amount -= extra
        roulette.update_player(self.name, extra)
        roulette.update_bet(extra)
        ss1 = colored.magenta(f"player[")
        ss2 = self.color_name()
        ss3 = colored.magenta(f"] raise. raise ${extra}")
        puts(ss1 + ss2 + ss3)
        logger.info("player=%s do raise. raise=$%s, amount=$%s", self.name, extra, self.amount)
        return extra
        
    def all_in(self):
        pass
       
    def showdown(self):
        self._show = True
        self.pick_hand = PickupCard(self.hands)
        self.max_hand = self.pick_hand.get_max_combine()

    def get_base_card(self):
        cards = self.hands[:2]
        return " ".join(str(c) for c in cards)
      
    def do_strategy(self, roulette):
        if roulette.rounder == 1:
            return self.check(roulette)
        elif roulette.rounder == 2:
            position = roulette.get_player_position(self.name)
            if position == 0:
                if roulette.times == 0:
                    return self.bet(roulette, 5)
                else:
                    return self.call(roulette)
            else:
                return self.do_raise(roulette)
      
    def act(self, roulette):
        data = self.do_strategy(roulette)
        
    def __lt__(self, other):
        return self.max_hand < other.max_hand
    
    def __gt__(self, other):
        return self.max_hand > other.max_hand
    
    def __eq__(self, other):
        return self.max_hand == other.max_hand


class HumanPlayer(Player):
    def __init__(self, name="human", amount=200):
        super(HumanPlayer, self).__init__(name, amount, role="human")    

    def human_select(self, extra):
        action = input(">>>> ")
        if action.lower() == "ch":
            if extra > 0:
                return False
            self.check()
        elif action.lower() == "ca":
            self.call(extra)
        elif action.lower() == "r":
            self.do_raise()
        elif action.lower() == "f":
            self.fold()
        elif action.lower() == "s":
            self.showdown()
        else:
            return False
        return True
            
    def show_tips(self):
        puts(colored.cyan("======select you choice=========="))
            
    def show_check(self):
        self.show_tips()
        puts(colored.cyan("Ch[eck] Ca[ll] R[aise F[old]"))
        
    def show_call(self):
        self.show_tips()
        puts(colored.cyan("Ca[ll] R[aise] F[old]"))  
    
    def show_warning(self):
        puts(colored.yellow("Invalid select. re-select"))            
            
    def show_cards(self):
        base_str = " ".join([str(x) for x in self.hands[:2]]) + " "
        if len(self.hands) > 2:
            other_str = " ".join([str(x) for x in self.hands[2:]])
        else:
            other_str = "" 
        if other_str:
            puts(colored.magenta("you hands is ")  + colored.white(base_str) + colored.red(other_str))
        else:
            puts(colored.magenta("you hands is ")  + colored.white(base_str))            
            
    def act(self, roulette):
        while True:
            self.show_cards()
            if roulette.bet == 0:
                self.show_check()
            else:
                self.show_call()
            tag = self.human_select(bet, rounder)
            if tag:
                break
            else:
                self.show_warning()
            return extra


