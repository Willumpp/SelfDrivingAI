import math

'''
Stack data structure
initialisation attributes:
    max_size
private variables:
    stack []
    size int
    max_size int

public methods:
    is_empty()
    is_full()
    push(val)
    peek()
    pop()
    get_size()
'''
class Stack:
    def __init__(self, max_size):
        #Set all attributes to private using __
        #   max_size : maximum size of the stack
        #   size : the current count of items; also acts as a head pointer
        #   stack : the list holding the stack's items
        self.__max_size = max_size
        self.__size = 0
        self.__stack = []

    #Performs a check if the stack contains any items
    def is_empty(self):
        #Stack doesnt contain items if the size/head pointer is at 0
        if self.__size == 0:
            return True #return true if empty

        return False #return false if not empty

    #Performs a check if the stack has reached its size limit
    #   size limit is specified upon stack initilisation
    def is_full(self):
        #Stack has reached size limit if size equals specified maximum size
        if self.__size == self.__max_size:
            return True #return true if full

        return False #return false if not full

    #Adds an item to the end of the list
    #   acts as pushing to the stack
    #given item can be of any data type
    def push(self, item):
        #Perform an error test if the stack is full
        if self.is_full() == True:
            #Raise error to inform developer that the stack is full
            raise Exception("Error. Cannot perform push; stack is full")
            return -1

        #Add item to the end of the stack using "size" pointer
        #   determine to increase the size of the array using append
        #   or use the stack pointer
        if self.__size < len(self.__stack):
            self.__stack[self.__size] = item
        else:
            self.__stack.append(item)
        self.__size += 1 #Increment stack size/head pointer

    #Returns the last item on the stack without removing the item
    def peek(self):
        if self.is_empty() == True:
            #Raise error for peak in case of any unexpected results with returning a placeholder
            raise Exception("Error. Cannot perform peek; stack is empty")

        #Return "size-1" as "size" points to the next free, empty location
        return self.__stack[self.__size - 1]

    #Returns the last item on the stack, removing the item
    def pop(self):
        if self.is_empty() == True:
            #Raise error to avoid unexpected results of returning and error code
            raise Exception("Error. Cannot perform pop; stack is empty")

        #Set output to "size-1" as "size" points to the next empty, free location
        _output = self.__stack[self.__size - 1] #Get the back item
        self.__size -= 1 #Decrement stack size, deleting the previous item
        return _output

    #Get method for stack size
    def get_size(self):
        return self.__size

    #Display the stack list and size when printed
    def __repr__(self):
        return f"stack contents: {self.__stack[:self.__size]}; size : {self.__size}; list contents: {self.__stack}"

'''
Vector data structure
Stores an x and y component whilst providing some useful mathematical functions
Methods:
    get_pos() : Returns the x and y of the vector as a tuple
    get_mag() : Calculates and returns the magnitude of the vector
    set_pos(x, y) : Set the x and y coordinate of the vector
    normalised() : Returns the direction of the vector
    dot(inp) : Returns the dot product of the given vector
    dir(inp) : Calculates the angle between two vectors
'''
class Vector:
    #x and y are public as methods should calculate using the x and y every time they are called
    #   this means x and y are freely changeable
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #Returns a tuple containing the x and y component of the vector
    def get_pos(self):
        return (self.x, self.y)

    #Returns the magnitude of the vector
    #   Mag = sqrt(a^2 + b^2)
    def get_mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    #Set the x and y coordinate of the vector
    def set_pos(self, x, y):
        self.x = x
        self.y = y

    #Set method for x (optional)
    def set_x(self, x):
        self.x = x

    #Set method for y (optional)
    def set_y(self, y):
        self.y = y

    #Returns the normalised vector (direction)
    #   Unit vector = 1/mag * vector
    def normalised(self):
        _mag = self.get_mag()
        return Vector(self.x / _mag, self.y / _mag)

    #Returns the dot product between two vectors
    #   dot(a, b) = a.x*b.x + a.y*b.y
    def dot(self, inp):
        return inp.x * self.x + inp.y * self.y

    #Returns the angle between two vectors (in radians)
    def angle(self, inp):
        return math.acos(self.dot(inp) / (self.get_mag()*inp.get_mag()))

    #Apply matrix transformation on vector
    #   col1 = Column 1 of matrix
    #   col2 = Column 2 of matrix
    def transformation(self, col1, col2):
        return Vector(col1.x * self.x + col2.x * self.y, col1.y * self.x + col2.y * self.y)

    #Returns a printable version of the vector
    def __repr__(self):
        return f"{(self.x, self.y)}"

    #Allows adding between two vectors
    def __add__(self, inp):
        return Vector(self.x + inp.x, self.y + inp.y)

    #Allows subtraction of vectors
    def __sub__(self, inp):
        return Vector(self.x - inp.x, self.y - inp.y)

    #Version 2:
    #Allows multiplication of a constant
    def __rmul__(self, inp):
        return Vector(self.x * inp, self.y * inp)

    #Performs an integer cast on the contents of the vector
    def int(self):
        return Vector(int(self.x), int(self.y))

    #Allows to index the vector
    #   Vector[0] = x
    #   Vector[1] = y
    def __getitem__(self, indices):
        if indices == 0:
            return self.x
        elif indices == 1:
            return self.y
        else:
            raise Exception("Error; Invalid index for Vector indexing")

