import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

import neo4jclass

nlp = spacy.load("en_core_web_md")
nlp.add_pipe("spacytextblob")

def analyse(conn, session_id, text):
  doc = nlp(text)
  index_length = 0
  for sentence in list(doc.sents):
    sbj = get_subject_phrase(sentence, index_length)
    obj = get_object_phrase(sentence, index_length)
    comp = get_complement(sentence, index_length)
    pred = get_predicate(sentence)
    summary = get_polarity_and_subjectivity(sentence)
    index_length += len(sentence)
    if (summary["assessments"] and (sbj is not None or obj is not None or comp is not None)):
      if (summary["subjectivity"] >= 0.5):
        neo4jclass.add_simple_attitude(
            conn, sbj, obj, comp, pred, summary["polarity"],
            summary["subjectivity"], session_id, str(sentence))
        #neo4jclass.add_detailed_attitude(
            #conn, sbj, obj, comp, pred,
            #summary["polarity"], session_id)

def get_subject_phrase(doc, index_length):
  for token in doc:
    if ("subj" in token.dep_):
      subtree = list(token.subtree)
      start = subtree[0].i - index_length
      end = subtree[-1].i + 1 - index_length
      return str(doc[start:end])
  return None

def get_object_phrase(doc, index_length):
  for token in doc:
    if ("obj" in token.dep_):
      subtree = list(token.subtree)
      start = subtree[0].i - index_length
      end = subtree[-1].i + 1 - index_length
      return str(doc[start:end])
  return None

def get_complement(doc, index_length):
  for token in doc:
    if ("comp" in token.dep_):
      return str(token)
  return None

def get_predicate(doc):
  for token in doc:
    if (("ROOT" in token.dep_) and ("VB" in token.tag_)):
      return str(token)
  return None

def get_polarity_and_subjectivity(doc):
  summary = {
      "polarity": doc._.polarity,
      "subjectivity": doc._.subjectivity,
      "assessments": doc._.assessments
  }
  return summary


