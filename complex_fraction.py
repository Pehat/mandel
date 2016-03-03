from fractions import Fraction

class ComplexFraction(object):
    def __init__(self, re=Fraction(), im=Fraction()):
        self.re = re
        self.im = im
        
    def __iadd__(self, other):
        self.re += other.re
        self.im += other.im
        return self
            
    def __add__(self, other):
        return ComplexFraction(self.re + other.re, self.im + other.im)
        
    def __imul__(self, other):
        re = self.re * other.re - self.im * other.im
        im = self.re * other.im + self.im * other.re
        self.re = re
        self.im = im
        return self
            
    def __mul__(self, other):
        re = self.re * other.re - self.im * other.im
        im = self.re * other.im + self.im * other.re
        return ComplexFraction(re, im)
    
    def __pow__(self, x):
        result = ComplexFraction(1, 1)
        while x:
            if x & 1:
                result *= self
                x -= 1
            else:
                result *= result
                x >>= 1
        return result
        
    def abs2(self):
        return self.re * self.re + self.im * self.im
        