import csv
import codecs


csvFile = open('movies.csv', 'r')
reader = csv.reader(csvFile, delimiter=',', quotechar='"')

f = open('years.csv', 'w')
csvHead = 'movieId,year\n'

f.write(csvHead)
firstPass = False


counter = -1
for row in reader:
    counter += 1
    movie = row[1]
    year = row[1][len(movie)-6:len(movie)]
    parseMovie = row[1][:len(movie)-7]
    
    parseYear = year.strip('(')
    parseYear = parseYear.strip(' ')
    parseYear = parseYear.strip(')')
    
    if '(' not in year and ')' not in year:
        parseMovie = movie
        parseYear = 'N/A'
    
    if not firstPass:
        firstPass = True
    else:
        line = str(counter) + ',' + parseYear + '\n'
        f.write(line)
    
            
