'''This file is to test the whitespace and translator objects'''
import os
import whitespac3 as w
#char to int use ord('c')
#int to char use 
output = open("output.ws", 'w')
output.truncate()

s = w.WhiteSpace()

cond = s.store(None, 3)

s.printstr("Hello!\n")
s.stringin()
s.exit()

output.write(s.string)

output.close()


os.system("python interpreter.py output.ws")
