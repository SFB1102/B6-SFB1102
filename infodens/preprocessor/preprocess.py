# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 15:19:12 2016

@author: admin
"""
import nltk
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer
import subprocess
from infodens.preprocessor.preprocess_services import Preprocess_Services
import os


class Preprocess:
    
    fileName = ''
    
    def __init__(self, configurator):

        self.inputFile = configurator.inputFile
        self.corpusForLM = configurator.corpusLM
        self.operatingLanguage = configurator.language
        self.sentCount = 0
        self.threadsCount = configurator.threadsCount
        self.plainLof = []
        self.tokenSents = []
        self.parseTrees = []
        self.taggedPOSSents = []
        self.lemmatizedSents = []
        self.mixedSents = []
        self.word2vecModel = {}
        self.langModelFiles = []
        self.srilmBinaries = configurator.srilmBinPath
        self.kenlmbins = configurator.kenlmBinPath
        self.prep_servs = Preprocess_Services(srilmBinaries=configurator.srilmBinPath,
                                              kenlmBins=configurator.kenlmBinPath,
                                              lang=configurator.language)

    def getLanguageMode(self):
        """Return the current language mode."""
        return self.operatingLanguage

    def setLanguageMode(self, lang):
        """Set language mode for preprocessing operations."""
        self.operatingLanguage = lang

    def getSentCount(self):
        self.getPlainSentences()
        return self.sentCount

    def getInputFileName(self):
        return self.inputFile

    def getCorpusLMName(self):
        return self.corpusForLM

    def getBinariesPath(self):
        return self.srilmBinaries, self.kenlmbins

    def getPlainSentences(self):
        """Return sentences as read from file."""
        if not self.plainLof:
            self.plainLof = self.prep_servs.preprocessBySentence(self.inputFile)
            self.sentCount = len(self.plainLof)
        return self.plainLof

    def gettokenizeSents(self):
        """Return tokenized sentences."""
        if not self.tokenSents:
            self.tokenSents = [nltk.word_tokenize(sent) for sent in self.getPlainSentences()]
        return self.tokenSents

    def getParseTrees(self):
        """Return parse trees of each sentence."""
        from pattern.en import parsetree
        if not self.parseTrees:
            self.parseTrees = [parsetree(sent) for sent in self.getPlainSentences()]
        return

    def buildLanguageModel(self, ngram=3, corpus="", discounting=True):
        """Build a language model from given corpus."""

        if not self.corpusForLM and not corpus:
            print("Corpus for Language model not defined.")
            return 0
        elif self.corpusForLM and not corpus:
            testCWDCorpus = "{0}{1}".format(os.path.join(os.getcwd(), ''), self.corpusForLM)
            if os.path.isfile(testCWDCorpus):
                # File in CWD, add directory to path
                corpus = testCWDCorpus
            else:
                # Use as is
                corpus = self.corpusForLM

        # remove any quotes
        corpus = corpus.replace("\"", "")
        langModelFile = "{0}_langModel{1}.lm".format(os.path.basename(corpus), ngram)
        # Wrap to handle spaces in path
        if not corpus.endswith("\""):
            corpus = "\"{0}\"".format(corpus)

        if langModelFile not in self.langModelFiles:
            self.prep_servs.languageModelBuilder(ngram, corpus, langModelFile, kndiscount=discounting)
            self.langModelFiles.append(langModelFile)
        else:
            print(langModelFile)

        return langModelFile

    def buildBackwardLanguageModel(self, ngram=3, corpus="", discounting=True):
        """Build a language model from given corpus."""

        if corpus:
            # find its reversed version
            corpus = "".join(os.path.splitext(corpus)[:-1]) + "_reversed" \
                                              + os.path.splitext(corpus)[-1]

        if not self.corpusForLM and not corpus:
            print("Corpus for Language model not defined.")
            return 0
        elif self.corpusForLM and not corpus:
            reversedCorpusForLM = "".join(os.path.splitext(self.corpusForLM)[:-1]) + "_reversed" \
                                              + os.path.splitext(self.corpusForLM)[-1]
            testCWDCorpus = "{0}{1}".format(os.path.join(os.getcwd(), ''), reversedCorpusForLM)
            if os.path.isfile(testCWDCorpus):
                # File in CWD, add directory to path
                corpus = testCWDCorpus
            else:
                # Use as is
                corpus = reversedCorpusForLM

        # remove any quotes
        corpus = corpus.replace("\"", "")
        langModelFile = "{0}_langModel{1}.lm".format(os.path.basename(corpus), ngram)
        # Wrap to handle spaces in path
        if not corpus.endswith("\""):
            corpus = "\"{0}\"".format(corpus)

        if langModelFile not in self.langModelFiles:
            self.prep_servs.languageModelBuilder(ngram, corpus, langModelFile, kndiscount=discounting)
            self.langModelFiles.append(langModelFile)
        else:
            print(langModelFile)

        return langModelFile

    def getPOStagged(self, filePOS=""):
        """ Return POS tagged sentences from Input file or tokens. """
        if filePOS:
            # Return tokens from POS file give
            return self.prep_servs.getFileTokens(filePOS)

        if not self.taggedPOSSents:
            print("POS tagging..")
            tagPOSSents = nltk.pos_tag_sents(self.gettokenizeSents(), lang=self.operatingLanguage)
            for i in range(0, len(tagPOSSents)):
                self.taggedPOSSents.append([wordAndTag[1] for wordAndTag in tagPOSSents[i]])
            print("POS tagging done.")

        return self.taggedPOSSents
        
    def getLemmatizedSents(self):
        """Lemmatize and return sentences."""
        if not self.lemmatizedSents:
            self.gettokenizeSents()
            lemmatizer = WordNetLemmatizer()
            for i in range(0, len(self.tokenSents)):
                lemmatized = [lemmatizer.lemmatize(a) for a in self.tokenSents[i]]
                self.lemmatizedSents.append(lemmatized)

        return self.lemmatizedSents
        
    def getMixedSents(self):
        """Build and return mixed sentences (POS for J,N,V, or R)"""
        if not self.mixedSents:
            self.getPOStagged()
            for i in range(len(self.tokenSents)):
                sent = []
                for j in range(len(self.tokenSents[i])):
                    if self.taggedPOSSents[i][j].startswith('J') or \
                            self.taggedPOSSents[i][j].startswith('N') or \
                            self.taggedPOSSents[i][j].startswith('V') or \
                            self.taggedPOSSents[i][j].startswith('R'):
                        sent.append(self.taggedPOSSents[i][j])
                    else:
                        sent.append(self.tokenSents[i][j])
                self.mixedSents.append(sent)
            
        return self.mixedSents

    def getWord2vecModel(self, size=100):
        if not self.corpusForLM:
            print("Corpus not provided...")
            return 0
        if size not in self.word2vecModel.keys():
            self.word2vecModel[size] = self.prep_servs.trainWord2Vec(size, self.corpusForLM, self.threadsCount)
        return self.word2vecModel[size]


