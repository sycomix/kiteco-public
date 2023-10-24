#!/bin/env python

# This script will exit with a (hopefully informative) error if the C-optimized gensim module
# for word2vec is not available.

from scipy.version import version

if version != "0.15.1":
	print(f"Warning: scipy version is {version}. Try pip install scipy==0.15.1")

from gensim.models.word2vec_inner import train_sentence_sg, train_sentence_cbow, FAST_VERSION

print("C-optimized gensim module for word2vec is working")