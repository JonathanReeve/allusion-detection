
# coding: utf-8

import nltk
import re
import difflib
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
        return open(self.filename).read()

    @property
    def tokens(self): 
        """ Tokenizes the text, breaking it up into words, removing punctuation. """
        tokenizer = nltk.RegexpTokenizer('[a-zA-Z]\w+\'?\w*') # A custom regex tokenizer. 
        self.spans = list(tokenizer.span_tokenize(self.text))
        return tokenizer.tokenize(self.text)
    
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



@click.command()
@click.argument('text1', type=click.Path(exists=True))
@click.argument('text2', type=click.Path(exists=True))
@click.option('-t', '--threshold', type=int, default=2, help='The shortest length of match to include.')
@click.option('-n', '--ngrams', type=int, default=3, help='The ngram n-value to match against.')
@click.option('-l', '--logfile', default='log.txt', help='The name of the log file to write to.')
def cli(text1, text2, threshold, ngrams, logfile):
    """ This program finds similar text in two text files. """
    myMatch = Matcher(text1, text2, threshold, ngrams)
    myMatch.match()

    # Write the log
    line = [text1, text2, str(threshold), str(ngrams), str(myMatch.numMatches)]
    line = ",".join(line) + '\n'
    f = open(logfile, 'a')
    f.write(line)
    f.close()

if __name__ == '__main__':
    cli()