'''
Queue data structure
Functions as a circular queue
private attributes:
    max_size : the maximum size of the queue
    queue : the list containing the queue items
    back : the pointer at the back free location
    front: the pointer at the first item in the queue

methods:
    is_empty() : returns true/false depending on if the queue is empty
    is_full() : returns true/false depending on if the queue is full
    enqueue(item) : adds an item to the end of the queue
    dequeue() : removes an item from the front of the queue, returning the item
    head() : returns the front item of the queue, without removing the item
    get_size() : returns the current number of items in the queue
'''
class Queue:
    #max_size is the only parameter, which determines the capacity of the queue
    def __init__(self, max_size):
        self.__max_size = max_size #queue capacity
        self.__queue = [0 for i in range(max_size)] #create a list of placeholders, all zeroes
        self.__back = 0 #pointer to the next free location
        self.__front = 0 #pointer to the front item

    #Validation, checking the queue is empty
    #   makes use of the "get_size" method
    #returns true if the queue is empty
    def is_empty(self):
        if self.get_size() == 0:
            return True
        
        return False

    #Validation checking the queue is full
    #   makes use of the "get_size" method
    #returns true if the queue is full
    def is_full(self):
        if self.get_size() == self.__max_size:
            return True
        
        return False

    #Add an element to the back of the queue
    #   raises an error if the queue is full, this avoids unexpected outcomes
    #   does not return a value
    def enqueue(self, item):
        #Perform the validation check, raises an error if cannot add another item
        #   items will be overriden without this validation
        if self.is_full():
            raise Exception("Error. Cannot perform enqueue; queue is full")
        
        #Assign the new value to the queue list
        #   use back % max_size to cycle the values of the "back" pointer
        #   this enables the queue to be circular
        self.__queue[self.__back % self.__max_size] = item
        self.__back += 1 #Increment the back pointer

    #Remove an element from the front of the queue
    #   raises an error if the queue is empty, this avoids unexpected outcomes
    #   returns the front element removed
    def dequeue(self):
        #Perform the validation check, raises an error if cannot remove another item
        #   returning an error code could create unexpected outcomes in code
        if self.is_empty():
            raise Exception("Error. Cannot perfrom dequeue; queue is empty")

        #Uses front % max size to cycle the values of the "front" pointer
        #   this gives the queue a circular structure
        output = self.__queue[self.__front % self.__max_size]
        self.__front += 1
        return output

    #Returns the size of the queue
    def get_size(self):
        #Size = front pointer - back pointer
        return self.__back - self.__front

    #Returns the front item of the queue, without removing the item
    def head(self):
        #Perform validation check, raises an error if the queue is empty
        #   need to raise an error as returning an error code creates unexpected outcomes
        if self.is_empty():
            raise Exception("Error. Cannot perform head; queue is empty")
        
        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[self.__front % self.__max_size]

    #Returns the back item of the queue, without removing the item
    def tail(self):
        #Perform validation check, raises an error if the queue is empty
        #   need to raise an error as returning an error code creates unexpected outcomes
        if self.is_empty():
            raise Exception("Error. Cannot perform tail; queue is empty")

        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[(self.__back-1) % self.__max_size]

    #Resets the class
    def clear(self):
        self.__init__(self.__max_size)

    #Prints the queue list, front pointer, and back pointer
    def __repr__(self):
        return f"Queue: {self.__queue}; Front:{self.__front}; Back:{self.__back}"


