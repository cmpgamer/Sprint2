import csv
import codecs


csvFile = open('movies.csv', 'r')
reader = csv.reader(csvFile, delimiter=',', quotechar='"')

f = open('titles.csv', 'w')
csvHead = 'movieId,title\n'

f.write(csvHead)
firstPass = False

counter = -1

for row in reader:
    movie = row[1]
    parseMovie = row[1][:len(movie)-7]
    
    counter += 1
    
    if not firstPass:
        firstPass = True
    else:
        line = str(counter) + '|' + parseMovie + '\n'
        f.write(line)
        
    
            
