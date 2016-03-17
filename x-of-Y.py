import re
import glob
import os
from termcolor import colored
import click
import sys
import nltk
import codecs


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

def findKJVism(text, filename, context=20, show=False): 
    matches = re.finditer(r"\b[A-Za-z']+\sof\s[A-Z][a-z]+", text)
    # TODO: do POS tagging and get nouns for the first word
    counter = 0
    tokenizer = nltk.RegexpTokenizer('[a-zA-Z]\w+\'?\w*') # A custom regex tokenizer. 
    for match in matches: 
        contextBefore, matchText, contextAfter = getContext(match, text, context)
        filename = os.path.basename(filename)

        # Do some POS tagging. 
        moreBefore, moreText, moreAfter = getContext(match, text, context+30) # Get more context for POS tagging. 
        line = moreBefore + moreText + moreAfter
        tokens = tokenizer.tokenize(line)
        pos = nltk.pos_tag(tokens)
        posDict = dict(pos) # put it in a dictionary so we can look it up

        matchTokens = tokenizer.tokenize(matchText)
        try: 
            firstWordPOS = posDict[matchTokens[0]][0]
        except: 
            firstWordPOS = "???" 
        if firstWordPOS is not 'N': 
            continue

        if show: 
            out = filename + ": " + contextBefore + colored(matchText, 'red') + contextAfter
            out = cleanText(out) # sanitize output again
            counter += 1
            print(out, flush=True)
    if counter > 0: 
        print('%s KJV-style possessives found in %s' % (counter, filename), flush=True)
    return counter

def findRegularPossessives(text, filename, context=20, show=False): 
    counter = 0
    matches = re.finditer(r"\b[A-Z]\w+'s\s\w+", text)
    tokenizer = nltk.RegexpTokenizer('[a-zA-Z]\w+\'?\w*') # A custom regex tokenizer. 
    for match in matches: 
        contextBefore, matchText, contextAfter = getContext(match, text, context)
        matchTokens = tokenizer.tokenize(matchText)

        # Ignore contractions. 
        contractions = ["it's", "there's", "here's"]
        if matchTokens[0].lower() in contractions: 
            continue
        
        if show: 
            out = filename + ": " + contextBefore + colored(matchText, 'red') + contextAfter
            out = cleanText(out) # sanitize output again
            counter += 1
            print(out, flush=True)
    if counter > 0: 
        print('%s regular possessives found in %s' % (counter, filename), flush=True)
    return counter

@click.command()
@click.argument('filenames', nargs=-1)
@click.option('-l', '--logfile', default='x-of-Y-log.txt', help='The name of the log file to write to.')
def cli(filenames, logfile):
    for filename in filenames: 
        f = open(filename, encoding='utf-8', errors='ignore') 
        text = f.read()
        KJVisms = findKJVism(text, filename, show=True)
        regPossessives = findRegularPossessives(text, filename, show=True)
        if KJVisms == 0 and regPossessives == 0: 
            KJVPossessiveScore = 0 # Nothing to compare. 
        elif KJVisms == 0: 
            KJVPossessiveScore = 0 # Don't try to divide zero. 
        elif regPossessives == 0: 
            KJVPossessiveScore = KJVisms
        else: 
            KJVPossessiveScore = KJVisms / regPossessives

        print('KJV Possessive Score: %s' % KJVPossessiveScore)
        # Write to log
        line = [filename, str(KJVPossessiveScore)]  
        line = ",".join(line) + '\n'
        f = open(logfile, 'a')
        f.write(line)
        f.close()

if __name__ == '__main__':
    cli()
