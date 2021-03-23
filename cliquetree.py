import asyncio # for async stuff
from util import factor_marg, factor_mult

class Clique:

    def __init__(self, elements, factors, verbose=False):
        '''elements(tuple), factors is a (tuple):(list) dict.'''
        verbose and print(f'Initializing clique {elements}:')
        self.neighbors = []
        self.msgs = {} # Incoming messages will be here key is sender, value is factor
        factors = {
            elements: factor_mult(factors, elements, verbose=verbose)
        }
        self.factors = factors
        self.elements = elements

    def add_neighbor(self, clique):
        self.neighbors.append(clique)

    def get_belief(self, verbose=False):
        assert len(self.msgs)>0, "Run message passing first."
        
        factors = {s[0]:s[1][s[0]] for x, s in self.msgs.items()}
        factors.update(self.factors)
        return {self.elements: factor_mult(factors, self.elements, verbose=verbose)}

    def __msg(self, sender, verbose=False):
        self.msgs.update(sender)
        verbose and print(f'message! from: {sender.keys()}, to: {self.elements}')

    def send_msg(self, verbose=False):
        return asyncio.gather(*[self.__single_msg(n, verbose=verbose) for n in self.neighbors])

    async def __single_msg(self, target, verbose=False): # The message passing is done here
        verbose and print(f'starting {self.elements} -> {target.elements}')
        while True:
            verbose and print(f'cur msgs for {self.elements}: {self.msgs}')
            waiting_for = [x for x in self.neighbors if x!=target and x.elements not in self.msgs]
            if len(waiting_for) > 0: # Wait for incoming
                verbose and print(f'{self.elements} waiting for {waiting_for[0].elements}')
                await asyncio.sleep(0)
            else: # Send message, msg format: {sender: (sepset, factor)}
                sepset = tuple(set(self.elements).intersection(target.elements))

                factors = {}
                for x, s in self.msgs.items():
                    if x!=target.elements:
                        factors.update(s[1])
                factors.update(self.factors)

                verbose and print(f'multiplying factors: {factors}')
                factors = {self.elements: factor_mult(factors, self.elements, verbose=verbose)}
                verbose and print(f'marginalizing factor {factors} over sepset {sepset}')
                factors = {sepset: factor_marg(factors, sepset, verbose=verbose)}

                target.__msg({self.elements: (sepset, factors)}, verbose=verbose)
                break

    def __str__(self):
        return "Clique{{ {}: {}, neighbors: {} }}".format(str(self.elements), str(self.factors), ','.join(str(x.elements) for x in self.neighbors))

class CTree:
    # it works more like CLine
    def __init__(self, factors, tree, verbose=False):

        tree = [set(map(int, x.strip('][ ').split(','))) for x in tree.split('-')]
        f_connections = factors.keys()

        self.cliques = []
        self.__msgpassed = False
        for clique in tree:
            verbose and print(f'Clique: {clique}')
            clique_factors = {}
            for a, b in f_connections:
                if a in clique and b in clique:
                    clique_factors[(a,b)] = factors[(a,b)]
            verbose and print(f'Includes factors: {clique_factors}')
            self.cliques.append(Clique(tuple(clique), clique_factors, verbose=verbose))
        
        # add neighbors
        for i, clique in enumerate(self.cliques):
            if i == 0 and len(self.cliques) > 1:
                clique.add_neighbor(self.cliques[i+1])
            elif i == len(self.cliques) - 1:
                clique.add_neighbor(self.cliques[i-1])
            else:
                clique.add_neighbor(self.cliques[i-1])
                clique.add_neighbor(self.cliques[i+1])

    async def pass_messages(self, verbose=False):
        await asyncio.wait([c.send_msg(verbose=verbose) for c in self.cliques])
        self.__msgpassed = True # this should set it to true only after all messages are passed

    def calculate_beliefs(self, verbose=False):
        assert self.__msgpassed==True, "Run message passing first!"
        verbose and print('Calculating beliefs:')
        # clique beliefs
        c_beliefs = {}
        for i in self.cliques:
            c_beliefs.update(i.get_belief(verbose=verbose))

        # sepset beliefs
        s_beliefs = {}
        for i in self.cliques:
            for n in i.neighbors:
                sepset = tuple(set(i.elements).intersection(n.elements))
                if sepset not in s_beliefs:
                    s_beliefs.update({sepset: factor_marg({i.elements: c_beliefs[i.elements]}, sepset, verbose=verbose)})

        return c_beliefs, s_beliefs

    def __str__(self):
        return ','.join(str(x) for x in self.cliques)