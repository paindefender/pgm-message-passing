import asyncio
from cliquetree import Clique, CTree

# Examples below, theyre inside coroutines because cant use await outside, can use it in a Jupyter Notebook though:

async def example_book_confusion(verbose): 
    # Confusion
    factors = {
        (0,1) : [30,5,1,10],
        (1,2) : [100,1,1,100],
        (2,3) : [1,100,100,1],
        (3,0) : [100,1,1,100]
    }

    ctree = CTree(factors,'[0,1,3] - [1,2,3]', verbose=verbose)
    await ctree.pass_messages(verbose=verbose)
    c, s = ctree.calculate_beliefs(verbose=verbose)
    print(f'Clique beliefs: {c}\nSepset beliefs: {s}')

async def example_moodle(verbose):
    factors = {
        (0,1) : [404, 331, 454, 432],
        (0,2) : [211, 215, 339, 151],
        (2,3) : [394, 206, 122, 468],
        (2,4) : [45, 401, 42, 101],
        (2,6) : [82, 187, 396, 48],
        (3,4) : [393, 168, 323, 270],
        (3,5) : [496, 262, 307, 191],
        (3,6) : [47, 200, 160, 199]
    }

    ctree = CTree(factors,'[0,1,2] - [2,3,4] - [2,3,6] - [3,5,6]', verbose=verbose)
    await ctree.pass_messages(verbose=verbose)
    c, s = ctree.calculate_beliefs(verbose=verbose)
    print(f'Clique beliefs: {c}\nSepset beliefs: {s}')

asyncio.run(example_moodle(False))
asyncio.run(example_book_confusion(True))