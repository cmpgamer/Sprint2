import csv
import codecs


csvFile = open('movies.csv', 'r')
reader = csv.reader(csvFile, delimiter=',', quotechar='"')

csvFile1 = open('newRatings.csv', 'r')
reader1 = csv.reader(csvFile1, delimiter=',', quotechar='"')

csvFile2 = open('titles.csv', 'r')
reader2 = csv.reader(csvFile2, delimiter='|', quotechar='"')


f = open('ratings.csv', 'w')
firstPass = False

counter = -1

oldIDs = []
movieIDs = []

for row in reader2:
    movieIDs.append(row[0])

for row in reader:
    oldIDs.append(row[0])

dictionary = dict(zip(oldIDs, movieIDs))

#print (dictionary)
firstPass = False

csvHead = 'userId,movieId,rating\n'
f.write(csvHead)

for row in reader1:
    
    if not firstPass:
        firstPass = True
    else:
        row[1] = dictionary[row[1]]
        
        if len(row) < 3:
            continue
        
        line = row[0] + ',' + row[1] + ',' + row[2] + '\n'
        f.write(line)
