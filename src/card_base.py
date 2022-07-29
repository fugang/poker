from enum import Enum
from collections import Counter
import copy
from functools import cmp_to_key


class CardNumError(Exception):
    pass
    

class CardSuitError(Exception):
    pass
    
class CardValueError(Exception):
    pass 
        
class CompareError(Exception):
    pass        

class ValueCard(Enum):
    TWO = 2
    THR = 3
    FOR = 4
    FIV = 5
    SIX = 6
    SVN = 7
    EHT = 8
    NIN = 9
    TEN = 10
    JAK = 11
    QUE = 12
    KIN = 13
    ACE = 14

class SuitCard(Enum):
    S = 1
    H = 2
    C = 3
    D = 4


class HandValue(Enum):
    RoyalFlush = 10
    StraightFlush = 9
    FourKind = 8
    FullHouse = 7
    Flush = 6
    Straight = 5
    ThreeKind = 4
    TwoPair = 3
    Pair = 2
    HighCard = 1
    

def sort_values(values):
    def comp(key1, key2):
        if key1[1] > key2[1]:
            return -1
        elif key1[1] < key2[1]:
            return 1
        else:
            if key1[0] > key2[0]:
                return -1
            elif key1[0] < key2[0]:
                return 1
            else:
                return 0   
    data = sorted(values, key=cmp_to_key(comp))
    data = [x[0] for x in data]
    return data
    
def compare_value(list_a, list_b):
    if len(list_a) != len(list_b):
        raise CompareError("value error")
    for a, b in zip(list_a, list_b):
        if a > b:
            return 1
        elif a < b:
            return -1
        else:
            continue
    return 0  


class Card():
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    @classmethod
    def from_str(cls, value):
        suit = value[0]
        value = value[1:]
        try:
            suit = SuitCard[suit]
        except ValueError:
            raise CardSuitError("illegal suit")
        try:    
            value = ValueCard(int(value))
        except ValueError:
            raise CardValueError("illegal value")
        return cls(suit, value)     
    
    def __repr__(self):
        return f"{self.suit.name}{self.value.value}"
    
    def value(self):
        return self.value.value
        
    def __lt__(self, other):
        if self.value.value != other.value.value:
            return self.value.value < other.value.value
        else:
            return self.suit.value > other.suit.value
        
    def __gt__(self, other):
        if self.value.value != other.value.value:
            return self.value.value > other.value.value
        else:
            return self.suit.value < other.value.value 
        
    def __eq__(self, other):
        return self.value.value == other.value.value

        
