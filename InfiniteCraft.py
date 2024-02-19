#imports
from sklearn.preprocessing import LabelEncoder # For element id to element conversions
import pickle # For importing encodings
from math import log # Used in debug statements
from time import time,sleep # Used for timing debug statements
import collections # Used to compare states


hell = Exception # I am very funny

# Load Data from Encodings
recipieDict = dict()
#Load recipieDict
with open('recipieDict.pkl', 'rb') as f:
    recipieDict = pickle.load(f) # A dict relating an element ID to a tuple containing its elemenet ID's

#Load wordEncoder
with open('wordEncoder.pkl', 'rb') as f:
    wordEncoder = pickle.load(f) #A LabelEncoder that transforms from string element names into element ID's and visa versa

#Load orderTable
with open('ordertable.pkl', 'rb') as f:
    orderTable = pickle.load(f) #int -> int dict that converts elements to their "order" which is how many layers are required to get to them: Their DEPTH in the explore tree 

# Algorithm parts
# A state is uniquely identified by if the path to it contains the same items and need the same things(impling same recipies) 
class state:
    def __init__(self,needList,path = []):
        self.needList = needList
        self.path = path
        self.hVal = None
        
    # For debugging, it prints the needed elements and their order
    def __str__(self):
        needListList = list(self.needList)
        strList = wordEncoder.inverse_transform(needListList)
        returnme = "["
        for i in range(len(needListList)):
             returnme+=""
             returnme+=strList[i]+" ("+str(orderTable[needListList[i]])+")"
             if i != len(needListList)-1:
                 returnme+=","
        return returnme+"]"

    # We have to do a counter as path is a list and we don't care about order
    def __eq__(self, other):
        return collections.Counter(self.path) ==  collections.Counter(other.path) and self.needList == other.needList

    # These values are used to calculate h
    def dis(self):
        return len(self.path)# The time it has taken us is how long our path list is.
    # A* heuristic is the highest order of the needed elements. 
    def heuristic(self):
        maxOrder = max([orderTable[x] for x in self.needList]) # The highest order element
        return maxOrder + (sum([(1 if orderTable[x] == maxOrder else 0) for x in self.needList]))

    # This is the value of this state according to A*
    def h(self):
        if(self.hVal == None): # Single compute, as an optimisation
            self.hVal = self.dis() + self.heuristic()
        return self.hVal

