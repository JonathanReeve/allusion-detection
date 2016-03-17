
# coding: utf-8

import nltk
import re 
import os
import glob
import difflib 
import logging
import itertools
from nltk.util import ngrams 
from difflib import SequenceMatcher
from string import punctuation
from termcolor import colored
import click

class Text: 
    def __init__(self, filename): 
        self.filename = filename
        self.trigrams = self.ngrams(3)
        
    @property
    def text(self):
        """ Reads the file in memory. """
        f = open(self.filename, encoding='utf-8', errors='ignore')
        return f.read() 

    @property
    def tokens(self, removeStopwords=True): 
        """ Tokenizes the text, breaking it up into words, removing punctuation. """
        tokenizer = nltk.RegexpTokenizer('[a-zA-Z]\w+\'?\w*') # A custom regex tokenizer. 
        spans = list(tokenizer.span_tokenize(self.text))
        tokens = tokenizer.tokenize(self.text)
        tokens = [ token.lower() for token in tokens ] # make them lowercase
        if not removeStopwords: 
            self.spans = spans
            return tokens
        tokenSpans = list(zip(tokens, spans)) # zip it up
        stopwords = nltk.corpus.stopwords.words('english') # get stopwords
        tokenSpans = [ token for token in tokenSpans if token[0] not in stopwords ] # remove stopwords from zip
        self.spans = [ x[1] for x in tokenSpans ] # unzip; get spans
        return [ x[0] for x in tokenSpans ] # unzip; get tokens
    
    def ngrams(self, n): 
        """ Returns ngrams for the text."""
        return list(ngrams(self.tokens, n))

class Matcher: 
    def __init__(self, fileA, fileB, threshold, ngramSize):
        """
        Gets the texts from the files, tokenizes them, 
        cleans them up as necessary. 
        """
        self.threshold = threshold
        self.ngramSize = ngramSize
        
        self.textA, self.textB = Text(fileA), Text(fileB)
        
        self.textAgrams = self.textA.ngrams(ngramSize)
        self.textBgrams = self.textB.ngrams(ngramSize)

    def getContext(self, text, start, length, context): 
        match = self.getTokensText(text, start, length)
        before = self.getTokensText(text, start-context, context)
        after = self.getTokensText(text, start+length, context)
        match = colored(match, 'red')
        out = " ".join([before, match, after])
        out = out.replace('\n', ' ') # Replace newlines with spaces. 
        out = re.sub('\s+', ' ', out)
        return out

    def getTokensText(self, text, start, length):  
        """ Looks up the passage in the original text, using its spans. """
        matchTokens = text.tokens[start:start+length]
        spans = text.spans[start:start+length]
        passage = text.text[spans[0][0]:spans[-1][-1]]
        return passage 

    def getMatch(self, match, textA, textB, context): 
        wordsA = self.getContext(textA, match.a, match.size, context)
        wordsB = self.getContext(textB, match.b, match.size, context)
        line1 = ('%s: %s' % (colored(textA.filename, 'green'), wordsA) )
        line2 = ('%s: %s' % (colored(textB.filename, 'green'), wordsB) )
        return line1 + '\n' + line2

    def match(self): 
        """
        This does the main work of finding matching n-gram sequences between
        the texts.
        """
        sequence = SequenceMatcher(None,self.textAgrams,self.textBgrams)
        matchingBlocks = sequence.get_matching_blocks()

        # Only return the matching sequences that are higher than the 
        # threshold given by the user. 
        highMatchingBlocks = [match for match in matchingBlocks if match.size > self.threshold]
    
        numBlocks = len(highMatchingBlocks)
        self.numMatches = numBlocks
        
        if numBlocks > 0: 
            print('%s total matches found.' % numBlocks)

        for num, match in enumerate(highMatchingBlocks): 
            out = self.getMatch(match, self.textA, self.textB, 3)
            print('\n')
            print('match %s:' % (num+1))
            print(out)

# myMatch = Matcher('texts/milton.txt', 'texts/kjv.txt', 2, 3)
# myMatch.match()

# myMatch = Matcher('texts/yeats.txt', 'texts/kjv.txt', 2, 4)
# myMatch.match()

#maxcafe2020

def getFiles(path): 
    """ 
    Determines whether a path is a file or directory. 
    If it's a directory, it gets a list of all the text files 
    in that directory, recursively. If not, it gets the file. 
    """

    if os.path.isfile(path): 
        return [path]
    elif os.path.isdir(path): 
        # Get list of all files in dir, recursively. 
        return glob.glob(path + "/**/*.txt", recursive=True)
    else: 
        raise click.ClickException("The path %s doesn't appear to be a file or directory" % path) 


@click.command()
@click.argument('text1')
@click.argument('text2') 
@click.option('-t', '--threshold', type=int, default=2, help='The shortest length of match to include.')
@click.option('-n', '--ngrams', type=int, default=3, help='The ngram n-value to match against.')
@click.option('-l', '--logfile', default='log.txt', help='The name of the log file to write to.')
@click.option('--verbose', is_flag=True, help='Whether to enable verbose mode, giving more information.')
def cli(text1, text2, threshold, ngrams, logfile, verbose):
    """ This program finds similar text in two text files. """

    #Determine whether the given path is a file or directory. 

    texts1 = getFiles(text1)
    texts2 = getFiles(text2) 

    if verbose: 
        logging.basicConfig(level=logging.DEBUG)

    logging.debug('Comparing this/these text(s): %s' % str(texts1))
    logging.debug('with this/these text(s): %s' % str(texts2))

    pairs = list(itertools.product(texts1, texts2))

    numPairs = len(pairs) 

    logging.debug('Comparing %s pairs.' % numPairs)
    logging.debug('List of pairs to compare: %s' % pairs)

    for index, pair in enumerate(pairs): 
        logging.debug('Now comparing pair %s of %s.' % (index, numPairs))
        logging.debug('Comparing %s with %s.' % (pair[0], pair[1]))

        # Do the matching. 
        myMatch = Matcher(pair[0], pair[1], threshold, ngrams)
        myMatch.match()

        # Write to the log, but only if a match is found.
        if myMatch.numMatches > 0: 
            line = [pair[0], pair[1], str(threshold), str(ngrams), str(myMatch.numMatches)]
            line = ",".join(line) + '\n'
            f = open(logfile, 'a')
            f.write(line)
            f.close()

if __name__ == '__main__':
    cli()
