from utils import logger

class PositionError(Exception):
    pass
    
class PlayerError(Exception):
    pass

class Roulette():
    def __init__(self, blind, big_blind):
        self.pot_total = 0
        self.bet = 0
        self.times = 0
        self.blind = blind
        self.big_blind = big_blind
        self.player_info = {}
        
    def new_round(self):
        self.bet = 0
        self.times = 0
        
    def pre_flop(self):
        self.new_round()
        self.rounder = 1
    
    def flop(self):
        self.new_round()
        self.rounder = 2
    
    def turn(self):
        self.new_round()
        self.rounder = 3
    
    def river(self):
        self.new_round()
        self.rounder = 4
        
    def update_bet(self, bet):
        self.bet = max(self.bet, bet)    
        
    def update_player(self, player, pot, position=None):
        if player in self.player_info:
            data = self.player_info[player]
            data['pot'] += pot
        else:
            if position is None:
                raise PositionError
            data = {'pot': pot, "position": position}
        self.player_info[player] = data
   
    def set_times(self, times):
        self.times = times + 1  
        
    def debug(self):
        for name, value in self.player_info.items():
            logger.debug("=====bet info. rounder=%s, times=%s. \
                        player=%s, amount=%s", self.rounder, self.times, name, value)
        logger.debug("####### Roulette info. rounder=%s, times=%s. \
                pot=%s, bet=%s", self.rounder, self.times, self.pot_total, self.bet)   
    
    def check_this_round(self):
        pot = [p["pot"] for p in self.player_info.values()]
        if len(set(pot)) == 1:
            return True
        else:
            return False

    def get_player_position(self, name):
        data = self.player_info[name]
        if data is None:
            raise PlayerError    
        return data["position"]
        
                 
    
