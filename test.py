'''This file is to test the whitespace and translator objects'''
import whitespac3 as w
#char to int use ord('c')
#int to char use 
output = open("test.txt", 'w')
output.truncate()

s = w.Translator()



s.label(0)
s.push(ord("\n"))
s.printchar()
s.push(100)
s.push(10)
s.store()
s.push(3)
s.printnum()

s.exit()

output.write(s.string)

output.close()
