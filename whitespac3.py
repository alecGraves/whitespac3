class WhiteSpace(object):
    '''This class can be used to generate whitespace code'''
    def __init__(self, explain=True):
        self.string = ""
        self.explain = explain
        self.labelidx = 1
        self.store(0,1)# initialize heapidx
    def __str__(self):
        '''how to print the whitespace code'''
        return self.string
    def __add__(self, other):
        '''join together two pieces of whitespace code'''
        return self.string + other.string
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
        '''swap the top two items in the stack'''
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
    def add(self, num=None):
        '''
        Add top of stack.
        Pass in a num if you want to add
            that amount to the top of 
            the stack.
        '''
        if num is not None:
            self.push(num)
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
    def heapidx(self, n=1, leave=True):
        '''
        keeps track of current location in heap
        number stored in heap[0].

        Inputs:
        incriments heap[0] by n

        If leave:
            leave previous heapidx at the top of the stack
        '''
        self.retrieve(0)
        if leave:
            self.dupl()
        self.add(n)
        self.store(0)

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
        Returns address if used.

        Note: if you use the arguments (None, Val),
            val will be stored at the current heapidx
        '''
        if addr is not None and val is not None:
            self.push(addr)
            self.push(val)
        elif addr is None and val is not None: # get new address
            self.heapidx(1)
            self.dupl()
            self.push(val)
        elif addr is not None and val is None:
            self.push(addr)
            self.swap()
        # else: #Both are none
        #     self.retrieve(0)
        #     self.swap()
        #     self.heapidx(1)
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
    def printnum(self):
        '''output and delete number at top of stack'''
        self.iocom()
        if self.explain:
            self.write("oututput_top_num")
        self.write(" \t")
    def printchar(self, char=None):
        '''output and delete character at top of stack'''
        if char is not None:
            self.push(ord(char))
        self.iocom()
        if self.explain:
            self.write("output_top_char")
        self.write("  ")
    def printstr(self, string=None):
        '''
        Pass in a string to print it in the program

        If string not passed in, prints string from
            memory address at top of stack.
        '''
        if string is not None:
            for i in enumerate(string):
                self.printchar(i[1])
        else: pass#print string from memory
            # self.new_num(1)
            # loop_label = self.label()
            # self.swap()
            # self.dupl()
            # self.add()

            # # Incriment
            # self.dupl()
            # self.dupl()
            # self.retrieve()
            # self.add(1)
            # self.store()
            # self.jump(loop_label)
            # self.endloop(loop_label)
    def charin(self):
        '''read in a character, leave it at top of stack'''
        self.iocom()
        if self.explain:
            self.write("read_in_char")
        self.write("\t ")
    def stringin(self, endchar='\n'):
        '''
        Read in a string, leave addr in stack

        String[0]=len(String)-1
        '''
        self.heapidx(1)
        self.dupl() #duplicate string start address
        self.push(0)
        self.store()

        label = self.label()

        self.heapidx(1)# get new memory address for character
        self.dupl()
        self.charin()# save the character in the memory address
        self.retrieve()# get the new character

        #if (char != '\n'')
        self.add(-1*ord(endchar))#subtract endchar
        end = self.ifstate()

        #incriment string length
        self.dupl()#duplicate string start address
        self.dupl()
        self.retrieve() #retrieve length of string (first member of the string)
        self.add(1) #incriment
        self.store()

        #repeat
        self.jump(label)
        self.endif(end)
        self.heapidx(-1, False)# 'deallocate' the endchar

    def numin(self):
        '''read in a number'''
        self.iocom()
        if self.explain:
            self.write("read_in_num")
        self.write("\t\t")

#Loops
    def loop(self):
        '''
        Starts a while loop.

        Push a condition address to the stack then run this.

        Continues until value in condition address value is zero.
        '''
        start_label = self.label()
        self.labelidx += 1
        self.dupl()
        self.retrieve()
        self.jumpzer(start_label+1)
        return start_label

    def endloop(self, start_label):
        '''Ends a while loop'''
        self.jump(start_label)
        self.label(start_label+1)

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

    def compare(self, comparison="=="):
        """
        Inputs: Eats the top 2 in the stack.

        comparison: defaults to vars are equal.
        options: "==", '>' , '<', '>=' or '<='

        Outputs:

        var1 'comparison' var2

        pushes 0 to top of stack if false,
        pushes 1 if true

        example usage:

        push(var1)

        push(var2)

        compare(">=") # var1 >= Var2?
        """
        self.labelidx += 3
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

# Special
    def add_address(self, n):
        '''incriments/decriments value in address at top of stack'''
        self.dupl()
        self.dupl()
        self.retrieve()
        self.add(n)
        self.store()
    def new_num(self, initializer=0):
        '''adds a number to the heap. leaves the address in the stack.'''
        self.heapidx(1)
        self.dupl()
        self.push(initializer)
        self.store()
