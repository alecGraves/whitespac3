'''This file is to test the whitespace and translator objects'''
import os
import whitespac3 as w
#char to int use ord('c')
#int to char use 
output = open("output.txt", 'w')
output.truncate()

s = w.Translator()

s.printstr("Hello, World!\n")
loc = s.alloc(1)
loc2 = s.alloc(1)
s.push(loc)
s.push(loc2)
s.charin()
s.charin()
s.retrieve(loc)
s.printchar()
s.retrieve(loc2)
s.printchar()
s.exit()

output.write(s.string)

output.close()


os.system("python whitespace.py output.txt")
