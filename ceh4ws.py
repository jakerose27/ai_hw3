from negotiator_base import BaseNegotiator
from itertools import permutations
from collections import OrderedDict

# Example negotiator implementation, which randomly chooses to accept
# an offer or return with a randomized counteroffer.
# Important things to note: We always set self.offer to be equal to whatever
# we eventually pick as our offer. This is necessary for utility computation.
# Second, note that we ensure that we never accept an offer of "None".


class Negotiator(BaseNegotiator):
    # Override the make_offer method from BaseNegotiator to accept a given offer 5%
    # of the time, and return a random permutation the rest of the time.
    def __init__(self):
        BaseNegotiator.__init__(self)
        self.last_enemy_util = 0
        self.last_util = 0
        self.results = {}
        self.round = 1
        self.first = False

    def initialize(self, preferences, iter_limit):
        self.preferences = preferences[:]
        self.iter_limit = iter_limit
        self.max_utility = self.get_utility(preferences)
        print("MAX_UTIL: {util}".format(util=self.max_utility))
        self.possibilities = self.get_possibilities(preferences)

    # TO DO: THIS BULLSHIT
    def make_offer(self, offer):
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

    # A round has ended. Store the results. Increment Round Counter
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
        our_util = self.get_utility(offer)
        print
        diff = float(our_util) / float(self.max_utility)
        print("Diff: {diff}".format(diff=diff))

        if diff <= .5:
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