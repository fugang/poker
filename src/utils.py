import yaml
import logging
import logging.config
from card_base import Card

def load_cards():
    card_pool = []
    with open("test_cards.yaml", "rb") as reader:
        data_list = yaml.safe_load(reader)
    for data in data_list:
        card = Card.from_str(data)
        card_pool.append(card)
    return card_pool
    
    
log_conf = {
    "version": 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s %(levelname)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'games.log',
            'mode': "w",
        }
    },
    'loggers': { 
        'games': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
} 
logging.config.dictConfig(log_conf)   

logger = logging.getLogger("games")

