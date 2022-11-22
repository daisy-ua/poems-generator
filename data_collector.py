import pandas as pd
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from writer import *
from pathlib import Path
import os


def load_initial_data():
    callback = None

    Path(os.path.join(os.path.dirname(__file__)) +
         "/data").mkdir(parents=True, exist_ok=True)
    

    for writer in Writer:
        if writer == Writer.EDGAR_ALLAN_POE:
            callback = edgar_allan_poe_callback

        file = get_filename(writer)
        parse_data(writer.value, file, callback)
        docs_to_sentences(file)


def edgar_allan_poe_callback(results):
    ignore_link = "https://mypoeticside.com/show-classic-poem-22531"
    results.remove(ignore_link)
    return results


def parse_data(writer, output_file, callback=None):
    data = any
    with urlopen('https://mypoeticside.com/poets/' + writer) as url:
        data = url.read().decode()

    soup = BeautifulSoup(data, 'html.parser')
    poem_list = soup.find(class_="list-poems")
    links = poem_list.findAll('a')

    results = ["https:" + link.get('href') for link in links]

    if callback != None:
        results = callback(results)

    titles = []
    corpus = []
    for page in results:
        with urlopen(page) as url:
            data = url.read().decode()

        soup = BeautifulSoup(data, 'html.parser')
        title = soup.find(class_='title-poem')
        poem = soup.find(class_='poem-entry')
        titles.append(title.getText())
        corpus.append(poem.find('p').getText())

    poems = pd.DataFrame({'title': titles, 'text': corpus})
    poems.to_csv(output_file)


def docs_to_sentences(file, split=r"\n"):
    df_docs = pd.read_csv(file)
    number_docs = df_docs.shape[0]
    df_sentences = pd.DataFrame(columns=['doc_id', 'sentence'])

    for i in range(number_docs):
        text = df_docs.text[i]

        replace_dict = {'?«':  '«',
                        '(':  '', ')': '', ':': ',', '.': ',', ',,,': ','}
        for x, y in replace_dict.items():
            text = text.replace(x, y)
        text = text.lower()

        sentences = re.split(split, text)
        len_sentences = len(sentences)
        doc_id = [i] * (len_sentences)
        sentences = [i.strip() for i in sentences]

        doc_sentences = pd.DataFrame({'doc_id': doc_id, 'sentence': sentences})
        df_sentences = pd.concat(
            [df_sentences, pd.DataFrame.from_records(doc_sentences)])

    df_sentences = df_sentences[df_sentences.sentence != '']
    df_sentences.reset_index(drop=True, inplace=True)

    df_sentences.to_csv(file)
