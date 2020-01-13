from random import shuffle, choice
from itertools import product, repeat, chain
from enum import Enum
from typing import Iterable, Iterator, Sized, Union


# COLORS = ['red', 'yellow', 'green', 'blue']
# ALL_COLORS = COLORS + ['black']
# NUMBERS = list(range(10)) + list(range(1, 10))
# SPECIAL_CARD_TYPES = ['skip', 'reverse', '+2']
# COLOR_CARD_TYPES = NUMBERS + SPECIAL_CARD_TYPES * 2
# BLACK_CARD_TYPES = ['wildcard', '+4']
# CARD_TYPES = NUMBERS + SPECIAL_CARD_TYPES + BLACK_CARD_TYPES


class CardColor(Enum):
    ...


class NormalCardColor(CardColor):
    RED = 'red'
    YELLOW = 'yellow'
    GREEN = 'green'
    BLUE = 'blue'


class BlackCardColor(CardColor):
    BLACK = 'black'


class CardType(Enum):
    ...


class ColorCardType(CardType):
    ...


class NumberCardType(ColorCardType):
    N0 = '0'
    N1 = '1'
    N2 = '2'
    N3 = '3'
    N4 = '4'
    N5 = '5'
    N6 = '6'
    N7 = '7'
    N8 = '8'
    N9 = '9'


class SpecialCardType(ColorCardType):
    SKIP = 'skip'
    REVERSE = 'reverse'
    PLUS2 = '+2'


class BlackCardType(CardType):
    WILDCARD = 'wildcard'
    PLUS4 = '+4'


class UnoCard:
    """
    Represents a single Uno Card, given a valid color and card type.

    color: string
    card_type: string/int

    >>> card = UnoCard(CardColor.RED, CardType.N0)
    """

    def __init__(self, color: CardColor, card_type: CardType):
        UnoCard.__validate(color, card_type)
        self.color = color
        self.type = card_type
        # self.temp_color = None

    @staticmethod
    def __validate(color: CardColor, card_type: CardType) -> None:
        """
        Check the card is valid, raise exception if not.
        """
        if color not in CardColor:
            raise ValueError(f'Invalid color [{color}]!')
        if (
                (color == CardColor.BLACK and card_type not in BlackCardType) or
                (color != CardColor.BLACK and card_type not in ColorCardType)
        ):
            raise ValueError(f'Invalid card [{color} {card_type}]!')

    def __repr__(self):
        return f'<{UnoCard.__name__} object: {self.color:6} {self.type}>'

    def __str__(self):
        return f'{self.color} {self.type}'

    def __eq__(self, other):
        return self.color == other.color and self.type == other.card_type

    # @property
    # def color_short(self):
    #     return self.color[0].upper()
    #
    # @property
    # def card_type_short(self):
    #     if self.card_type in ('skip', 'reverse', 'wildcard'):
    #         return self.card_type[0].upper()
    #     else:
    #         return self.card_type
    #
    # @property
    # def _color(self):
    #     return self.temp_color if self.temp_color else self.color
    #
    # @property
    # def temp_color(self):
    #     return self._temp_color
    #
    # @temp_color.setter
    # def temp_color(self, color):
    #     if color is not None:
    #         if color not in COLORS:
    #             raise ValueError('Invalid color')
    #     self._temp_color = color

    def playable(self, other: 'UnoCard') -> bool:
        """
        Return True if the other card is playable on top of this card,
        otherwise return False
        """
        return (
                self.color == other.color or
                self.type == other.type or
                other.color == 'black'
        )


class UnoPlayer:
    """
    Represents a player in an Uno game. A player is created with a list of 7
    Uno cards.

    cards: list of 7 UnoCards
    player_id: int/str (default: None)

    >>> cards = [*repeat(UnoCard(NormalCardColor.RED, NumberCardType.N0), 7)]
    >>> player = UnoPlayer(cards)
    """

    def __init__(self, cards: Iterable[UnoCard] + Sized,
                 player_id: Union[int, str] = None):
        self.hand = cards
        self.player_id = player_id

    @staticmethod
    def __validate(cards) -> None:
        card_size = len(cards)
        if card_size != 7:
            raise ValueError(f'Invalid number of cards: '
                             f'expected 7 UnoCards, '
                             f'but got [{card_size}]!')
        if not all(isinstance(card, UnoCard) for card in cards):
            raise ValueError('Invalid card types: cards must all be UnoCard objects!')
        del card_size

    def __repr__(self):
        if self.player_id is not None:
            return f'<UnoPlayer object: player id [{self.player_id}]>'
        else:
            return f'<UnoPlayer object>'

    def __str__(self):
        if self.player_id is not None:
            return f'Player {self.player_id}'
        else:
            return repr(self)

    def can_play(self, current_card) -> bool:
        """
        Return True if the player has any playable cards (on top of the current
        card provided), otherwise return False
        """
        return any(current_card.playable(card) for card in self.hand)


