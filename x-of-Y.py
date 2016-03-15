import re
import glob
import os
from termcolor import colored
import click
import sys
import nltk

blacklist = []

def cleanText(text): 
    text = re.sub('\n', ' ', text) # replace newlines with spaces
    text = re.sub('\s+', ' ', text) # collapse whitespace
    return text

def getContext(match, text, context): 
    """ 
    Gets context for a match. Context of 20 will return 
    20 characters before and 20 characters after a match.
    """ 
    matchText = cleanText(match.group(0)) # Some matches happen across newlines
    contextBefore = text[match.span()[0] - context:match.span()[0]]
    contextAfter = text[match.span()[1] : match.span()[1] + context ]  
    return contextBefore, matchText, contextAfter

def findKJVism(text, filename, context=20): 
    matches = re.finditer(r'\w+\sof\s[A-Z][a-z]+', text)
    # TODO: do POS tagging and get nouns for the first word
    counter = 0
    tokenizer = nltk.RegexpTokenizer('[a-zA-Z]\w+\'?\w*') # A custom regex tokenizer. 
    for match in matches: 
        contextBefore, matchText, contextAfter = getContext(match, text, context)
        if matchText in blacklist: # ignore blacklisted matches
            continue
        filename = os.path.basename(filename)

        # Do some POS tagging. 
        moreBefore, moreText, moreAfter = getContext(match, text, context+30) # Get more context for POS tagging. 
        line = moreBefore + moreText + moreAfter
        tokens = tokenizer.tokenize(line)
        pos = nltk.pos_tag(tokens)
        posDict = dict(pos) # put it in a dictionary so we can look it up

        matchTokens = tokenizer.tokenize(matchText)
        firstWordPOS = posDict[matchTokens[0]][0]
        if firstWordPOS is not 'N': 
            continue

        out = filename + ": " + contextBefore + colored(matchText, 'red') + contextAfter
        out = cleanText(out) # sanitize output again
        counter += 1
        print(out, flush=True)
    if counter > 0: 
        print('%s total matches found in %s' % (counter, filename), flush=True)
    return counter


@click.command()
@click.argument('filenames', nargs=-1)
@click.option('-l', '--logfile', default='x-of-Y-log.txt', help='The name of the log file to write to.')
def cli(filenames, logfile):
    for filename in filenames: 
        text = open(filename).read()
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

