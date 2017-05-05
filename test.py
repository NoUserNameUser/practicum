'''
Created on May 3, 2017

@author: findj
'''

def multiply(num):
    total = 0
    while num > 0:
        total += num * num
        num -= 1
    return total

print multiply(54651045)