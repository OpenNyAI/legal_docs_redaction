import uuid

import spacy
import pandas as pd
from name_matching.name_matcher import NameMatcher

entity_types_to_mask = ["CARDINAL", "DATE", "MONEY","PERCENT", "QUANTITY", "TIME"]
entity_type_to_replace = ["ORG","PERSON","PRODUCT"]
def redact_entity(ent,grouped_entities:dict) -> str:
    # if ent.text == 'MRIL Limited':
    #     print('here')
    if ent.label_ in entity_type_to_replace:
        group_id = grouped_entities.get((ent.start_char, ent.end_char))
        if group_id is not None:
            redacted_text = ent.label_ + "_" + str(group_id)
        else:
            redacted_text = ent.label_ + "_" + uuid.uuid4().hex
    else:
        redacted_text = "XXXXX"

    return redacted_text


def create_groups(result_df) -> dict:
    # Creates groups based on the result of name matching. Creates a dict mapping each span to a group id. Returns dict with key as span and value as group id
    groups = {}
    group_id = 1
    for index, row in result_df.iterrows():
        ent1_span = (row['original_ent'].start_char, row['original_ent'].end_char)
        ent2_span = (row['match_ent'].start_char, row['match_ent'].end_char)
        if groups.get(ent1_span) is None:
            if groups.get(ent2_span) is None:
                groups[ent1_span] = group_id
                groups[ent2_span] = group_id
                group_id += 1
            else:
                groups[ent1_span] = groups[ent2_span]
        else:
            if groups.get(ent2_span) is None:
                groups[ent2_span] = groups[ent1_span]

    return groups

def group_similar_names(matcher, entities:list,threshold = 40) -> dict:
    # Groups the entities based on similarity and returns a dict with span as key and group id as value
    result_df = pd.DataFrame()
    for i in range(len(entities)):
        similar_type_ents = [j for j in entities[i+1:] if j.label_ == entities[i].label_ and j.label_ in entity_type_to_replace]
        if len(similar_type_ents) > 0:
            names_to_be_matched = pd.DataFrame({"name":[n.text for n in similar_type_ents],
                                                "ent":similar_type_ents})
            name_to_match = pd.DataFrame({"name":[entities[i].text],
                                          "ent":[entities[i]]})
            matcher.load_and_process_master_data('name', names_to_be_matched)
            result = matcher.match_names(to_be_matched=name_to_match, column_matching='name')
            result['original_ent'] = [entities[i]]
            result['match_ent'] = names_to_be_matched['ent'].loc[result['match_index'].to_list()].to_list()
            result = result.loc[result['score'] >= threshold]
            result_df = pd.concat([result_df,result])
    groups = create_groups(result_df)
    return groups




if __name__ == '__main__':
    nlp = spacy.load("en_core_web_trf")
    file_path = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review/output/text_plain_ocr/FACILITY AGREEMENT.txt'
    redacted_output_path = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review/output/text_plain_ocr/'
    text = open(file_path).read()
    doc = nlp(text)
    original_text = text
    entities = [i for i in doc.ents]
    entities = sorted(entities, key=lambda x: x.start_char)

    matcher = NameMatcher(top_n=1,
                          lowercase=True,
                          punctuations=True,
                          remove_ascii=True,
                          legal_suffixes=True,
                          common_words=False,
                          verbose=True)

    matcher.set_distance_metrics(['discounted_levenshtein',
                                  'SSK',
                                  'fuzzy_wuzzy_token_sort'])

    grouped_entities = group_similar_names(matcher,entities)
    redacted_text = original_text[0:entities[0].start_char]
    original_redacted_map = []
    for i,ent in enumerate(entities):
        if ent.label_ in entity_types_to_mask or ent.label_ in entity_type_to_replace:
            redacted_entity_text = redact_entity(ent, grouped_entities)
            redacted_text = redacted_text + redacted_entity_text
            if i < len(entities) - 1:
                redacted_text = redacted_text + original_text[ent.end_char:entities[i+1].start_char]
            else:
                redacted_text = redacted_text + original_text[entities[-1].end_char:]

            original_redacted_map.append({"original_text":ent.text,
                                          "original_span":(ent.start_char,ent.end_char),
                                          "entity_type":ent.label_,
                                          "redacted_text":redacted_entity_text})

    original_redacted_df = pd.DataFrame(original_redacted_map)
    original_redacted_df.to_csv(redacted_output_path + 'original_redacted_map.csv',index=False)
    with open(redacted_output_path+ 'redacted_text.txt','w') as f:
        f.write(redacted_text)
