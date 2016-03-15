import csv
import codecs


csvFile = open('movies.csv', 'r')
reader = csv.reader(csvFile, delimiter=',', quotechar='"')

f = open('genres.csv', 'w')
g = open('genres.txt', 'w')
csvHead = 'movieId,genre\n'

f.write(csvHead)
firstPass = False

listOfGenres = []


for row in reader:
    genres = row[2].split('|')
    for genre in genres:
        
        if not firstPass:
            firstPass = True
        else:
            if genre not in listOfGenres:
                listOfGenres.append(genre)
                
            line = row[0] + ',' + genre + '\n'
            f.write(line)

listOfGenres.sort()
            
for genre in listOfGenres:
    g.write(genre+'\n')