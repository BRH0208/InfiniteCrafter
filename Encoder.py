import csv
from sklearn.preprocessing import LabelEncoder
import pickle
import numpy as np
all_words = set()
allRecipies = []
recipieDict = dict()
lines = 0

# First, load and store the TSV
print("Loading CSV")
with open('InfiniteCraft.tsv', encoding="utf8") as csvfile:
    spamreader = csv.reader(csvfile, delimiter='\t') # We do tab deliniation because reciies have a lot of wierd characters, but no tabs
    for row in spamreader:
        lines+=1
        if(lines % 1000 == 0):
            print(lines)
        allRecipies.append(row)
        for word in row:
            all_words.add(word)

# Fit the encoder on all words seen
print("Word Encoding")
wordEncoder = LabelEncoder()
print(len(all_words),"words found")
wordEncoder.fit(list(all_words))
lines = 0

# Fill the recipieDict
print("Creating Recipies")
recipieEncoded = wordEncoder.transform(np.array(allRecipies).flatten()) # Encoding done in one batch for speed
val = 0 # For indexing the encoded version
for recipieRaw in allRecipies:
    lines+=1
    if(lines % 100 == 0):
        print(lines)
    # Get a tuple of the encoded strings    
    recipie = (recipieEncoded[val],recipieEncoded[val+1],recipieEncoded[val+2])
    val+=3

    # To prevent duplicates or effective duplicates, we order the strings by their encoded value. 
    if(recipie[0] > recipie[1]):
        first = recipie[0]
        second = recipie[1]
    else:
        first = recipie[1]
        second = recipie[0]
    if recipie[2] in recipieDict:
        recipieDict[recipie[2]].add( (first,second) )
    else:
        recipieDict[recipie[2]] = set([(first,second)])

# To get the order, we need to be able to combine items together which is the inverse of our normal recipie dict
print("inverting dict")
recipieDict_inv = dict()
for k, val in recipieDict.items():
    for v in val:
        recipieDict_inv[v] = k

# We make a table of the order of each element
print("Creating order table")
startingElementsStr = ["Water","Fire","Wind","Earth"]
startingElements = wordEncoder.transform(startingElementsStr)

foundSet = set()
exploreSet = set(startingElements)
nextExploreSet = set()
orderTable = dict()
order = 0
totalWords = len(all_words)
print(order,0)
while len(exploreSet) != 0:
    exploreThisItr = set(exploreSet)
    for elemA in exploreThisItr: # We combine our new elements...
        for elemB in exploreThisItr.union(foundSet): # ... With everything we know about, including the new elements ...
            #...And see what we get
            val = recipieDict_inv.get((elemA,elemB))
            # If we got nothing try the other direction we need not be picky on direction
            if val == None:
                val = recipieDict_inv.get((elemB,elemA))    

            if val != None:
                # If we got something
                if(not (val in foundSet)): # And we haven't seen it before
                    nextExploreSet.add(val) # Add it. 
    # Set the orders
    for elem in exploreSet:
        orderTable[elem] = order

    # Prepare for next iteration
    order += 1
    foundSet = foundSet.union(exploreSet)
    exploreSet = nextExploreSet
    nextExploreSet = set()

    # Debug statement
    print(order,(float(len(foundSet)))/totalWords) # For progress updates, this is out of 1 which is nice.

# Export everything with pickle
with open('ordertable.pkl', 'wb') as outfile:
    pickle.dump(orderTable, outfile)

with open('recipieDict.pkl', 'wb') as outfile:
    pickle.dump(recipieDict, outfile)

with open("wordEncoder.pkl", "wb") as outfile: 
    pickle.dump(wordEncoder,outfile)
