import re
import glob
import os
from termcolor import colored
import click
import sys
import codecs

blacklist = ['it of its']

def cleanText(text): 
    text = re.sub('\n', ' ', text) # replace newlines with spaces
    text = re.sub('\s+', ' ', text) # collapse whitespace
    return text

def findKJVism(text, filename, context=20): 
    matches = re.finditer(r'(\b(.+?)\b\sof\s\2s\b)', text)
    counter = 0
    for match in matches: 
        matchText = cleanText(match.group(0))
        if matchText in blacklist: # ignore blacklisted matches
            continue
        filename = os.path.basename(filename)
        contextBefore = text[match.span()[0] - context:match.span()[0]]
        contextAfter = text[match.span()[1] : match.span()[1] + context ]  
        out = filename + ": " + contextBefore + colored(matchText, 'red') + contextAfter
        out = cleanText(out) # sanitize output again
        counter += 1
        print(out, flush=True)
    if counter > 0: 
        print('%s total matches found in %s' % (counter, filename), flush=True)
    return counter


@click.command()
@click.argument('filenames', nargs=-1)
@click.option('-l', '--logfile', default='x-of-xs-log.txt', help='The name of the log file to write to.')
def cli(filenames, logfile):
    for filename in filenames: 
        with codecs.open(filename, "r",encoding='utf-8', errors='ignore') as fdata:
            text = fdata.read().lower()
        count = findKJVism(text, filename)
        # Write to log
        if count > 0: 
            line = [filename, str(count)]  
            line = ",".join(line) + '\n'
            f = open(logfile, 'a')
            f.write(line)
            f.close()

if __name__ == '__main__':
    cli()
