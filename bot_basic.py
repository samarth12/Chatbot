#!/usr/bin/python
from __future__ import print_function, unicode_literals
import random
import logging
import os

os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

from textblob import TextBlob
from config import FILTER_WORDS

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

GREETING_KEYWORDS = ("hello", "hi", "greetings", "sup", "what's up",)

GREETING_RESPONSES = ["'sup bro", "hey", "*nods*", "hey you get my snap?"]

class UnacceptableUtteranceException(Exception):
    """Raise this (uncaught) exception if the response was going to trigger our blacklist"""
    pass

def check_for_greeting(sentence):
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)

NONE_RESPONSES = [
    "uh whatever",
    "meet me at the foosball table, bro?",
    "code hard bro",
    "want to bro down and crush code?",
    "I'd like to add you to my professional network on LinkedIn",
    "Have you closed your seed round, dog?",
]

COMMENTS_ABOUT_SELF = [
    "You're just jealous",
    "I worked really hard on that",
    "My Klout score is {}".format(random.randint(100, 500)),
]

def preprocess_text(sentence):
    cleaned = []
    words = sentence.split(' ')
    for w in words:
        if w == 'i':
            w = 'I'
        if w == "i'm":
            w = "I'm"
        cleaned.append(w)

    return ' '.join(cleaned)

def start_with_vowel(word):
    return True if word[0] in 'aeiou' else False

def bot(sentence):
    resp = response(sentence)
    return resp

def find_pronoun(sent):
    pronoun = None
    for word, pos in sent.pos_tags:
        if pos == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        if pos == 'PRP' and word.lower() == 'I':
            pronoun = 'You'
    return pronoun

def find_verb(sent):
    verb = None
    partos = None
    for word, pos in sent.pos_tags:
        if pos == 'VB':
            verb = word
            partos = pos
            break
    return verb, partos



def find_noun(sent):
    noun = None
    for word, pos in sent.pos_tags:
        if pos == 'NN':
            noun = word
            break
    return noun

def find_adjective(sent):
    adj = None
    for word, pos in sent.pos_tags:
        if pos == 'JJ':
            adj = word
            break
    return adj

def construct_response(pronoun, noun, verb):
    resp = []

    if pronoun:
        resp.append(pronoun)

    # We always respond in the present tense, and the pronoun will always either be a passthrough
    # from the user, or 'you' or 'I', in which case we might need to change the tense for some
    # irregular verbs.
    if verb:
        verb_word = verb[0]
        if verb_word in ('be', 'am', 'is', "'m"):  # This would be an excellent place to use lemmas!
            if pronoun.lower() == 'you':
                # The bot will always tell the person they aren't whatever they said they were
                resp.append("aren't really")
            else:
                resp.append(verb_word)
    if noun:
        pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(pronoun + " " + noun)

    resp.append(random.choice(("tho", "bro", "lol", "bruh", "smh", "")))

    return " ".join(resp)

def check_for_comment_about_bot(pronoun, noun, adjective):
    resp = None
    if pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp


SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "Were you aware I was a serial entrepreneur in the {noun} sector?",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]


def response(sentence):
    cleaned = preprocess_text(sentence)
    parsed = TextBlob(cleaned)
    pronoun, noun, adjective, verb = find_candidate_POS(parsed)
    resp = check_for_comment_about_bot(pronoun, noun, adjective)

    if not resp:
        resp = check_for_greeting(parsed)

    if not resp:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif pronoun == 'I' and not verb:
            resp = random.choice(COMMENTS_ABOUT_SELF)
        else:
            resp = construct_response(pronoun, noun, verb)

    if not resp:
        resp = random.choice(NONE_RESPONSES)

    logger.info("Returning phrase '%s'", resp)
    filter_response(resp)

    return resp



def find_candidate_POS(parsed):
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for sent in parsed.sentences:
        pronoun = find_pronoun(sent)
        noun = find_noun(sent)
        adjective = find_adjective(sent)
        verb = find_verb(sent)
    logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun, noun, adjective, verb)
    return pronoun, noun, adjective, verb


def filter_response(resp):
    tok = resp.split(' ')
    for word in tok:
        if '@' in word or '!' in word or '#' in word:
            raise UnacceptableUtteranceException()

        for s in FILTER_WORDS:
            if word.lower().startswith(s):
                raise UnacceptableUtteranceException()

if __name__ == '__main__':
    import sys
    # Usage:
    # python broize.py "I am an engineer"
    if (len(sys.argv) > 0):
        saying = sys.argv[1]
    else:
        saying = "How are you, brobot?"
    print(bot(saying))