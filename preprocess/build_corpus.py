"""
Transforms each dictionary with questions into a pickle Corpus instance.

All input file must have a pickled list of dictionaries with keys 'questions'.
Each question will be procesed with the features in the file feature_extraction.

The output file will have a pickled instance of Corpus

"""

import pickle

from docopt import docopt
from feature_extraction import get_features
from corpus import Corpus
from sklearn.preprocessing import Normalizer, MinMaxScaler
from scipy.sparse import csr_matrix
from scipy import int8


def _get_repr(word_list):
    return ' '.join([w.token for w in word_list])


def process_corpus(tr_in_filename, te_in_filename, u_in_filename,
                   tr_out_filename, te_out_filename, u_out_filename):
    input_f = open(tr_in_filename, 'r')
    tr_original_corpus = pickle.load(input_f)
    input_f.close()

    input_f = open(te_in_filename, 'r')
    te_original_corpus = pickle.load(input_f)
    input_f.close()

    input_f = open(u_in_filename, 'r')
    u_original_corpus = pickle.load(input_f)
    input_f.close()
    tr_instances = [d['question'] for d in tr_original_corpus
                    if '' not in d['target']]
    te_instances = [d['question'] for d in te_original_corpus
                    if '' not in d['target']]
    u_instances = [d['question'] for d in u_original_corpus
                   if ((not 'target' in d) or '' not in d['target'])]

    vect = get_features()
    vect.fit(tr_instances + te_instances + u_instances)
    v_instances = vect.transform(tr_instances + te_instances + u_instances)
    v_instances = csr_matrix(v_instances > 0, dtype=int8)
    print v_instances.shape

    tr_corpus = Corpus()
    tr_corpus.instances = v_instances[:len(tr_instances)]
    tr_corpus.full_targets = [d['target'] for d in tr_original_corpus
                              if '' not in d['target']]
    tr_corpus.representations = [_get_repr(i[0]) for i in tr_instances]
    tr_corpus._features_vectorizer = vect
    tr_corpus.save_to_file(tr_out_filename)

    te_corpus = Corpus()
    te_corpus.instances = v_instances[:len(te_instances)]
    te_corpus.full_targets = [d['target'] for d in te_original_corpus
                              if '' not in d['target']]
    te_corpus.representations = [_get_repr(i[0]) for i in te_instances]
    te_corpus._features_vectorizer = vect
    te_corpus.save_to_file(te_out_filename)

    u_corpus = Corpus()
    u_corpus.instances = v_instances[:len(u_instances)]
    u_corpus.full_targets = [d['target']
                             if ('target' in d and '' not in d['target']) else []
                             for d in u_original_corpus]
    u_corpus.representations = [_get_repr(i[0]) for i in u_instances]
    u_corpus._features_vectorizer = vect
    u_corpus.save_to_file(u_out_filename)
