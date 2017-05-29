# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 18:26:40 2016

@author: lifu
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation
import jieba
import numpy as np
import scipy as sp
import argparse
import os

def extract_qa_pairs(text):
    lines = text.split('\n')[:-1]
    evenLines = map(lambda p: p[1][8:], 
                    filter(lambda p: p[0] & 1 == 0, enumerate(lines)))
    oddLines = map(lambda p: p[1][6:], 
                   filter(lambda p: p[0] & 1 == 1, enumerate(lines)))
    return evenLines, oddLines

if __name__ == '__main__':    
    ap = argparse.ArgumentParser()
    ap.add_argument(dest = 'input_path', 
                    help = 'file containing text to be clustered')
    ap.add_argument(dest = 'output_dir',
                    help = 'directory of the clustered result')
    ap.add_argument(dest = 'n_clusters', type = int,
                    help = 'number of clusters')
    ap.add_argument('--ndims', dest = 'n_dims', type = int, 
                    help = 'dimensions of word space')
    args = ap.parse_args()
    
    with open(args.input_path) as f:
        text = f.read()
    questions, answers = extract_qa_pairs(text)

    tv = TfidfVectorizer(tokenizer=jieba.cut)    
    X = tv.fit_transform(answers)
    if args.n_dims:
        print 'Reducing dimension from %d to %d...' % (X.shape[1], args.n_dims),
        U, s, Vt = sp.sparse.linalg.svds(X, k=args.n_dims)
        X = X.dot(Vt.T)
        print 'Done!'
    
    print 'Clustering...',
    km = KMeans(n_clusters = args.n_clusters)
    ap = AffinityPropagation()
    km.fit(X)
    print 'Done!'
    
    clustered_ans = [[] for i in xrange(args.n_clusters)]
    clustered_qst = [[] for i in xrange(args.n_clusters)]
    
    for i in xrange(len(questions)):
        clustered_ans[km.labels_[i]].append(answers[i])
        clustered_qst[km.labels_[i]].append(questions[i])

    answer_cluster_dir = os.path.join(args.output_dir, 'answer_clusters/')
    question_cluster_dir = os.path.join(args.output_dir, 'question_clusters/')
    if not os.path.exists(answer_cluster_dir):
        os.makedirs(answer_cluster_dir)
    if not os.path.exists(question_cluster_dir):
        os.makedirs(question_cluster_dir)
        
    for i in xrange(args.n_clusters):
        print 'Generating cluster #', i, '...',
        answer_cluster_path = os.path.join(answer_cluster_dir,
                                            str(i) + '.txt')
        question_cluster_path = os.path.join(question_cluster_dir,
                                             str(i) + '.txt')
        with open(answer_cluster_path, 'w') as f:
            f.write('\n'.join(clustered_ans[i]))
        with open(question_cluster_path, 'w') as f:
            f.write('\n'.join(clustered_qst[i]))
        print 'Done'
    print 'Success!'
