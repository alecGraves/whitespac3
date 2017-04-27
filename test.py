'''This file is to test the whitespace and translator objects'''
import os
import whitespac3 as w
#char to int use ord('c')
#int to char use 
output = open("output.ws", 'w')
output.truncate()

s = w.WhiteSpace()

s.store(None, 3)

label = s.loop()
s.printstr("Hello!\n")

#decriment
s.add_address(-1)

s.endloop(label)

# s.stringin()
s.exit()

output.write(s.string)

output.close()

os.system("python interpreter.py output.ws")

# os.system("python interpreter.py --verbose output.ws")
