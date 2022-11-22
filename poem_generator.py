import pandas as pd
import numpy as np
import spacy
from writer import *


def generate(writer=None, keywords='', n_sents=4):
    df = None

    if writer is None:
        df = merge_poem_files()
    else:
        file = get_filename(writer)
        df = pd.read_csv(file)

    return poem_generator(df, keywords, n_sents)


def merge_poem_files():
    df = None
    sup_index = 0
    start_doc_id = 0

    for writer in Writer:
        file = get_filename(writer)
        df_writer = pd.read_csv(file)
        number_docs = df_writer.shape[0]

        index = [sup_index + i for i in range(number_docs)]
        sup_index += number_docs + 1
        doc_id = [start_doc_id + i for i in df_writer['doc_id']]

        doc_sentences = pd.DataFrame(
            {'index': index, 'doc_id': doc_id, 'sentence': df_writer['sentence']})

        df = pd.concat(
            [df, doc_sentences], ignore_index=True)

        start_doc_id = doc_sentences.iloc[-1]['doc_id'] + 1

    return df


def poem_generator(sentences, keywords, n_sents):
    nlp = spacy.load("en_core_web_sm")
    init_str = nlp(keywords)

    if keywords != '':
        sentences.loc[-1] = ['-1', '0', keywords]
        sentences.index = sentences.index + 1
        sentences.sort_index(inplace=True)

    poem = []
    sup_index = sentences.shape[0]
    poem_id = int()

    for i in range(n_sents):
        rand_sent_index = np.random.randint(0, sup_index, size=30)
        if i == 0 and keywords != '':
            rand_sent_index = np.insert(rand_sent_index, 0, 0)

        sent_list = list(sentences.sentence.iloc[rand_sent_index])
        docs = nlp.pipe(sent_list)
        sim_list = []

        for sent in docs:
            similarity = (init_str.similarity(sent))
            sim_list.append(similarity)

        df_1 = pd.DataFrame(
            {'similarity': sim_list, 'doc_id': sentences.doc_id.iloc[rand_sent_index]}, index=rand_sent_index)
        df_1 = df_1[df_1.doc_id != poem_id]
        df_1.sort_values(by='similarity', inplace=True, ascending=False)

        sent_index = df_1.index[0]
        sent = sentences.sentence[sent_index]

        replace_dict = {'\n':  '', '\r':  ''}
        for x, y in replace_dict.items():
            sent = sent.replace(x, y)

        poem.append(sent)
        poem_id = df_1.doc_id.iloc[0]
        init_str = nlp(sent)

    str_poem = ("\n".join(poem))

    if str_poem[-1].isalpha() == False:
        str_poem = str_poem[:-1]

    return str_poem + '.'
