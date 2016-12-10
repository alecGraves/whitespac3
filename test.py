'''This file is to test the whitespace and translator objects'''
import os
import whitespac3 as w
#char to int use ord('c')
#int to char use 
output = open("output.ws", 'w')
output.truncate()

s = w.Translator()
start = s.label()
x= s.store(None, 100)
y= s.store(None, 100)
s.compare(x, '<=', y)

e=s.ifstate()
s.printstr("True")
s.jump(s.labelidx)
s.endif(e)
s.printstr("False")
s.label()
s.exit()

output.write(s.string)

output.close()


os.system("python whitespace.py output.txt")
