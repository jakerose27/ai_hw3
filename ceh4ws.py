from negotiator_base import BaseNegotiator

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

    def initialize(self, preferences, iter_limit):
        self.preferences = preferences
        self.iter_limit = iter_limit

    # TO DO: THIS BULLSHIT
    def make_offer(self, offer):
        self.offer = offer[:]

    def receive_utility(self, utility):
        self.last_enemy_util = utility

    # A round has ended. Store the results. Increment Round Counter
    def receive_results(self, results):
        self.results[round] = results
        round += 1

