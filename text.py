import nltk
from nltk.tokenize import TweetTokenizer, RegexpTokenizer
from nltk.tag import pos_tag
from nltk.corpus import wordnet, stopwords
from nltk.stem import WordNetLemmatizer
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim import corpora, models
# from matplotlib import pyplot as plt


def get_text(dir):
    if dir.endswith('.json'):
        commit_list = json.load(open(dir, 'r'))
        texts = [i['message'] for i in commit_list]
        return texts
    files = os.listdir(dir)
    json_files = [f for f in files if f.endswith('.json')][:100]
    texts = []
    for json_file in json_files:
        file = os.path.join(dir, json_file)
        commit_list = json.load(open(file, 'r'))
        for commit in commit_list:
            if len(commit['message'].split(' ')) > 3:
                texts.append(commit['message'])
    print("Total {} lines.".format(len(texts)))
    return texts


def text_preprocess(text):
    # define tokenizer only considering 'Word' and 'word'
    regex_tokenizer = RegexpTokenizer(pattern='[A-Z]?[a-z]+')
    text_tokens = [regex_tokenizer.tokenize(i) for i in text]
    wnl = WordNetLemmatizer()
    preprocessed_text = []
    for tokens in text_tokens:
        tokens = [i.lower() for i in tokens]
        tagged_sent = pos_tag(tokens)
        lemmas_sent = []
        for tag in tagged_sent:
            wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
            lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))
        preprocessed_text.append(' '.join(lemmas_sent))
    return preprocessed_text


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def line_tokenizer(line, fine=True):
    """ split line and format a new line
    """
    f_tokenizer = RegexpTokenizer(pattern='\w+|[^\s\w]')
    if not fine:
        return " ".join([i.lower() for i in f_tokenizer.tokenize(line)])
    s_tokenizer = RegexpTokenizer(pattern='[A-Z][a-z]*|[a-z]+|\d+')
    tokens = f_tokenizer.tokenize(line.replace("_", " "))
    new_tokens = []
    for i in tokens:
        if len(i) == 1:
            new_tokens.append(i.lower())
        elif i.isalpha() and (i.islower() or i.isupper()):
            new_tokens.append(i.lower())
        else:
            [new_tokens.append(j.lower()) for j in s_tokenizer.tokenize(i)]
    return " ".join(new_tokens)


def lines_tokenizer(lines, fine=True):
    f_tokenizer = RegexpTokenizer(pattern='\w+|[^\s\w]')
    new_lines = []
    if not fine:
        for line in lines:
            new_lines.append(" ".join([i.lower()
                                       for i in f_tokenizer.tokenize(line)]))
        return new_lines
    s_tokenizer = RegexpTokenizer(pattern='[A-Z][a-z]*|[a-z]+|\d+')
    for line in lines:
        tokens = f_tokenizer.tokenize(line.replace("_", " "))
        new_tokens = []
        for i in tokens:
            if len(i) == 1:
                new_tokens.append(i.lower())
            elif i.isalpha() and (i.islower() or i.isupper()):
                new_tokens.append(i.lower())
            else:
                [new_tokens.append(j.lower()) for j in s_tokenizer.tokenize(i)]
        new_lines.append(" ".join(new_tokens))
    return new_lines


def text_cluster(texts, max_features=3000):
    tokenizer = TweetTokenizer(preserve_case=False)
    tfidf_vectorizer = TfidfVectorizer(
        tokenizer=tokenizer.tokenize, max_features=max_features)
    X = tfidf_vectorizer.fit_transform(texts)
    sse = []
    for n in range(10, 100, 5):
        kmeans_model = KMeans(n_clusters=n, random_state=1).fit(X)
        sse.append(kmeans_model.inertia_)
        print("{} {}".format(n, kmeans_model.inertia_))
    print("--- sse value to determin k ---")
    print(sse)
    # plt.plot(range(10, 100, 5), sse, marker='o')
    # plt.xlabel('k value')
    # plt.ylabel('sse')
    # plt.savefig('kmeans_sse.jpg')
    # plt.show()
    # labels = kmeans_model.labels_
    # with open("/Users/kingxu/tmp/message_label.txt", 'w') as f:
    #     for i, j in zip(labels, texts):
    #         f.write(str(i) + '\t' + j + '\n')


def LDA(texts, num_topics):
    stop_words = set(stopwords.words('english'))
    texts = [[w for w in l.strip().split() if w not in stop_words]
             for l in texts]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(l) for l in texts]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lda = models.LdaModel(
        corpus_tfidf, id2word=dictionary, num_topics=num_topics)
    lda.print_topics()


if __name__ == '__main__':
    # texts = get_text('/mnt/data1/kingxu/atomic_change')
    # print(len(texts))
    # text_cluster(texts)
    LDA(texts, 10)
    LDA(texts, 20)