'''
Priority queue
Functions like a linear queue but elements are added in order of a giver priority
Highest priority is always at the front of the queue
private attributes:
    max_size : the maximum size of the queue
    queue : the list containing the queue items
    back : the pointer at the back free location
    front: the pointer at the first item in the queue

methods:
    is_empty() : returns true/false depending on if the queue is empty
    is_full() : returns true/false depending on if the queue is full
    enqueue(item, priority) : adds an item to the end of the queue using given priority
    dequeue() : removes an item from the front of the queue, returning the item
    head() : returns the front item of the queue, without removing the item
    get_size() : returns the current number of items in the queue
'''
class PriorityQueue:
    #max_size is the only parameter, which determines the capacity of the queue
    def __init__(self, max_size):
        self.__max_size = max_size #queue capacity
        #Queue is a 2d array
        #   index 0 = data; index 1 = priority
        self.__queue = [(0, 0) for i in range(max_size)] #create a list of placeholders, all zeroes
        self.__back = 0 #pointer to the next free location
        self.__front = 0 #pointer to the front most item

    #Validation, checking the queue is empty
    #   makes use of the "get_size" method
    #returns true if the queue is empty
    def is_empty(self):
        if self.get_size() == 0:
            return True
        
        return False

    #Validation checking the queue is full
    #   makes use of the "get_size" method
    #returns true if the queue is full
    def is_full(self):
        if self.get_size() == self.__max_size:
            return True
        
        return False

    #Add an element to the back of the queue
    #   raises an error if the queue is full, this avoids unexpected outcomes
    #   does not return a value
    def enqueue(self, item, priority):
        #Perform the validation check, raises an error if cannot add another item
        #   items will be overriden without this validation
        if self.is_full():
            raise Exception("Error. Cannot perform enqueue; queue is full")
        
        #Find the location to insert new element
        #   loop through the queue list until a higher priority is met
        for index in range(self.__front, self.__back+1):

            #Priority check, if priority is now higher...
            if priority > self.__queue[index % self.__max_size][1]:
                #Shift elements accross the queue
                #   loop from back of queue to the new index
                #   shift elements one-by-one
                for index2 in range(self.__back, index, -1):
                    #Element shift
                    self.__queue[index2 % self.__max_size] = self.__queue[(index2-1) % self.__max_size]

                #Insert item
                self.__queue[index % self.__max_size] = (item, priority)

                break

        self.__back += 1

    #Remove an element from the front of the queue
    #   raises an error if the queue is empty, this avoids unexpected outcomes
    #   returns the front element removed
    def dequeue(self):
        #Perform the validation check, raises an error if cannot remove another item
        #   returning an error code could create unexpected outcomes in code
        if self.is_empty():
            raise Exception("Error. Cannot perfrom dequeue; queue is empty")

        #Uses front % max size to cycle the values of the "front" pointer
        #   this gives the queue a circular structure
        output = self.__queue[self.__front % self.__max_size]

        self.__front += 1
        return output[0]

    #Returns the size of the queue
    def get_size(self):
        #Size = front pointer - back pointer
        return self.__back - self.__front

    #Returns the front item of the queue, without removing the item
    def head(self):
        #Perform validation check, raises an error if the queue is empty
        #   need to raise an error as returning an error code creates unexpected outcomes
        if self.is_empty():
            raise Exception("Error. Cannot perform head; queue is empty")
        
        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[self.__front % self.__max_size][0] #Output data contents with index [0]

    #Prints the queue list, front pointer, and back pointer
    def __repr__(self):
        return f"Queue: {self.__queue}; Front:{self.__front}; Back:{self.__back}"

#V2
class PriorityQueue2(Queue):
    #max_size is the only parameter, which determines the capacity of the queue
    def __init__(self, max_size):
        self._Queue__max_size = max_size #queue capacity
        #Queue is a 2d array
        #   index 0 = data; index 1 = priority
        self._Queue__queue = [(0, 0) for i in range(max_size)] #create a list of placeholders, all zeroes
        self._Queue__back = 0 #pointer to the next free location
        self._Queue__front = 0 #pointer to the front most item

    #Add an element to the back of the queue
    #   raises an error if the queue is full, this avoids unexpected outcomes
    #   does not return a value
    def enqueue(self, item, priority):
        #Perform the validation check, raises an error if cannot add another item
        #   items will be overriden without this validation
        if self.is_full():
            raise Exception("Error. Cannot perform enqueue; queue is full")
        
        #Find the location to insert new element
        #   loop through the queue list until a higher priority is met
        for index in range(self._Queue__front, self._Queue__back+1):

            #Priority check, if priority is now higher...
            if priority > self._Queue__queue[index % self._Queue__max_size][1]:
                #Shift elements accross the queue
                #   loop from back of queue to the new index
                #   shift elements one-by-one
                for index2 in range(self._Queue__back, index, -1):
                    #Element shift
                    self._Queue__queue[index2 % self._Queue__max_size] = self._Queue__queue[(index2-1) % self._Queue__max_size]

                #Insert item
                self._Queue__queue[index % self._Queue__max_size] = (item, priority)

                break

        self._Queue__back += 1

    def dequeue(self):
        return super().dequeue()[0]


