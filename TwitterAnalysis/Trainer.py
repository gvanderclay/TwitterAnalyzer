import os
import time
import sys
import nltk
import pickle
import random
from os.path import basename, dirname
from multiprocessing import Pool
from nltk.corpus import twitter_samples
from nltk.tokenize.casual import TweetTokenizer
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.classify.util import apply_features
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from Classifier import VoteClassifier

#  j is adject, r is adverb, and v is verb
ALLOWED_WORD_TYPES = ["J", "R", "V"]
PROJECT_ROOT = os.path.dirname(__file__)

# tokenizer that is aware of twitter strings
# http://www.nltk.org/api/nltk.tokenize.html#module-nltk.tokenize.casual
tokenizer = TweetTokenizer(strip_handles=True)

all_words = None

documents = None


# - All words
# all_words is an array that contains all of the words in the training sets
# maybe be filtered based on POS
# - Documents
# documents is an array that contains tokenized versions of tweets
# with a sentiment tag of either Positive ("pos") or Negative ("neg")
def get_all_words_and_documents():
    global all_words, documents
    if all_words is not None and documents is not None:
        return all_words, documents
    if data_exists("all_words") and data_exists("documents"):
        all_words = load_data("all_words")
        documents = load_data("documents")
        return all_words, documents
    documents = []
    all_words = []
    print("starting words and documents")
    for fileid in [("positive_tweets.json", "pos"),
                   ("negative_tweets.json", "neg")]:
        print("Analyzing " + fileid[0])
        for tokens in twitter_samples.tokenized(fileid[0]):
            documents.append((" ".join(tokens), fileid[1]))
            pos = nltk.pos_tag(tokens)
            for w in pos:
                # TODO should we get rid of POS filtering
                if w[1][0] in ALLOWED_WORD_TYPES:
                    all_words.append(w[0].lower())
    for directory in ['positive', 'negative']:
        for filename in os.listdir(directory):
            i = 0
            randomize_lines_in_file(directory + '/' + filename)
            file = open(directory + '/shuffled_' + filename, 'r')
            print("Analyzing " + filename)
            for tweet in file:
                i += 1
                tweet = tweet.replace(":)", "")
                tweet = tweet.replace(":(", "")
                documents.append((tweet, directory[:3]))
                pos = nltk.pos_tag(tweet)
                for w in pos:
                    # TODO should we get rid of POS filtering
                    if w[1][0] in ALLOWED_WORD_TYPES:
                        all_words.append(w[0].lower())
                if i == 10000:
                    print("Reached 10000")
                    file.close()
                    break
            file.close()
            os.remove(file.name)
    print("Done with all words and documents")
    save_data(all_words, "all_words")
    save_data(documents, "documents")
    return all_words, documents


def randomize_lines_in_file(filename):
    base_filename = None
    directory = None
    with open(filename, 'r') as source:
        base_filename = basename(source.name)
        directory = dirname(source.name)
        data = [(random.random(), line) for line in source]
        data.sort()
    with open(directory + '/shuffled_' + base_filename, 'w') as target:
        for _, line in data:
            target.write(line)


def get_documents():
    global documents
    if documents is not None:
        return documents
    if data_exists("documents"):
        documents = load_data("documents")
        return documents
    raise "Documents does not exist"


# Save the data to a pickle
def save_data(data, name):
    save_data = open(
        os.path.join(PROJECT_ROOT, "pickles", name + ".pickle"), "wb")
    pickle.dump(data, save_data)
    save_data.close()


# load the pickles
def load_data(name):
    data_f = open(
        os.path.join(PROJECT_ROOT, "pickles", name + ".pickle"), "rb")
    data = pickle.load(data_f)
    data_f.close()
    return data


# check if a pickle exists for the data
def data_exists(name):
    return os.path.isfile(
        os.path.join(PROJECT_ROOT, "pickles", name + ".pickle"))


word_features = None


# Get the set of all words in the training data
def get_word_features():
    global word_features
    if word_features is not None:
        return word_features
    if data_exists("word_features") and word_features is None:
        word_features = load_data("word_features")
        return word_features
    print("Getting word features")
    all_words = get_all_words_and_documents()[0]
    all_words = nltk.FreqDist(all_words)
    word_features = list(all_words.keys())[:5000]
    save_data(word_features, "word_features")
    return word_features


# Get the features of a document
def find_features(document):
    # updated tokenizer that is aware of weird twitter strings
    words = tokenizer.tokenize(document)
    word_features = get_word_features()
    features = {w: (w in words) for w in word_features}
    return features


def create_feature_sets(documents=None):
    print("Creating features sets")
    if documents is None:
        pass
    elif data_exists("documents"):
        documents = get_documents()
    else:
        documents = get_all_words_and_documents()[1]
    print("Creating feature_sets")
    return apply_features(find_features, documents, labeled=True)


class Trainer(object):
    def __init__(self, training_set):
        self.training_set = training_set

    def __call__(self, classifier):
        if data_exists(classifier.__name__):
            return load_data(classifier.__name__)
        print("Training: " + classifier.__name__)
        c = (SklearnClassifier(classifier()).train(self.training_set),
             classifier.__name__)
        save_data(c, classifier.__name__)
        return c


def create_classifiers():
    classes = [
        MultinomialNB,
        BernoulliNB,
        LogisticRegression,
        SVC,
        LinearSVC,
        NuSVC,
        SGDClassifier
    ]
    all_exist = all(map(lambda c: data_exists(c.__name__), classes))
    if all_exist:
        return list(map(lambda c: load_data(c.__name__), classes))
    feature_sets = list(create_feature_sets())
    random.shuffle(feature_sets)

    size = int(len(feature_sets) / 2)

    training_set = feature_sets[:size]
    testing_set = feature_sets[size:]

    print("training...")
    classifiers = list(map(Trainer(training_set), classes))
    print("training finished")

    print("testing")
    for c in classifiers:
        print("Accuracy for " + c[1] + ": " + str(
            nltk.classify.accuracy(c[0], testing_set) * 100))
    print("Done testing")
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
    feats = find_features(text)
    return voted_classifier.classify(feats), voted_classifier.confidence(feats)


if __name__ == "__main__":
    tweet = sys.argv[1] if len(sys.argv) > 1 else "I love pizza so much"
    start = time.time()
    print(sentiment(tweet))
    end = time.time()
    print((end - start))
