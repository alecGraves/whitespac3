#!/usr/bin/python
# -*- coding: utf-8 -*-

# A Whitespace interpreter in Python with limited debugging capabilities
# By Miguel Colom
# http://mcolom.info

# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#

__author__  = '''Miguel Colom'''
__docformat__ = 'plaintext'

import optparse
import sys

G_verbose = False
G_stack = False
G_pause = False

SPACE = ord(' ')
TAB = ord('\t')
LF = ord('\n')

PARAM_NONE = 0
PARAM_NUM = 1
PARAM_LABEL = 2

# Interpreter execution-time exception
class InterpreterException(Exception):
	def __init__(self, ip, message):
		msg = "Error in ip=%d --> %s" % ((ip, message))
		Exception.__init__(self, msg)


# The instructions of the VM
instructions = {
	# Stack Manipulation (IMP: [Space])
	'PUSH': ((SPACE, SPACE), PARAM_NUM, 'Push the number onto the stack'), 
	'SDUPLI': ((SPACE, LF, SPACE), PARAM_NONE, 'Duplicate the top item on the stack'),
	'SCOPY': ((SPACE, TAB, SPACE), PARAM_NUM, 'Copy the nth item on the stack onto the top of the stack'),
	'SSWAP': ((SPACE, LF, TAB), PARAM_NONE, 'Swap the top two items on the stack'),
	'SDISCARD': ((SPACE, LF, LF), PARAM_NONE, 'Discard the top item on the stack'),
	'SSLIDE': ((SPACE, TAB, LF), PARAM_NUM, 'Slide n items off the stack, keeping the top item'),

	# Arithmetic (IMP: [Tab][Space])
	'ADD': ((TAB, SPACE, SPACE, SPACE), PARAM_NONE, 'Addition'),
	'SUB': ((TAB, SPACE, SPACE, TAB), PARAM_NONE, 'Subtraction'),
	'MUL': ((TAB, SPACE, SPACE, LF), PARAM_NONE, 'Multiplication'),
	'DIV': ((TAB, SPACE, TAB, SPACE), PARAM_NONE, 'Integer Division'),
	'MOD': ((TAB, SPACE, TAB, TAB), PARAM_NONE, 'Modulo'),

	# Heap Access (IMP: [Tab][Tab])
	'STORE': ((TAB, TAB, SPACE), PARAM_NONE, 'Store'),
	'RETRIEVE': ((TAB, TAB, TAB), PARAM_NONE, 'Retrieve'),

	# Flow Control (IMP: [LF])
	'LABEL': ((LF, SPACE, SPACE), PARAM_LABEL, 'Mark a location in the program'),
	'CALL': ((LF, SPACE, TAB), PARAM_LABEL, 'Call a subroutine'),
	'JUMP': ((LF, SPACE, LF), PARAM_LABEL, 'Jump unconditionally to a label'),
	'JUMP-ZERO': ((LF, TAB, SPACE), PARAM_LABEL, 'Jump to a label if the top of the stack is zero'),
	'JUMP-NEG': ((LF, TAB, TAB), PARAM_LABEL, 'Jump to a label if the top of the stack is negative'),
	'RETURN': ((LF, TAB, LF), PARAM_NONE, 'End of subroutine'),
	'END': ((LF, LF, LF), 0, 'End the program'),

	# I/O (IMP: [Tab][LF])
	'OUT-CHAR': ((TAB, LF, SPACE, SPACE), PARAM_NONE, 'Output the character at the top of the stack'),
	'OUT-NUM': ((TAB, LF, SPACE, TAB), PARAM_NONE, 'Output the number at the top of the stack'),
	'IN-CHAR': ((TAB, LF, TAB, SPACE), PARAM_NONE, 'Read a character and place it in the location given by the top of the stack'),
	'IN-NUM': ((TAB, LF, TAB, TAB), PARAM_NONE, 'Read a number and place it in the location given by the top of the stack')
}

# Checks if the IP points to a valid instruction
def format_compatible(format, memory, ip):
	for i in range(len(format)):
		if format[i] != memory[ip+i]:
			return False
	return True

# Returns the name of the instruction pointed by IP or '' if it's not a
# valid instruction
def identify_instruction(memory, ip):
	for name in list(instructions.keys()):
		instruction_def = instructions[name]
		format = instruction_def[0]
		#
		# Check format compatibility
		if format_compatible(format, memory, ip):
			return name
	#
	# Not found
	return ''

# Decodes the number pointed by IP
def decode_num(memory, ip):
	bits = []

	i = ip
	ch = memory[i]
	while ch != LF:
		if ch == SPACE:
			bits.append(0)
		elif ch == TAB:
			bits.append(1)
		#
		i += 1
		ch = memory[i]

	length = len(bits) + 1 # +1 because of the final LF

	number = 0
	multiplier = 1
	while len(bits) > 1:
		b = bits.pop()
		number += b * multiplier
		multiplier *= 2

	# Get sign and multiply
	sign = (+1 if bits.pop() == 0 else -1)
	number *= sign
	#
	return number, length