class HandCards():
    def __init__(self, cards):
        if len(cards) != 5:
            raise CardNumError("illegal hand cards")
        self.suits = set()
        self.values = []
        self.cards = cards
        self.counter = Counter()
        self.init()
        
    def init(self):
        for card in self.cards:
            self.suits.add(card.suit.value)
            self.values.append(card.value.value)
            self.counter[card.value] += 1
        self.values.sort()
        self.values.reverse()
        self.max_value = self.values[0]       
                   
    def __repr__(self):
        self.cards.sort()
        self.cards.reverse()
        values = [str(x) for x in self.cards]
        return " ".join(values)
    
    @staticmethod
    def _check_straight(values):
        tup_data = zip(values[:5], values[1:])
        for x, y in tup_data:
            if abs(x - y) != 1:
                return False
        return True
        
    @property
    def is_pair(self):
        return list(self.counter.values()).count(2) == 1 and list(self.counter.values()).count(3) == 0     
       
    @property
    def is_two_pair(self):
        return list(self.counter.values()).count(2) == 2
        
    @property
    def is_three_kind(self):
        return list(self.counter.values()).count(3) == 1 and list(self.counter.values()).count(2) == 0 
        
    @property
    def is_straight(self):
        return self._check_straight(self.values) and len(self.suits) != 1    
        
    @property    
    def is_flush(self):
        return len(self.suits) == 1 and not self._check_straight(self.values)
        
    @property
    def is_full_house(self):
        return list(self.counter.values()).count(3) == 1 and list(self.counter.values()).count(2) == 1 
        
    @property
    def is_four_kind(self):
        return list(self.counter.values()).count(4) == 1
        
    @property
    def is_straight_flush(self):
        if len(self.suits) == 1 and self._check_straight(self.values):
            if self.suits == set([SuitCard.S.value]):
                if self.max_value != ValueCard.ACE.value:
                    return True
                else:
                    return False
            return True
        else:
            return False
        
    @property
    def is_royal_flush(self):
        return len(self.suits) == 1 and self._check_straight(self.values) and \
            self.suits == set([SuitCard.S.value]) and self.max_value == ValueCard.ACE.value
    
    def get_max_value(self):
        if self.hand_value in [HandValue.HighCard, HandValue.Flush, HandValue.Straight, HandValue.StraightFlush, HandValue.RoyalFlush]:
            return self.values
        elif self.hand_value in [HandValue.Pair, HandValue.TwoPair, HandValue.ThreeKind, HandValue.FullHouse, HandValue.FourKind]:
            tuple_data = [(key.value, value) for key, value in self.counter.items()]
            return sort_values(tuple_data)

            
    def __gt__(self, other):
        if self.hand_value != other.hand_value:
            return self.hand_value.value > other.hand_value.value
        else:
            num_list = self.get_max_value()
            other_list = other.get_max_value()
            if compare_value(num_list, other_list) == 1:
                return True
            else:
                return False
    
    def __lt__(self, other):
        if self.hand_value != other.hand_value:
            return self.hand_value.value < other.hand_value.value
        else:
            num_list = self.get_max_value()
            other_list = other.get_max_value()
            if compare_value(num_list, other_list) == -1:
                return True
            else:
                return False
            
    def __eq__(self, other):
        if self.hand_value.value != other.hand_value.value:
            return False
        else:
            num_list = self.get_max_value()
            other_list = other.get_max_value() 
            if compare_value(num_list, other_list) == 0:
                return True
            else:
                return False
            
    @property    
    def hand_value(self):
        if self.is_royal_flush:
            return HandValue.RoyalFlush
        elif self.is_straight_flush:
            return HandValue.StraightFlush
        elif self.is_four_kind:
            return HandValue.FourKind
        elif self.is_full_house:
            return HandValue.FullHouse
        elif self.is_flush:
            return HandValue.Flush
        elif self.is_straight:
            return HandValue.Straight
        elif self.is_three_kind:
            return HandValue.ThreeKind
        elif self.is_two_pair:
            return HandValue.TwoPair
        elif self.is_pair:
            return HandValue.Pair
        else:
            return HandValue.HighCard
    
    @classmethod              
    def from_list(cls, value_list):
        card_list = []
        for value in value_list:
            card = Card.from_str(value)
            card_list.append(card)
        return cls(card_list)
             
         
class PickupCard:
    def __init__(self, cards):
#        if len(cards) != 7:
#            raise CardNumError("illegal hand cards")  
        self.max_hand = None
        self.cards = cards
        self.combines = self.get_combines()
    
    @classmethod              
    def from_list(cls, value_list):
        card_list = []
        for value in value_list:
            card = Card.from_str(value)
            card_list.append(card)
        return cls(card_list)    
        
    def get_combines(self):
        result = []
        copy1 = copy.copy(self.cards)
        for card1 in self.cards:
            copy1.remove(card1)
            copy2 = copy.copy(copy1)
            for card2 in copy1:
                copy2.remove(card2)
                copy3 = copy.copy(copy2)
                for card3 in copy2:
                    copy3.remove(card3)
                    copy4 = copy.copy(copy3)
                    for card4 in copy3:
                        copy4.remove(card4)
                        for card5 in copy4:
                            result.append([card1, card2, card3, card4, card5])
        return result
        
    def get_max_combine(self):
        for card_list in self.combines:
            hand = HandCards(card_list)
            if self.max_hand is None:
                self.max_hand = hand
            elif self.max_hand < hand:
                self.max_hand = hand
        return self.max_hand
        
    def get_result(self):
        max_hand = self.get_max_combine()
        level = max_hand.hand_value
        return {"max_hand": str(max_hand), "max_level": level.name}   
        

def get_max_card(card_group):
    max_card = max(card_group)
    max_group = list(filter(lambda x: x==max_card, card_group))
    return max_group
    
             