# Given some desired element, what is the path from it to the starting elements?
# If verbose is on, it will every some number of seconds print some extra info for debugging
def explore(desiredElement,startingElements = ["Water","Fire","Wind","Earth"],initialPath = [],verbose = False):
    # My algorithm doesn't know how to find something it is just given, so it just throws a generic error
    if(desiredElement in startingElements):
        raise hell(str(desiredElement)+" is already in the starting elements")

    # The goal list is the list of items 
    goalList = set(wordEncoder.transform(startingElements)) # Because we explore backwards, the starting elements are our goal

    # The need list is part of the state and says which elements still need to be resolved.    
    initialNeedList = set()
    desiredElementID = wordEncoder.transform([desiredElement])[0] # We get the number form of our textual desired element
    initialNeedList.add(desiredElementID) # We need to get the desired element(in its encoded form). This is the need list for the initial state

    # We tend to start with a need list containing our desired element and a blank path
    initialState = state(initialNeedList,initialPath)

    nextStates = [] # list of all states we might want to explore
    nextStates.append(initialState) # We start ready to explore the start
    
    exploredStates = [] # append-only list of explored states(to prevent backtracking)
    exploredStates.append(initialState) # Whenever we append to next states, we must append here too

    # For debug printing. If verbose = False this does nothing
    warnExtraCounter = 10 # How many debug statements until we include our needlist in our debug statement?
    warnExtra = 0 # This variable tracks how long until we hit the warn extra counter
    warnDelay = 10 # How many seconds in between debug messages
    warnTime = time() # The start time

    stateCounter = 0 # We count how many states we have seen. We see a lot of states in most solutions.
    
    while len(nextStates) != 0:
        #  -- Update to Next State
        stateCounter+=1

        # Get the minimum state
        currentState = nextStates[0]
        minVal = currentState.h()
        for c_state in nextStates: 
            c_val = c_state.h()
            if(c_val < minVal):
                currentState = c_state
                minVal = c_val
        
        nextStates.remove(currentState) # We don't want to double look at this state
        needList = currentState.needList # Renamed for readability
        path = currentState.path # Renamed for readability

        # Do debug printing
        if(verbose):
            nowTime = time()
            if(nowTime > warnTime + warnDelay):
                warnTime = nowTime
                warnExtra += 1

                # Calculate cost metric
                summa = 0 # We think about recipies as a binary tree(they aren't) how long do we still have?
                for item in needList:
                    summa += 2**orderTable[item]# The use of exponentiation here means larger orders are seen as worse. 

                if(warnExtra >= warnExtraCounter):
                    print(stateCounter,log(summa),currentState)
                    warnExtra = 0
                else:
                    print(stateCounter,log(summa))

        # We only ever work on one element at a time from the needlist.
        # This is because the order in which we simplify elements has no effect
        # We still will find optimal solutions, but our branching factor is much less
        # We work on the element with max value, in an attempt to get to simpler elements faster. 
        element = None
        maxVal = 0
        for c_element in needList:
            if(c_element in goalList):
                continue
            if(not(c_element in recipieDict)):
                continue
            order  = orderTable[c_element]
            if(order >= maxVal):
                maxVal = order
                element = c_element    
        if(element == None):
            continue # This state is a bust, forget it

        recipies = recipieDict[element] # Get the recipies
        
        # Clean the recipie list for recipies that use banned items
        elementOrder = orderTable[element]
        recipies = filter(lambda recipie : not (orderTable[recipie[0]] >= elementOrder or orderTable[recipie[1]] >= elementOrder),recipies)
        # A big advantage of the order table is that we know the shortest path doesn't go up in order.
        # Because the element could have been crafted with just elements lesser in order. 
        
        for recipie in recipies:
            # We add a new state in which we breakdown an element with a recipie

            # Make a new need list
            newNeedList = needList.copy()
            newNeedList.remove(element)
            if(not(recipie[0] in goalList)):
                newNeedList.add(recipie[0])
            if(not(recipie[1] in goalList)):
                newNeedList.add(recipie[1])

            # Make a new path
            newPath = path.copy()
            newPath.append(recipie)

            # Combine into a new state
            newState = state(newNeedList,newPath)

            # Is this state a winner
            if(len(newNeedList) == 0): # If we need nothing, then we succeeded in crafting
                return newState.path
            
            # Check for duplicates
            # Notably, because we use the equality defined by state, states don't need to be 100% the same for them to be equal
            # They just have to make the same optimal paths. 
            failState = False;
            for c_state in exploredStates:
                if(failState):
                    continue
                if(c_state == newState):
                    failState = True
            # If there are no "duplicate" states
            if (not (failState)):
                nextStates.append(newState)
                exploredStates.append(newState)
    return [] # If we run out of states, but have not found our element(returned early) then we have failed!

if __name__ == '__main__':
    # Explore for an element
    desiredElement = input("Element name to search for:")
    elem = ""
    try:
        elem = wordEncoder.transform([desiredElement])[0]
    except ValueError:
        print("That element was not in the encoded dataset")
        raise hell("Element not in encoded dataset")

    # Print what is happening
    maxOrder = orderTable[elem]
    print("Exploring for "+desiredElement,"("+str(maxOrder)+")")

    # Run the explore
    val = explore(desiredElement,verbose = True)

    
    # Print path in a readable way.
    if(val == []): # fail case
        print("We failed to find")
    for elem in val:
        elemAsString = wordEncoder.inverse_transform([elem[0],elem[1]])
        print(elemAsString[0],"+",elemAsString[1])
    print("Done")
    sleep(60) # This sleep does nothing, I have it because I hate consoles terminals on finish
