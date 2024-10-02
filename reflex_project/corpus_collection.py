import re
import pandas as pd


def clear_text(text):
    idx = text.find('X-FileName')
    text = text[idx:]
    idx = text.find('\n')
    text = text[idx:]
    text = re.sub(r'(^.*Forwarded.*$|^.*Subject.*$|^.*To:.*$|^.*cc:.*$|^.*From:.*$|^.*on.*\d{2}\/\d{2}\/\d{4}.*$)','', text, flags=re.MULTILINE)
    text = re.sub(r'\b(?:\d{1,2}[-/\.]){2}\d{2,4}\b', '', text)
    text = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap][Mm])?\b', '', text)
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b', '', text)
    text = re.sub(r'\b(?:\+?(\d{1,3}))?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b', '', text)
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
    if 'Outlook Migration Team' in text:
        idx = text.find('Current Notes User')
        text = text[idx:]

    text = text.replace('\n\n', '\n')
    text = text.replace('>', '')
    text = text.replace('<', '')
    text = text.replace('\t\t\t\t\t', ' ')
    text = text.replace('-', '')
    text = text.replace('_', '')
    text = text.replace('()', '')
    text = text.replace('&', 'and')
    text = re.sub(r'\b\w*(EES@|ECT@|@ENRON|.xls|.doc|HOU)\w*\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Original Message Sent: \w+,\s+\w+\s+\d{1,2},', '', text)
    text = re.sub(r'Original Message Sent:', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def collect_corpus(data_path):
    emails = pd.read_csv(data_path)
    corpus = []
    for i in range(emails.shape[0]):
        corpus.append(clear_text(emails.loc[i, :]['message']).split())
    return corpus


def extract_corpus(data_path):
    emails = pd.read_csv(data_path)
    corpus = []
    for i in range(emails.shape[0]//10):
        email = str(emails.loc[i, :]['message'])
        email_splitted = re.findall(r'[0-9]+|[A-z]+|,|.|;|:|\?|\(|\)|\[|]|"|!', email)
        email_splitted = [i.lower() for i in email_splitted if i != ' ']
        corpus.append(email_splitted)
        if i % 20000 == 0:
            print(i)
    return corpus