class UnoGame(Iterator):
    """
    Represents an Uno game.

    players: int
    random: bool (default: True)

    >>> game = UnoGame(5)
    """

    def __init__(self, players: int, random: bool = True):
        if not isinstance(players, int):
            raise ValueError('Invalid game: players must be integer')
        if not 2 <= players <= 15:
            raise ValueError('Invalid game: must be between 2 and 15 players')
        self.deck = self._create_deck(random)
        self.players = [
            UnoPlayer(self._deal_hand(), n) for n in range(players)
        ]
        self._player_cycle = ReversibleCycle(self.players)
        self._current_player = next(self._player_cycle)
        self._winner = None

    def __next__(self):
        """
        Iteration sets the current player to the next player in the cycle.
        """
        self._current_player = next(self._player_cycle)

    def _create_deck(self, random):
        """
        Return a list of the complete set of Uno Cards. If random is True, the
        deck will be shuffled, otherwise will be unshuffled.
        """
        color_cards = product(COLORS, COLOR_CARD_TYPES)
        black_cards = product(repeat('black', 4), BLACK_CARD_TYPES)
        all_cards = chain(color_cards, black_cards)
        deck = [UnoCard(color, card_type) for color, card_type in all_cards]
        if random:
            shuffle(deck)
            return deck
        else:
            return list(reversed(deck))

    def _deal_hand(self):
        """
        Return a list of 7 cards from the top of the deck, and remove these
        from the deck.
        """
        return [self.deck.pop() for i in range(7)]

    @property
    def current_card(self):
        return self.deck[-1]

    @property
    def is_active(self):
        return all(len(player.hand) > 0 for player in self.players)

    @property
    def current_player(self):
        return self._current_player

    @property
    def winner(self):
        return self._winner

    def play(self, player, card=None, new_color=None):
        """
        Process the player playing a card.

        player: int representing player index number
        card: int representing index number of card in player's hand

        It must be player's turn, and if card is given, it must be playable.
        If card is not given (None), the player picks up a card from the deck.

        If game is over, raise an exception.
        """
        if not isinstance(player, int):
            raise ValueError('Invalid player: should be the index number')
        if not 0 <= player < len(self.players):
            raise ValueError('Invalid player: index out of range')
        _player = self.players[player]
        if self.current_player != _player:
            raise ValueError('Invalid player: not their turn')
        if card is None:
            self._pick_up(_player, 1)
            next(self)
            return
        _card = _player.hand[card]
        if not self.current_card.playable(_card):
            raise ValueError(
                'Invalid card: {} not playable on {}'.format(
                    _card, self.current_card
                )
            )
        if _card.color == 'black':
            if new_color not in COLORS:
                raise ValueError(
                    'Invalid new_color: must be red, yellow, green or blue'
                )
        if not self.is_active:
            raise ValueError('Game is over')

        played_card = _player.hand.pop(card)
        self.deck.append(played_card)

        card_color = played_card.color
        card_type = played_card.card_type
        if card_color == 'black':
            self.current_card.temp_color = new_color
            if card_type == '+4':
                next(self)
                self._pick_up(self.current_player, 4)
        elif card_type == 'reverse':
            self._player_cycle.reverse()
        elif card_type == 'skip':
            next(self)
        elif card_type == '+2':
            next(self)
            self._pick_up(self.current_player, 2)

        if self.is_active:
            next(self)
        else:
            self._winner = _player
            self._print_winner()

    def _print_winner(self):
        """
        Print the winner name if available, otherwise look up the index number.
        """
        if self.winner.player_id:
            winner_name = self.winner.player_id
        else:
            winner_name = self.players.index(self.winner)
        print("Player {} wins!".format(winner_name))

    def _pick_up(self, player, n):
        """
        Take n cards from the bottom of the deck and add it to the player's
        hand.

        player: UnoPlayer
        n: int
        """
        penalty_cards = [self.deck.pop(0) for i in range(n)]
        player.hand.extend(penalty_cards)


class ReversibleCycle:
    """
    Represents an interface to an iterable which can be infinitely cycled (like
    itertools.cycle), and can be reversed.

    Starts at the first item (index 0), unless reversed before first iteration,
    in which case starts at the last item.

    iterable: any finite iterable

    >>> rc = ReversibleCycle(range(3))
    >>> next(rc)
    0
    >>> next(rc)
    1
    >>> rc.reverse()
    >>> next(rc)
    0
    >>> next(rc)
    2
    """

    def __init__(self, iterable):
        self._items = list(iterable)
        self._pos = None
        self._reverse = False

    def __next__(self):
        if self.pos is None:
            self.pos = -1 if self._reverse else 0
        else:
            self.pos = self.pos + self._delta
        return self._items[self.pos]

    @property
    def _delta(self):
        return -1 if self._reverse else 1

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value % len(self._items)

    def reverse(self):
        """
        Reverse the order of the iterable.
        """
        self._reverse = not self._reverse


class AIUnoGame:
    def __init__(self, players):
        self.game = UnoGame(players)
        self.player = choice(self.game.players)
        self.player_index = self.game.players.index(self.player)
        print('The game begins. You are Player {}.'.format(self.player_index))
        self.print_hand()
        while self.game.is_active:
            print()
            next(self)

    def __next__(self):
        game = self.game
        player = game.current_player
        player_id = player.player_id
        current_card = game.current_card
        if player == self.player:
            print('Current card: {}, color: {}'.format(
                game.current_card, game.current_card._color
            ))
            self.print_hand()
            if player.can_play(current_card):
                played = False
                while not played:
                    card_index = int(input('Which card do you want to play? '))
                    card = player.hand[card_index]
                    if not game.current_card.playable(card):
                        print('Cannot play that card')
                    else:
                        if card.color == 'black':
                            new_color = input('Which color do you want? ')
                        else:
                            new_color = None
                        game.play(player_id, card_index, new_color)
                        played = True
            else:
                print('You cannot play. You must pick up a card.')
                game.play(player_id, card=None)
                self.print_hand()
        elif player.can_play(game.current_card):
            for i, card in enumerate(player.hand):
                if game.current_card.playable(card):
                    if card.color == 'black':
                        new_color = choice(COLORS)
                    else:
                        new_color = None
                    print("Player {} played {}".format(player, card))
                    game.play(player=player_id, card=i, new_color=new_color)
                    break
        else:
            print("Player {} picked up".format(player))
            game.play(player=player_id, card=None)

    def print_hand(self):
        print('Your hand: {}'.format(
            ' '.join(str(card) for card in self.player.hand)
        ))