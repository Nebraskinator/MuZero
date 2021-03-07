import collections
from typing import Optional, Dict

import tensorflow as tf

from game.supermariobros import SuperMarioBros
from game.game import AbstractGame
from networks.smb_network import SuperMarioBrosNetwork
from networks.network import BaseNetwork, UniformNetwork

KnownBounds = collections.namedtuple('KnownBounds', ['min', 'max'])


class MuZeroConfig(object):

    def __init__(self,
                 game,
                 nb_epochs: int,
                 network_args: Dict,
                 network,
                 action_space_size: int,
                 max_moves: int,
                 discount: float,
                 batch_size: int,
                 td_steps: int,
                 visit_softmax_temperature_fn,
                 lr: float,
                 network_path: str,
                 memory_path: str,
                 known_bounds: Optional[KnownBounds] = None,
                 ):
        ### Environment
        self.game = game

        ### Self-Play
        self.action_space_size = action_space_size
        # self.num_actors = num_actors

        self.visit_softmax_temperature_fn = visit_softmax_temperature_fn
        self.max_moves = max_moves
        self.discount = discount


        # If we already have some information about which values occur in the
        # environment, we can use them to initialize the rescaling.
        # This is not strictly necessary, but establishes identical behaviour to
        # AlphaZero in board games.
        self.known_bounds = known_bounds

        ### Training
        self.nb_epochs = nb_epochs  # Nb of epochs per training loop

        # self.training_steps = int(1000e3)
        # self.checkpoint_interval = int(1e3)
        self.window_size = int(115000)
        self.batch_size = batch_size
        self.num_unroll_steps = 5
        self.td_steps = td_steps

        self.weight_decay = 1e-4
        self.momentum = 0.9

        self.network_args = network_args
        self.network = network
        self.lr = lr
        
        self.initial_random_moves = 0
        
        self.network_path = network_path
        self.memory_path = memory_path
        
        self.num_searches = 3
        self.search_depth = 3
        # Exponential learning rate schedule
        # self.lr_init = lr_init
        # self.lr_decay_rate = 0.1
        # self.lr_decay_steps = lr_decay_steps

    def new_game(self, worlds) -> AbstractGame:
        return self.game(worlds, self.discount, self.memory_path)

    def new_network(self) -> BaseNetwork:
        return self.network(**self.network_args)

    def uniform_network(self) -> UniformNetwork:
        return UniformNetwork(self.action_space_size)

    def new_optimizer(self) -> tf.keras.optimizers:
        return tf.keras.optimizers.Adam(learning_rate=self.lr, clipvalue=5)
    def ex_optimizer(self) -> tf.keras.optimizers:
        return tf.keras.optimizers.Adam(learning_rate=self.lr/4, clipvalue=5)

    
def make_supermariobros_config() -> MuZeroConfig:
    def visit_softmax_temperature(num_moves, training_steps):
        if training_steps < 500:
            return 4
        elif training_steps < 1000:
            if num_moves < 100:
                return 6
            else: 
                return 5
        elif training_steps < 2000:
            return 7
        elif training_steps < 3000:
            return 8
        else:
            if num_moves < 225:
                return 9
            return 7

    return MuZeroConfig(
        game=SuperMarioBros,
        nb_epochs=200,
        network_args={'action_size': 12,
                      'state_size':  (96,96,64),
                      'representation_size': 256,
                      'max_value': 127},
        network=SuperMarioBrosNetwork,
        action_space_size=12,
        max_moves=550,
        discount=0.9,
        batch_size=128,
        td_steps=10,
        visit_softmax_temperature_fn=visit_softmax_temperature,
        lr=0.0002,
        network_path = r'D:/SuperMarioBrosAI/Networks',
        memory_path = r'D:/SuperMarioBrosAI/Memories',
        )