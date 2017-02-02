import os
import nltk
import pickle
from nltk.corpus import twitter_samples
from nltk.tokenize import word_tokenize
import random
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from Classifier import VoteClassifier

#  j is adject, r is adverb, and v is verb
ALLOWED_WORD_TYPES = ["J", "R", "V"]
PROJECT_ROOT = os.path.dirname(__file__)


# puts all words from the twitter samples into an array
def get_all_words_and_documents():
    if data_exists("all_words") and data_exists("documents"):
        return load_data("all_words"), load_data("documents")
    documents = []
    all_words = []
    for fileid in [("positive_tweets.json", "pos"),
                   ("negative_tweets.json", "neg")]:
        for tokens in twitter_samples.tokenized(fileid[0]):
            documents.append((" ".join(tokens), fileid[1]))
            pos = nltk.pos_tag(tokens)
            for w in pos:
                if w[1][0] in ALLOWED_WORD_TYPES:
                    all_words.append(w[0].lower())
    save_data(all_words, "all_words")
    save_data(documents, "documents")
    return all_words, documents


def save_data(data, name):
    save_data = open(
        os.path.join(PROJECT_ROOT, "pickles", name + ".pickle"), "wb")
    pickle.dump(data, save_data)
    save_data.close()


def load_data(name):
    data_f = open(
        os.path.join(PROJECT_ROOT, "pickles", name + ".pickle"), "rb")
    data = pickle.load(data_f)
    data_f.close()
    return data


def data_exists(name):
    return os.path.isfile(
        os.path.join(PROJECT_ROOT, "pickles", name + ".pickle"))


def get_word_features():
    if data_exists("word_features"):
        return load_data("word_features")
    all_words = get_all_words_and_documents()[0]
    all_words = nltk.FreqDist(all_words)
    word_features = list(all_words.keys())
    save_data(word_features, "word_features")
    return word_features


def find_features(document, all_words, word_features):
    words = word_tokenize(document)
    return {w: (w in words) for w in word_features}


def create_feature_sets():
    all_words, documents = get_all_words_and_documents()
    word_features = get_word_features()
    return [(find_features(rev, all_words, word_features), category)
            for (rev, category) in documents]


def create_classifiers():
    if data_exists("classifiers"):
        return load_data("classifiers")
    feature_sets = create_feature_sets()
    random.shuffle(feature_sets)

    size = int(len(feature_sets) / 2)

    training_set = feature_sets[size:]

    classifiers = list(
        map(lambda c: (SklearnClassifier(c()).train(training_set), c.__name__),
            [
                MultinomialNB, BernoulliNB, LogisticRegression, SVC, LinearSVC,
                NuSVC, SGDClassifier
            ]))

    save_data(classifiers, "classifiers")
    return classifiers


def create_voted_classifier(classifiers):
    if data_exists("voted_classifier"):
        return load_data("voted_classifier")
    else:
        voted_classifier = VoteClassifier([c[0] for c in classifiers])
        save_data(voted_classifier, "voted_classifier")
        return voted_classifier


def sentiment(text):
    classifiers = create_classifiers()
    voted_classifier = create_voted_classifier(classifiers)
    all_words = get_all_words_and_documents()[0]
    word_features = get_word_features()
    feats = find_features(text, all_words, word_features)
    return voted_classifier.classify(feats), voted_classifier.confidence(feats)


if __name__ == "__main__":
    test = "Memes keep me alive"
    print(sentiment(test))