# Retrieves a label from the location at IP
def get_label(memory, ip):
	label = ''

	i = ip
	v = memory[i]
	
	while v != LF:
		if v == SPACE or v == TAB:
			label += chr(v)			
		#
		i += 1
		v = memory[i]

    # Add the final LF
	label += chr(v)

	length = len(label)
	return label, length

# Reads a character from stdin
def in_char():
	return sys.stdin.read(1)

# Outputs a string to stdout
def out_string(string):
	sys.stdout.write(string)

# Executes a single instruction	
def exec_instruction(name, num, label, label_length, ip, memory, stack, call_stack, labels):
	new_ip = -1
	finished = False

	# *** Stack Manipulation ***
	if name == 'PUSH':
		stack.append(num)
	elif name == 'SDUPLI':
		if len(stack) < 1:
			raise InterpreterException(ip, "SDUPLI with empty stack")
		stack.append(stack[-1])
	elif name == 'SCOPY':
		pos = len(stack)-num-1
		if pos < 0:
		  raise InterpreterException(ip, "SCOPY with negative argument")
		stack.append(stack[pos])
	elif name == 'SSWAP':
		if len(stack) < 2:
			raise InterpreterException(ip, "SSWAP with less than two elements")
		n1 = stack.pop()
		n2 = stack.pop()
		stack.append(n1)
		stack.append(n2)
	elif name == 'SDISCARD':
		if len(stack) > 0:
			stack.pop()
	elif name == 'SSLIDE':
		if len(stack) > 0:
			top = stack.pop()
			for i in range(num):
				stack.pop()
			stack.append(top) # Recover top
	#
	# *** Arithmetic ***
	elif name == 'ADD':
		stack.append(stack.pop() + stack.pop())
	elif name == 'SUB':
		if len(stack) < 2:
			raise InterpreterException(ip, "SUB with less than two elements")
		n1 = stack.pop()
		n2 = stack.pop()
		stack.append(n2 - n1)
	elif name == 'MUL':
		if len(stack) < 2:
			raise InterpreterException(ip, "MUL with less than two elements")
		stack.append(stack.pop() * stack.pop())
	elif name == 'DIV':
		if len(stack) < 2:
			raise InterpreterException(ip, "DIV with less than two elements")
		n1 = stack.pop()
		n2 = stack.pop()
		stack.append(n2 / n1)
	elif name == 'MOD':
		if len(stack) < 2:
			raise InterpreterException(ip, "MOD with less than two elements")
		n1 = stack.pop()
		n2 = stack.pop()
		stack.append(n2 % n1)
	# *** Heap Access ***
	elif name == 'STORE':
		if len(stack) < 2:
			raise InterpreterException(ip, "STORE with less than two elements")
		value = stack.pop()
		addr = stack.pop()
		memory[addr] = value
	elif name == 'RETRIEVE':
		if len(stack) < 1:
			raise InterpreterException(ip, "RETREIVE with empty stack")
		n = stack.pop()
		stack.append(memory[n])
	# *** Flow Control ***
	elif name == 'LABEL':
		labels[label] = ip + len(label)
	elif name == 'CALL':
		try:
			new_ip = labels[label]
		except KeyError:
			raise InterpreterException(ip, "Unknown label: " + 
						"{0}".format(label).replace("\t", "[Tab]").replace("\n", "[LF]").replace(" ", "[space]") +
						"\nOR calling without correct label")
		call_stack.append(ip + label_length)
	elif name == 'JUMP':
		try:
			new_ip = labels[label]
		except KeyError:
			raise InterpreterException(ip, "Unknown label: " + 
						"{0}".format(label).replace("\t", "[Tab]").replace("\n", "[LF]").replace(" ", "[space]") +
						"\nOR jumping without correct label")
	elif name == 'JUMP-ZERO':
		if len(stack) < 1:
			raise InterpreterException(ip, "JUMP-ZERO with empty stack")
		test = stack.pop()
		if test == 0:
			new_ip = labels[label]
	elif name == 'JUMP-NEG':
		if len(stack) < 1:
			raise InterpreterException(ip, "JUMP-NEG with empty stack")
		test = stack.pop()
		if test < 0:
			new_ip = labels[label]
	elif name == 'RETURN':
		if len(call_stack) < 1:
			raise InterpreterException(ip, "RETURN with empty call_stack")
		new_ip = call_stack.pop()
	elif name == 'END':
		finished = True
	# *** I/O ***
	elif name == 'OUT-NUM':
		if len(stack) < 1:
			raise InterpreterException(ip, "OUT-NUM with empty stack")
		string = '%s' % stack.pop()
		out_string(string)
	elif name == 'OUT-CHAR':
		if len(stack) < 1:
			raise InterpreterException(ip, "OUT-CHAR with empty stack")
		string = '%c' % stack.pop()
		out_string(string)
	elif name == 'IN-NUM':
		if len(stack) < 1:
			raise InterpreterException(ip, "IN-NUM with empty stack")
		is_number = False
		while not is_number:
			try:			
				string = sys.stdin.readline()
				string = string.replace('\n', '')
				number = int(string)
				is_number = True
			except ValueError:
				print ("[INTERPRETER] Please enter a number")
				is_number = False
		#
		addr = stack.pop()
		memory[addr] = number
	elif name == 'IN-CHAR':
		if len(stack) < 1:
			raise InterpreterException(ip, "IN-CHAR with empty stack")
		c = in_char()
		addr = stack.pop()
		memory[addr] = ord(c)
	#
	return new_ip, finished
	
