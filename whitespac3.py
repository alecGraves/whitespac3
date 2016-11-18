
'''This module is used to generate WhiteSpace code.'''
class WhiteSpace(object):
    '''This class can be used to generate whitespace code'''
    def __init__(self, explain=True):
        self.string = ""
        self.explain = explain
        self.labelidx = 0
        self.heapidx = 0
    def __str__(self):
        '''how to print the object the whitespace code'''
        return self.string
    def __add__(self, other):
        '''join together two pieces of whitespace code'''
        return self.string.replace("\n\n\n", "") + other.string
    def number(self, num):
        '''
        add a number to the code
        Many commands require numbers or labels as parameters. Numbers
            can be any number of bits wide, and are simply represented as
            a series of [Space] and [Tab],terminated by a [LF].
        [Space] represents the binary digit 0, [Tab] represents 1.
        The sign of a number is given by its first character,
            [Space] for positive and [Tab] for negative.
        Note that this is not twos complement, it just indicates a sign.
        Labels are simply [LF] terminated lists of spaces and tabs.
        There is only one global namespace so all labels must be unique.
        '''
        numstr = ''
        if self.explain:
            numstr += 'num_{0}'.format(num)
        if num > 0:
            numstr += ' '
        else:
            numstr += '\t'
        numstr += str(bin(num))[2:].replace('0', ' ').replace('1', '\t').replace('b', '') + '\n'
        return numstr
    def write(self, string):
        '''add new item to the whitespace program'''
        self.string += string

#Stack manipulation commands:
    def stack_manip(self):
        '''Instruction modification parameter (IMP) stack manipulation'''
        if self.explain:
            self.write("IMP:stack_manip")
        self.write(" ")
    def push(self, num):
        '''push a num to the stack'''
        self.stack_manip()
        if self.explain:
            self.write("push")
        self.write(" " + self.number(num))
    def dupl(self):
        '''duplicate the top item on the stack'''
        self.stack_manip()
        if self.explain:
            self.write("dupliate_top")
        self.write("\n ")
    def swap(self):
        '''swap the top swo items in the stack'''
        self.stack_manip()
        if self.explain:
            self.write("swap_top_two")
        self.write("\n\t")
    def delete(self):
        '''discard the top item int the swap'''
        self.stack_manip()
        if self.explain:
            self.write("discard_top")
        self.write("\n\n")

#Arithmetic commands:
    def arith(self):
        '''
        IMP: Arithmetic
        Arithmetic commands operate on the top two items on the stack,
        and replace them with the result of the operation.
        The first item pushed is considered to be left of the operator.
        '''
        if self.explain:
            self.write("IMP:arithmetic")
        self.write("\t ")
    def add(self):
        '''add top of stack'''
        self.arith()
        if self.explain:
            self.write("add")
        self.write("  ")
    def sub(self):
        '''
        subtract top of stack
        The first item pushed is considered to be left of the operator.
        '''
        self.arith()
        if self.explain:
            self.write("sub")
        self.write(" \t")
    def mult(self):
        '''mult top of stack'''
        self.arith()
        if self.explain:
            self.write("mult")
        self.write(" \n")
    def div(self):
        '''
        intiger division on top of stack
        The first item pushed is considered to be left of the operator.
        '''
        self.arith()
        if self.explain:
            self.write("div")
        self.write("\t ")
    def mod(self):
        '''
        modulo on top of stack
        The first item pushed is considered to be left of the operator.
        '''
        self.arith()
        if self.explain:
            self.write("mod")
        self.write("\t\t")

