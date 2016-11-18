'''This file is to test the whitespace and translator objects'''
import os
import whitespac3 as w
#char to int use ord('c')
#int to char use 
output = open("output.txt", 'w')
output.truncate()

s = w.Translator()
start = s.label()
s.push(1)
e=s.ifstate()
s.printstr("If Activated")
s.endif(e)
s.exit()

output.write(s.string)

output.close()


os.system("python whitespace.py output.txt")
