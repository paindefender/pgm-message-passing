def bitlist2int(bitlist):
    '''converts [1,0,1] to 5 and more'''
    n = 0
    for bit in bitlist:
        n = (n << 1) | bit
    return n

def int2bitlist(number, n_max):
    ''' converts 5 to [1,0,1] and more,
    
        n_max is the max number representible by the bitlist of resulting size, if its high bitlist will be longer.
    '''
    return [number >> i & 1 for i in reversed(range(n_max))]

def factor_mult(factors, target, verbose=False):
    '''target must be tuple'''
    multipliers = factors.keys()
    index_maps = [tuple(target.index(f) for f in m) for m in multipliers] # Map to bits of the initial arrays
    result = [1] * 2**len(target)

    for index in range(2**len(target)):
        bits = int2bitlist(index, len(target)) # get bits of index to product
        verbose and print(f'{" ".join(f"{x[0]}^{x[1]}" for x in zip(target,bits))}, index: {index}', end=', val=')
        for i, f in enumerate(index_maps):
            bitlist = [bits[x] for x in f] # bits of index to multiplicand
            f_index = bitlist2int(bitlist)
            verbose and print(factors[list(multipliers)[i]][f_index], end = 'x')
            result[index] *= factors[list(multipliers)[i]][f_index]
        verbose and print("\b ")   
    verbose and print(f'result: {result}')     
    return result

def factor_marg(factor, target, verbose=False):
    '''target must be tuple, if marginalizing down to a single element use smth like (1,)'''
    multipliers = factor.keys()
    assert len(multipliers)==1, "Can marginalize only when there is a single factor."
    for m in multipliers:
        index_map = tuple(m.index(f) for f in target)
    result = [0] * 2**len(target)
    for index, _ in enumerate(result):
        bits = int2bitlist(index, len(target)) # get bits of index to product
        template = [None] * len(m)
        for bit, value in zip(index_map, bits):
            template[bit] = value

        verbose and print(f'{" ".join(f"{x[0]}^{x[1]}" for x in zip(target,bits))}, index: {index}', end=', val=')
        to_fill = [i for i, x in enumerate(template) if x is None]
        for filling in range(2**len(to_fill)): # Iterate and sum over the template matches
            bits = int2bitlist(filling, len(to_fill))
            bitlist = template
            for bit, value in zip(to_fill, bits):
                bitlist[bit] = value
            f_index = bitlist2int(bitlist)
            verbose and print(factor[m][f_index], end = '+')
            result[index] += factor[m][f_index]
        verbose and print("\b ")
    verbose and print(f'result: {result}') 
    return result