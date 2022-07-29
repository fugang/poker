from utils import load_cards, logger
import random
from card_base import Card, HandCards, PickupCard
import sys

from card_base import Card, HandCards, PickupCard, get_max_card
from roulette import Roulette
from clint.textui import puts, colored, indent
from player import Player, HumanPlayer, PlayerBroken


class RouletteBattle():
    def __init__(self, players, cards, blind, big_blind):
        self.players = players
        self.rult = Roulette(blind, big_blind)
        self.cards = cards
        self.desk_cards = []
                    
    def pre_flop(self):
        puts(colored.cyan(f"$$$$$$$$$$$$$$pre_flop$$$$$$$$$$$$"))
        self.rult.pre_flop()
        for index, player in enumerate(self.players):
            if index == 0:
                amount = self.rult.blind
            elif index == 1:
                amount = self.rult.big_blind
            else:
                amount = 0
            try:
                player.check_amount(amount)
            except PlayerBroken:
                player.active = False
                if player.role == "human":
                    puts(colored.green("you broken"))
                    self.gameover()
            two_cards = []
            for _ in range(2):
                two_cards.append(self.cards.pop())
            player.pre_flop(self.rult, amount, two_cards, index)
   
        self.debug()
                
        for i in range(3):
            tag = self.settle(i)
            if tag:
                break
        self.debug()
            
    def check_player_nums(self):
        self.players = [p for p in self.players if p.active]
        if len(self.players) == 1:
            self.gameover()
    
    def debug(self):
        for name, value in self.rult.player_info.items():
            logger.debug("=====bet info. rounder=%s, times=%s. \
                        player=%s, amount=%s", self.rult.rounder, self.rult.times, name, value)
        for p in self.players:
            logger.debug("+++++player info. rounder=%s, times=%s. \
                    player=%s, amount=%s", self.rult.rounder, self.rult.times, p.name, p.amount)
        self.rult.debug()
        
    def settle(self, times):
        self.rult.set_times(times)
        self.check_player_nums()
        for p in self.players:
            p.act(self.rult)
        self.check_player_nums()
        return self.rult.check_this_round()
           
    def check_showdown(self):
        for p in self.players:
            if not p._show:
                return False
        return True

    def flop_step(self):
        puts(colored.cyan(f"$$$$$$$$$$$$$$flop step$$$$$$$$$$$$"))
        self.rult.flop()
        round_cards = []
        self.cards.pop()
        for i in range(3):
            round_cards.append(self.cards.pop())
        for p in self.players:
            p.flop(round_cards)
        self.desk_cards.extend(round_cards)
        for i in range(3):
            tag = self.settle(i)
            if tag:
                break
    
    def turn_step(self):
        self.rounder = 3
        self.cards.pop()
        card = self.cards.pop()
        for p in self.players:
            p.turn(card)
        self.desk_cards.append(card)
        self.settle()        
            
    def river_step(self):
        self.rounder = 4
        self.cards.pop()
        card = self.cards.pop()
        for p in self.players:
            p.river(card)
        self.desk_cards.append(card)
        self.settle()            
            
    def gameover(self):
        if self.players[0].role == "human":
            puts(colored.cyan(f"game over. winner is you"))
        else:
            puts(colored.cyan(f"game over. winner is {self.players[0].name}"))
        sys.exit(0)       
   
    def do_last(self):
        print("unsupport")
        sys.exit(0)
        
    def desk_cards_str(self):
        return " ".join([str(c) for c in self.desk_cards])
        
    def do_showdown(self):
        puts(colored.cyan(f"desk cards: {self.desk_cards_str()}"))
        for p in self.players:
            result = p.pick_hand.get_result()
            max_hand = result["max_hand"]
            level = result["max_level"]
            puts("---->" + colored.blue(f"PLAYER: {p.name}"))
            puts("     " + colored.green(f"hands cards: {p.get_base_card()}"))
            puts("     " + colored.green(f"max cards: {max_hand}"))
            puts("     " + colored.green(f"max cards: {level}"))
        winner_group = get_max_card(self.players)
        if len(winner_group) == 1:
            if winner_group[0].role == "human":
                puts(colored.red("you win"))
            else:
                puts(colored.green("you lost. winners is ") + colored.yellow(f"{winner_group[0].name}"))
        else:
            winner_name = ""
            for winner in winner_group:
                if winner.role == "human":
                    puts(colored.red("draw game"))
                    break
                else:
                    winner_name += winner.name + ","
            else:
                puts(colored.green("you lost. winners is ") + colored.yellow(f"{winner_name}"))
                   

    def do_pipeline(self):
        self.pre_flop()
        self.flop_step()
#        while True:
#            if not r.check_showdown():
#                self.do_last()
#            else:
#                self.do_showdown()
#                break    
                            
# players = [Player("Player1", amount=5), HumanPlayer(amount=10), Player("Player2", amount=20)]   
players = [Player("Player1", amount=10), Player("Player2", amount=10), Player("Player3", amount=10)]           
cards = load_cards()
for i in range(5):
    random.shuffle(cards)
blind = 1
big_blind = 2        
r = RouletteBattle(players, cards, blind, big_blind)
r.do_pipeline()