# Heap access commands:
    def heap(self):
        '''
        IMP: Heap Access
        Heap access commands look at the stack to find the
        address of items to be stored or retrieved. To store
        an item, push the address then the value and run the store command.
        To retrieve an item, push the address and run the retrieve command,
        which will place the value stored in the location
        at the top of the stack.
        '''
        if self.explain:
            self.write("heap_access")
        self.write("\t\t")
    def store(self, addr=None, val=None):
        '''
        Push an address then a val and run this command to store it,
            or use the arguements.
        Returns address if used
        Note: if you use the arguments (None, Val),
            val will be stored at the heapidx (starts at 1k)
        More intelligent memory management may be added in the future.
        '''
        if addr is not None and val is not None:
            self.push(addr)
            self.push(val)
        elif addr is None and val is not None:
            addr = self.heapidx
            self.push(addr)
            self.push(val)
            self.heapidx += 1
        elif addr is not None and val is None:
            self.push(addr)
            self.swap()
        else:
            addr = self.heapidx
            self.push(addr)
            self.swap()
            self.heapidx += 1
        self.heap()
        if self.explain:
            self.write("store")
        self.write(" ")
        if addr is not None:
            return addr
    def retrieve(self, addr=None):
        '''
        push an address then run this command,
        and the val in the address will be pushed to the stack.
        '''
        if addr != None:
            self.push(addr)
        self.heap()
        if self.explain:
            self.write("retrieve")
        self.write("\t")
    def alloc(self, length):
        '''Allocate a length of memory from the heap'''
        self.heapidx += length
        location = self.heapidx - length
        return location

# Flow Control
    def flow(self):
        '''
        IMP: Flow Control
        Flow control operations are also common.
        Subroutines are marked by labels, as well as the targets
            of conditional and unconditional jumps,
            by which loops can be implemented.
        Programs must be ended by means of [LF][LF][LF]
            so that the interpreter can exit cleanly.
        '''
        if self.explain:
            self.write("IMP:Flow_Control")
        self.write("\n")
    def label(self, label=None):
        '''Mark a location in the program, returns the value'''
        self.flow()
        if self.explain:
            self.write("add_label")
        if label is None:
            label = self.labelidx
            self.write("  " + self.number(label))
            self.labelidx += 1
        else:
            self.write("  " + self.number(label))
        return label
    def subr(self, label):
        '''Call a subroutine in the program'''
        self.flow()
        if self.explain:
            self.write("call_subroutine")
        self.write(" \t" + self.number(label))
    def jump(self, label):
        '''jump to a label unconditionally'''
        self.flow()
        if self.explain:
            self.write("jump_to_")
        self.write(" \n" + self.number(label))
    def jumpzer(self, label):
        '''jump to a label if the top of the stack is 0'''
        self.flow()
        if self.explain:
            self.write("jump_to_if_top_zer")
        self.write("\t " + self.number(label))
    def jumpneg(self, label):
        '''jump to a label if the top of the stack is negative'''
        self.flow()
        if self.explain:
            self.write("jump_to_if_top_neg")
        self.write("\t\t" + self.number(label))
    def endsub(self):
        '''end subroutine and return control to the caller'''
        self.flow()
        if self.explain:
            self.write("break_subroutine")
        self.write("\t\n")
    def exit(self):
        '''jump to a label if the top of the stack is negative'''
        self.flow()
        if self.explain:
            self.write("exit_pgrm")
        self.write("\n\n")

