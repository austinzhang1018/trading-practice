from scipy.stats import uniform
from math import ceil
from random import random, shuffle

class Bot:
    def __init__(self, minimum, maximum, num_total_values, sample_distribution, mean_value, bot_id):
        self.bot_id = bot_id
        self.minimum = minimum
        self.maximum = maximum
        self.num_total_values = num_total_values
        self.sample_distribution = sample_distribution
        self.mean_value = mean_value
        self.private_value = self.minimum + int(sample_distribution()*(maximum-minimum))

    def reset_values(self, minimum=None, maximum=None, sample_distribution=None, mean=None):
        if minimum is not None and maximum is not None and sample_distribution is not None and mean is not None:
            self.minimum = minimum
            self.maximum = maximum
            self.sample_distribution = sample_distribution
            self.mean_value = mean
        self.private_value = self.minimum + int(self.sample_distribution()*(self.maximum-self.minimum))

    def expected_value(self):
        return self.minimum + int(self.mean_value*(self.maximum-self.minimum))
    
    def get_estimate(self, central_values):
        num_unknown = self.num_total_values - len(central_values) - 1
        return self.expected_value() * num_unknown + sum(central_values) + self.private_value

    def strategy(self, estimate, value):
        # linear strategy with random component
        return ceil(abs(estimate-value) / (10 + int(3*random())))

    def buy_amount(self, value, central_values, quantity):
        estimate = self.get_estimate(central_values)
        if value < estimate:
            return self.strategy(estimate, value)
        return 0
    
    def sell_amount(self, value, central_values, quantity):
        estimate = self.get_estimate(central_values)
        if value > estimate:
            return self.strategy(estimate, value)
        return 0

class Game:
    def __init__(self, num_bots=3, num_rounds=5, num_central_cards=5, minimum=0, maximum=1000,  sample_distribution=uniform.rvs, mean_value=uniform.mean(), easy_mode=False):
        self.num_rounds = num_rounds
        self.num_central_cards = num_central_cards
        self.minimum = minimum
        self.maximum = maximum
        self.player = 0, 0 # value, shares
        self.sample_distribution = sample_distribution
        self.easy_mode = easy_mode
        self.bots = [   Bot(
                        minimum=minimum,
                        maximum=maximum,
                        num_total_values=1+num_bots+num_central_cards,
                        sample_distribution=sample_distribution,
                        mean_value=mean_value,
                        bot_id=bot_id
                        ) for bot_id in range(1, num_bots+1)]
    
    def play_game(self):
        print('starting new game')
        print('-----------------')
        print('total players: %d' % (1+len(self.bots)))
        print('central cards: %d' % self.num_central_cards)
        print('minimum value: %d' % self.minimum)
        print('maximum value: %d' % self.maximum)

        player_value = int(self.sample_distribution()*(self.maximum-self.minimum))
        central_values = []

        print('your secret value is %d.' % player_value)

        for game_round in range(1, self.num_rounds+1):
            print()
            print('round %d' % game_round)
            print(''.join(['-' for _ in range(6+game_round)]))
            while True:
                try:
                    bid, bid_quantity = [int(value) for value in input('Enter your bid and quantity: ').strip().split()]
                    break
                except ValueError:
                    print('Invalid format, enter bid and amount separated by a space.')
        

            while True:
                try:
                    ask, ask_quantity = [int(value) for value in input('Enter your bid and quantity: ').strip().split()]
                    break
                except ValueError:
                    print('Invalid format, enter ask and amount separated by a space.')
                    

            delta_value = 0
            delta_shares = 0

            shuffle(self.bots)            

            # get bot actions
            for bot in self.bots:
                sell_amount = bot.sell_amount(bid, central_values, bid_quantity)
                buy_amount = bot.buy_amount(ask, central_values, ask_quantity)
                if sell_amount != 0:
                    delta_shares += sell_amount
                    delta_value -= sell_amount * bid
                    print('Bot %d sold %d shares%s' % (bot.bot_id, sell_amount, (' for %d.' % (sell_amount*bid)) if self.easy_mode else '.'))
                if buy_amount != 0:
                    delta_shares -= buy_amount
                    delta_value += buy_amount * ask
                    print('Bot %s purchased %d shares%s' % (bot.bot_id, buy_amount, (' for %d.' % (buy_amount*ask)) if self.easy_mode else '.'))


            prev_value, prev_shares = self.player
            self.player = prev_value+delta_value, prev_shares+delta_shares
            value, shares = self.player
            if self.easy_mode:
                print('You have a balance of %d and %d shares.' % (value, shares))

            # next card
            card_value = self.minimum + int(self.sample_distribution()*(self.maximum-self.minimum))
            central_values.append(card_value)

            if game_round < self.num_rounds:
                if self.easy_mode:
                    print('The card values are listed below.')
                    print('\n'.join([str(value) for value in central_values]))
                else:
                    print('The next card value is %s' % card_value)
            else:
                final_value = sum(central_values) + sum(map(lambda bot: bot.private_value, self.bots)) + player_value
                print('Game over. The target value was %d.' % final_value)
                print('You ended with %d credits and %d shares with a score of %d' % (value, shares, value+shares*final_value))
    
def get_params():
    while True:
        try:
            num_bots, num_rounds, minimum, maximum = [int(param) for param in input('Type in num bots, num rounds, minimum, maximum separated by spaces: ').strip().split()]
            break
        except ValueError as err:
            print('Invalid format, each parameter is an integer.')
    
    while True:
        try:
            mode = input('Type "hard" for hard mode. Anything else for easy mode: ').strip() != 'hard'
            break
        except ValueError:
            print('Invalid format, each parameter is an integer.')
    return num_bots, num_rounds, minimum, maximum, mode

if __name__ == '__main__':
    num_bots, num_rounds, minimum, maximum, mode = get_params()
    while True:
        game = Game(num_bots, num_rounds, num_rounds, minimum, maximum, easy_mode=mode)
        game.play_game()
        mode = input('Game over. Press any key to restart, s to change game settings, and q to quit: ').strip()
        if mode == 'q':
            break
        if mode == 's':
            num_bots, num_rounds, minimum, maximum, mode = get_params()