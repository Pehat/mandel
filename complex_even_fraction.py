class EvenFraction(object):
    def __init__(self, n=0, logd=0):
        self.n = n
        self.logd = logd
        
    def __imul__(self, other):
        self.n *= other.n
        self.logd += other.logd
        return self
        
    def __mul__(self, other):
        n = self.n * other.n
        logd = self.logd + other.logd
        return EvenFraction(n, logd)
        
    def __iadd__(self, other):
        n = (self.n << other.logd) + (other.n << self.logd)
        logd = other.logd + self.logd
        while not(n & 1) and (logd):
            n >>= 1
            logd -= 1
        self.n = n
        self.logd = logd
        return self
        
    def __add__(self, other):
        n = (self.n << other.logd) + (other.n << self.logd)
        logd = other.logd + self.logd
        while not(n & 1) and (logd):
            n >>= 1
            logd -= 1
        return EvenFraction(n, logd)
        
    def __isub__(self, other):
        n = (self.n << other.logd) - (other.n << self.logd)
        logd = other.logd + self.logd
        while not(n & 1) and (logd):
            n >>= 1
            logd -= 1
        self.n = n
        self.logd = logd
        return self
        
    def __sub__(self, other):
        n = (self.n << other.logd) - (other.n << self.logd)
        logd = other.logd + self.logd
        while not(n & 1) and (logd):
            n >>= 1
            logd -= 1
        return EvenFraction(n, logd)
        
        
class ComplexEvenFraction(object):
    def __init__(self, re=EvenFraction(), im=EvenFraction()):
        self.re = re
        self.im = im
        
    def __iadd__(self, other):
        self.re += other.re
        self.im += other.im
        return self
            
    def __add__(self, other):
        return ComplexEvenFraction(self.re + other.re, self.im + other.im)
        
    def __imul__(self, other):
        re = self.re * other.re - self.im * other.im
        im = self.re * other.im + self.im * other.re
        self.re = re
        self.im = im
        return self
            
    def __mul__(self, other):
        re = self.re * other.re - self.im * other.im
        im = self.re * other.im + self.im * other.re
        return ComplexEvenFraction(re, im)
    
    def __pow__(self, x):
        result = ComplexEvenFraction(1, 1)
        while x:
            if x & 1:
                result *= self
                x -= 1
            else:
                result *= result
                x >>= 1
        return result
        
    def in4(self):
        abs2 = self.re * self.re + self.im * self.im
        return abs2.n < (1 << (abs2.logd + 2))
        