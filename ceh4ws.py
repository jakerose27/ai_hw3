from negotiator_base import BaseNegotiator
from itertools import permutations
from collections import OrderedDict

# Example negotiator implementation, which randomly chooses to accept
# an offer or return with a randomized counteroffer.
# Important things to note: We always set self.offer to be equal to whatever
# we eventually pick as our offer. This is necessary for utility computation.
# Second, note that we ensure that we never accept an offer of "None".


class Negotiator(BaseNegotiator):
    def __init__(self):
        BaseNegotiator.__init__(self)
        self.last_enemy_util = 0
        self.enemy_util = []
        self.last_util = 0
        self.results = {}
        self.round = 1
        self.first = False
        self.enemy_util_slope = []
        self.init_enemy_util = 0
        self.enemy_greed_slope = 0
        self.THRESHOLD = 0.9

    def initialize(self, preferences, iter_limit):
        self.preferences = preferences[:]
        self.iter_limit = iter_limit
        self.max_utility = self.get_utility(preferences)
        print("MAX_UTIL: {util}".format(util=self.max_utility))
        self.possibilities = self.get_possibilities(preferences)
        self.threshold_increment = (0.9-0.5)/(iter_limit - 3)

    def make_offer(self, offer):
        print("NEGOTIATION ROUND {round}".format(round=self.round))
        new_offer = ""
        if self.round == 1:
            self.first = True if (offer == None) else False
            new_offer = self.make_first_offer(offer)
        elif self.round == self.iter_limit:
            new_offer = self.make_last_offer(offer)
        elif self.round == self.iter_limit+1:
            new_offer = self.accept(offer)
        else:
            if self.worth_it(offer):
                self.offer = offer[:]
                return self.offer
            else:
                bad_offer = self.possibilities.keys().index(tuple(self.offer))
                new_offer = self.possibilities.keys()[bad_offer-1][:]

        self.offer = new_offer[:]
        print("OUR_UTIL: {util}".format(util=self.get_utility(self.offer)))
        self.round += 1
        return new_offer[:]

    def receive_utility(self, utility):
        self.last_enemy_util = utility
        self.enemy_util.append(self.last_enemy_util)
        print("ENEMY_UTIL: {util}".format(util=self.enemy_util))
        slope = 0
        if len(self.enemy_util) > 1:
            current_slope = self.enemy_util[-1] - self.enemy_util[-2]
            self.enemy_util_slope.append(current_slope)
            slope = sum(self.enemy_util_slope) / len(self.enemy_util_slope)
        elif len(self.enemy_util) == 1:
            equilibrium = float(self.last_enemy_util) / 2.0
            self.enemy_greed_slope = (-1)*(equilibrium) / self.iter_limit
            print("ENEMY GREED SLOPE: {e}".format(e=self.enemy_greed_slope))
        print("LAST SLOPE: {util}".format(util=slope))
        self.enemy_avg_slope = slope

    # A round has ended. Store the results.
    def receive_results(self, results):
        self.results[self.round] = results

    def make_first_offer(self, offer):
        if self.first:
            return self.preferences
        else:
            return self.preferences

    def make_last_offer(self, offer):
        if self.first:
            return self.preferences
        else:
            return self.preferences

    def accept(self, offer):
        if self.worth_it(offer):
            return offer
        else:
            return []

    def worth_it(self, offer):
        self.incr_threshold()
        our_util = self.get_utility(offer)
        grade = float(our_util) / float(self.max_utility)
        print("Grade: {percent}".format(percent=grade))
        print("Threshold: {thresh}".format(thresh=self.THRESHOLD))
        if grade <= self.THRESHOLD:
            return False
        else:
            return True

    def get_utility(self, offer):
        temp = self.offer[:]
        self.offer = offer[:]
        value = self.utility()
        self.offer = temp[:]
        return value

    def get_possibilities(self, preferences):
        kv_store = {}
        for p in permutations(preferences):
            kv_store[p] = self.get_utility(p)
        sorted_kv = OrderedDict(sorted(kv_store.items(), key=lambda t: t[1]))
        return sorted_kv

    def incr_threshold(self):
        print("This is within the first {percent}%".format(percent=((float)(self.round)/(float)(self.iter_limit))*100))
        if (float)(self.round)/(float)(self.iter_limit) <= .3:
            print("Not Decrementing Threshold")
            return
        else:
            print("Decrementing Threshold")
            if self.enemy_avg_slope <= self.enemy_greed_slope:
                self.THRESHOLD -= (self.threshold_increment)/2.0
            else:
                self.THRESHOLD -= self.threshold_increment