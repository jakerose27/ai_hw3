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
        self.results = {}
        self.successful_results = []
        self.best_threshold = 0.5
        self.enemy_first_offer = []
        self.enemy_avg_slope = 0
        self.enemy_greed_slope = 0
        self.last_enemy_util = 0
        self.our_last_offer = []
        self.first = False
        self.enemy_util_slope = []
        self.init_enemy_util = 0
        self.enemy_util = []
        self.last_util = 0
        self.THRESHOLD = 0.9
        self.max_utility = 0
        self.threshold_increment = 0.1
        self.offers_made = []
        self.round = 1

    def initialize(self, preferences, iter_limit):
        self.enemy_util_slope = []
        self.init_enemy_util = 0
        self.enemy_greed_slope = 0
        self.last_enemy_util = 0
        self.enemy_util = []
        self.last_util = 0
        self.our_last_offer = []
        self.enemy_first_offer = []
        self.first = False
        self.THRESHOLD = 0.9
        self.preferences = preferences[:]
        self.iter_limit = iter_limit
        self.max_utility = self.get_utility(preferences)
        # print("MAX_UTIL: {util}".format(util=self.max_utility))
        self.threshold_increment = (0.9-self.best_threshold)/(iter_limit - 3)
        self.offers_made = []
        self.round = 1

    def make_offer(self, offer):
        # print("NEGOTIATION ROUND {round}".format(round=self.round))
        if self.round == 1:
            self.our_last_offer = self.preferences[:]
            self.first = True if (offer is None) else False
            new_offer = self.make_first_offer(offer)
        elif self.round == self.iter_limit:
            new_offer = self.make_last_offer()
        elif self.round == self.iter_limit+1:
            new_offer = self.accept(offer)
        else:
            if self.round == 2:
                if self.first:
                    self.enemy_first_offer = offer[:]
            if self.worth_it(offer):
                self.offer = offer[:]
                self.our_last_offer = offer[:]
                return self.offer
            else:
                # bad_offer = self.possibilities.keys().index(tuple(self.offer))
                # new_offer = self.possibilities.keys()[bad_offer-1][:]
                new_offer = self.generate_offer()

        self.offer = new_offer[:]
        # print("OUR_UTIL: {util}".format(util=self.get_utility(self.offer)))
        self.round += 1
        self.our_last_offer = new_offer[:]
        self.offers_made.append(new_offer)
        return new_offer[:]

    def receive_utility(self, utility):
        # print("ROUND: {r}".format(r=self.round))
        if self.first:
            if self.round > self.iter_limit:
                return
        else:
            if self.round == self.iter_limit:
                return
        self.last_enemy_util = utility
        self.enemy_util.append(self.last_enemy_util)
        # print("ENEMY_UTIL: {util}".format(util=self.enemy_util))
        slope = 0
        if len(self.enemy_util) > 1:
            current_slope = self.enemy_util[-1] - self.enemy_util[-2]
            self.enemy_util_slope.append(current_slope)
            # print("All Enemy Slopes: {sls}".format(sls=self.enemy_util_slope))
            slope = float(sum(self.enemy_util_slope)) / float(len(self.enemy_util_slope))
            # print("New Average Slope: {sl}".format(sl=slope))
        elif len(self.enemy_util) == 1:
            equilibrium = float(self.last_enemy_util) / 2.0
            self.enemy_greed_slope = (-1.0) * equilibrium / self.iter_limit
            # print("ENEMY GREED SLOPE: {e}".format(e=self.enemy_greed_slope))
        self.enemy_avg_slope = slope

    def generate_offer(self):
        possibilities = self.make_possibilities(self.our_last_offer)
        max_o = []
        max_u = 0
        for p in possibilities:
            if p not in self.offers_made:
                max_o = p if self.get_utility(p) > max_u else max_o
                max_u = self.get_utility(max_o)
        return max_o

    def make_possibilities(self, the_list):
        # print("Possibilities of {the_list}".format(the_list=the_list))
        poss_list = []
        for item in the_list:
            copy1 = the_list[:]
            copy2 = the_list[:]
            index = the_list.index(item)
            if index != 0:
                removed = copy1.pop(index)
                copy1.insert(index-1, removed)
                poss_list.append(copy1)
            if index != len(the_list)-1:
                removed = copy2.pop(index)
                copy2.insert(index+1, removed)
                poss_list.append(copy2)
        return poss_list

    # A round has ended. Store the results. (Success/A Points/B Points/Rounds)
    def receive_results(self, results):
        if results[0]:
            self.successful_results.append([results, self.THRESHOLD])
        self.best_threshold = (sum([x[1] for x in self.successful_results])/len(self.successful_results)) \
            if len(self.successful_results) != 0 else 0.5
        self.best_threshold = 0.5 if self.best_threshold < 0.5 else self.best_threshold

        # print("New Final Threshold = {bt}".format(bt=self.best_threshold))

    def make_first_offer(self, offer):
        if self.first:
            return self.preferences
        else:
            self.enemy_first_offer = offer[:]
            return self.preferences

    def make_last_offer(self):
        if self.enemy_avg_slope/self.enemy_greed_slope < 0.5:
            # print("BE MEAN")
            return self.preferences
        else:
            # print("BE FAIR")
            new_offer = self.generate_offer()
            self.offer = new_offer[:]
            return new_offer[:]

    def accept(self, offer):
        if self.worth_it(offer):
            return offer
        else:
            return []

    def worth_it(self, offer):
        self.incr_threshold()
        our_util = self.get_utility(offer)
        grade = float(our_util) / float(self.max_utility)
        # print("Grade: {percent}".format(percent=grade))
        # print("Threshold: {thresh}".format(thresh=self.THRESHOLD))
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

    def incr_threshold(self):
        if float(self.round)/float(self.iter_limit) <= .3:
            # print("Not Decrementing Threshold")
            return
        else:
            # print("Decrementing Threshold")
            if self.enemy_avg_slope <= self.enemy_greed_slope:
                self.THRESHOLD -= self.threshold_increment/2.0
            else:
                self.THRESHOLD -= self.threshold_increment