# Prints a debug message
def print_verbose(string):
	if G_verbose:
		out_string("[INFO] " + string + "\n")

# Looks for labels and maps them with their locations
def find_and_execute_labels(labels, memory, instructions, stack, call_stack, program_length):
	ip = 0
	while ip < program_length:
		name = identify_instruction(memory, ip)
		if name == 'LABEL':
			instruction_def = instructions[name]
			addr_instr = ip
			addr_label = ip + len(instruction_def[0])
			label, length = get_label(memory, addr_label)
			if label not in labels: # Only the first is considered
				num = None
				exec_instruction(name, num, label, length, addr_label, memory, stack, call_stack, labels)
			ip = addr_instr
		#
		ip += 1

################################################################

# Parse program arguments
parser = optparse.OptionParser()
parser.add_option("-v", "--verbose",  action="store_true", default=False, help="Activate verbose mode")
parser.add_option("-s", "--stack",  action="store_true", default=False, help="Show the stack after each intruction execution")
parser.add_option("-p", "--pause",  action="store_true", default=False, help="Pause the execution after each instruction")

(opts, args) = parser.parse_args()
if len(args) != 1:
	print ("Please specify the filename of the program")
	parser.print_help()
	print()
	print ("Whitespace interpreter by Miguel Colom")
	print ("http://mcolom.perso.math.cnrs.fr/")
	sys.exit(-1)

# Read options	
G_verbose = opts.verbose
G_stack = opts.stack
G_pause = opts.pause

call_return = -1

# Memory and stacks
extra_space = 65536
stack = []
call_stack = []
labels = {}

# Read program
f = open(args[0])
text = f.read(-1)
f.close()
#
print_verbose("Program read, %d characters" % len(text))

memory = [0] * (len(text) + extra_space)

# Load program into memory
ip = 0
for c in text:
	v = ord(c)
	if v in (SPACE, TAB, LF):
		memory[ip] = v
		ip += 1
	else:
		print_verbose("Ignored colored character {0:s} at ip={1}".format(c, ip))
#
program_length = ip
print_verbose("Program loaded, %d positions in memory" % program_length)

# Look for LABEL instructions
find_and_execute_labels(labels, memory, instructions, stack, call_stack, program_length)

# Start program execution
ip = 0
print_verbose("Set ip=0 to start execution")

# Run until finished or exception
finished = False
while not finished:
	instruction_ip = ip

	# Identify instruction
	name = identify_instruction(memory, ip)
	if name != '':
		instruction_ip = ip
		instruction_def = instructions[name]

		ip += len(instruction_def[0])

		# Check parameters
		if instruction_def[1] == PARAM_NUM:
			num, length = decode_num(memory, ip)
			label = None
			print_verbose("%d\t%s %d\t;%s" % ((instruction_ip, name, num, instruction_def[2])))
		elif instruction_def[1] == PARAM_LABEL:
			label, length = get_label(memory, ip)
			num = None
			label_str = labels[label] if label in labels else "<???>"
			print_verbose("%d\t%s %s\t;%s" % ((instruction_ip, name, label_str, instruction_def[2])))
		elif instruction_def[1] == PARAM_NONE:
			num, label, length = None, None, 0
			print_verbose("%d\t%s\t;%s" % ((instruction_ip, name, instruction_def[2])))

		# Interactive mode
		if G_pause:
			is_call = (name == "CALL")
			if is_call:
				print ("[INTERPRETER] CALL instruction: press S to step-out")
			if call_return == -1 or call_return == ip:
				c = sys.stdin.read(1)				
				if is_call and (c == "s" or c == "S"): # step-out
					call_return = ip + length
					print(("call return: " + str(call_return)))

		# Execute instruction
		new_ip, finished = exec_instruction(name, num, label, length, ip, memory, stack, call_stack, labels)

		# Print stack status before instruction execution
		if G_stack:
			print('Stack: %s' % stack)
			print('Call stack: %s' % call_stack)

		# Increment IP by the length of the parameter,
		# or set its new value if it's a jump.
		if new_ip >= 0:
			ip = new_ip
		else:
			ip += length
			
		if ip == call_return:
			print("[INTERPRETER] End of subroutine")
			call_return = -1			
	else:
		ip += 1