# Serial com commands
    def iocom(self):
        '''
        IMP: Serial Commands
        There are IO instructions for reading and writing numbers
            and individual characters.
        With these, string manipulation routines can be written.
        The read instructions take the heap address in which to store
            the result from the top of the stack.
        '''
        if self.explain:
            self.write("IMP:I/O")
        self.write("\t\n")
    def printchar(self, char=None):
        '''output and delete character at top of stack'''
        if char is not None:
            self.push(ord(char))
        self.iocom()
        if self.explain:
            self.write("output_top_char")
        self.write("  ")
    def printstr(self, string):
        '''Print a string'''
        for i in enumerate(string):
            self.printchar(i[1])
    def printnum(self):
        '''output and delete number at top of stack'''
        self.iocom()
        if self.explain:
            self.write("oututput_top_num")
        self.write(" \t")
    def charin(self):
        '''read in a character'''
        self.iocom()
        if self.explain:
            self.write("read_in_char")
        self.write("\t ")
    def stringin(self):
        '''Read in a string'''
        strlen_addr = self.store(None, 0)
        string_addr = self.alloc(100)
        linefeed = ord("\n")
        condition_addr = self.store(None, 0)

        dostart, condition_addr = self.doloop(condition_addr)
        self.store(condition_addr, 1)
        self.push(string_addr)
        self.retrieve(strlen_addr)
        self.add()
        self.charin()
        self.retrieve(strlen_addr)
        self.push(1)
        self.add()
        self.store(strlen_addr)

        self.push(string_addr)
        self.retrieve(strlen_addr)
        self.add()
        self.retrieve()
        self.dupl()
        self.printnum()
        self.push(linefeed)
        self.sub()

        self.jumpzer(self.labelidx)
        self.store(condition_addr, 0)
        self.label()

        self.enddoloop(dostart, condition_addr)

        return strlen_addr, string_addr
    def numin(self):
        '''read in a number'''
        self.iocom()
        if self.explain:
            self.write("read_in_num")
        self.write("\t\t")

#Loops
    def doloop(self, conditionloc):
        '''
        start a do loop.
        Continues until value in conditionloc is nonzero.
        '''
        label = self.label()
        return label, conditionloc
    def enddoloop(self, label, conditionloc):
        '''end a do loop'''
        self.retrieve(conditionloc)
        self.jumpzer(label)

    def loop(self, repetitions):
        '''
        Starts a generic loop, returns args for endloop()
        Args: repetitions
        Returns: loop_label, iterator_location
        '''
        iterator = self.store(None, -1*repetitions)
        label = self.label()
        return label, iterator
    def endloop(self, label, iterator):
        '''Ends a generic loop loop'''
        self.retrieve(iterator)
        self.push(1)
        self.add()
        self.dupl()
        self.store(iterator)
        self.jumpneg(label)
# Logic
    def ifstate(self):
        """
        Starts an if statement.
        wrapped code executes if top of stack is not 0
        (eats top of stack)
        RETURNS arg for endif
        """
        end_label = self.labelidx
        self.labelidx += 1
        self.jumpzer(end_label)
        return end_label
    def endif(self, end_label):
        '''easily end if statement'''
        self.label(end_label)

    def compare(self, var1_address, comparison, var2_address):
        """
        first arg is on left.
        defaults to vars are equal
        '>' for greater, '<' for lessthan
        pushes 0 to top of stack if false,
        pushes 1 if true
        """
        self.labelidx += 3
        self.retrieve(var1_address)
        self.retrieve(var2_address)
        if comparison == '=' or comparison == '==':
            self.sub()
            self.jumpzer(self.labelidx-3)
            self.jump(self.labelidx-2)
        elif comparison == '<':
            self.sub()
            self.jumpneg(self.labelidx-3)
            self.jump(self.labelidx-2)
        elif comparison == '<=':
            self.sub()
            self.dupl()
            self.jumpneg(self.labelidx-3)
            self.jumpzer(self.labelidx-3)
            self.jump(self.labelidx-2)
        elif comparison == '>':
            self.swap()
            self.sub()
            self.jumpneg(self.labelidx-3)
            self.jump(self.labelidx-2)
        elif comparison == '>=':
            self.swap()
            self.sub()
            self.dupl()
            self.jumpneg(self.labelidx-3)
            self.jumpzer(self.labelidx-3)
            self.jump(self.labelidx-2)

        self.label(self.labelidx-3)
        self.push(1)
        self.jump(self.labelidx-1)

        self.label(self.labelidx-2)
        self.push(0)

        self.label(self.labelidx-1)

class Translator(WhiteSpace):
    '''
    This class can be used to translate basic python code into WhiteSpace code
    '''
    def __init__(self, explain=True):
        WhiteSpace.__init__(self, explain)
