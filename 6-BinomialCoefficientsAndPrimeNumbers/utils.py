def pascalTriangle(N):
    triangle = [[1]]
    for iRow in range(1, N+1):
        triangle.append([1]+[first+second for first, second in zip(triangle[-1][:], triangle[-1][1:])]+[1])
    return triangle

def getPrimes(N):
    isPrime = [False, False] + [True] * (N-1)
    primes = []

    for p in range(2, N+1, 1):
        if isPrime[p]:
            primes.append(p)
            for mul in range(p**2, N+1, p):
                isPrime[mul] = False

    return isPrime, primes

def pgcd(x,y):
    return x if y==0 else pgcd(y, x%y)

def pgcdOfList(L):
    divisor = L[0]
    for element in L[1:]:
        divisor = pgcd(divisor, element)
        if divisor == 1: # On arrive au fond
            return divisor
    return divisor

def research(N=100):
    T = pascalTriangle(N)
    isPrime, primes = getPrimes(N)
    print(f"n\tPGCD((k parmi n))\tis n a prime ?")
    for n,row in enumerate(T[2:],2):
        # print(f"{n}\t{row}\t{pgcdOfList(row[1:-1])}")
        print(f"{n}\t{pgcdOfList(row[1:-1])}\t{isPrime[n]}")

if __name__ == '__main__':
    research()