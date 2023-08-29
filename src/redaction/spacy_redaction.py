from tqdm import tqdm
import glob
import spacy
import pandas as pd
from name_matching.name_matcher import NameMatcher
import os

class DataRedaction:
    def __init__(self,input_dir_path,redacted_output_path):
        self.entity_types_to_mask = ["DATE", "MONEY","PERCENT", "QUANTITY", "TIME"]
        self.entity_type_to_replace = ["ORG","PERSON","PRODUCT"]
        self.nlp = spacy.load("en_core_web_trf")
        self.input_dir_path = input_dir_path
        self.redacted_output_path = redacted_output_path
        os.makedirs(self.redacted_output_path,exist_ok=True)
        self.number_of_matches = 10

        self.matcher = NameMatcher(top_n=self.number_of_matches * 2,
                                number_of_matches = self.number_of_matches,
                              lowercase=True,
                              punctuations=True,
                              remove_ascii=True,
                              legal_suffixes=True,
                              common_words=False,
                              verbose=False)
        self.matcher.set_distance_metrics(['discounted_levenshtein',
                                      'SSK',
                                      'fuzzy_wuzzy_token_sort'])
        self.matching_threshold = 80 # match below this would be discarded

    def _redact_entity(self, ent,grouped_entities:dict,last_group_id) -> tuple[str,int]:
        if ent.label_ in self.entity_type_to_replace:
            ent_text_type = ent.text.lower().strip() + '_' + ent.label_
            group_id = grouped_entities.get(ent_text_type)
            if group_id is not None:
                redacted_text = ent.label_ + "_" + str(group_id)
            else:
                redacted_text = ent.label_ + "_" + str(last_group_id)
                last_group_id += 1
        else:
            redacted_text = "XXXXX"

        return redacted_text,last_group_id

    def _group_similar_names(self, entities:list) -> dict:
        # Groups the entities based on similarity and returns a dict with entity text as key and group id as value
        group_id = 0
        grouped_entities = {}
        for i in range(len(entities)):
            entity_text = entities[i].text.lower().strip()
            entity_text_type = entity_text + '_' + entities[i].label_

            if grouped_entities.get(entity_text_type) or (entities[i].label_ not in self.entity_type_to_replace and entities[i].label_ not in self.entity_types_to_mask):
                continue

            similar_type_ents = [j for j in entities[i+1:] if j.label_ == entities[i].label_ and
                                 entity_text != j.text.lower().strip() and
                                 j.label_ in self.entity_type_to_replace]
            if len(similar_type_ents) > 0:
                names_to_be_matched = pd.DataFrame({"name":[n.text for n in similar_type_ents],
                                                    "ent":similar_type_ents})
                names_to_be_matched.drop_duplicates(subset=['name'],inplace=True)
                name_to_match = pd.DataFrame({"name":[entities[i].text],
                                              "ent":[entities[i]]})
                self.matcher.load_and_process_master_data('name', names_to_be_matched)
                result = self.matcher.match_names(to_be_matched=name_to_match, column_matching='name').iloc[0]

                grouped_entities[entity_text_type] = group_id

                for j in range(self.number_of_matches):
                    if result['score_'+str(j)] >= self.matching_threshold:
                        match_entity_text_type = result['match_name_'+str(j)].lower().strip() + '_' + entities[i].label_
                        grouped_entities[match_entity_text_type] = group_id
                group_id += 1

        return grouped_entities

    def _redact_extracted_entities_and_write(self, doc, entities, file_name):
        redacted_text_map = {}
        entity_groups = self._group_similar_names(entities)
        redacted_text = doc.text[0:entities[0].start_char]
        original_redacted_map = []
        last_group_id = max(entity_groups.values()) + 1
        for i, ent in enumerate(entities):
            if ent.label_ in self.entity_types_to_mask or ent.label_ in self.entity_type_to_replace:

                text_based_replacement = redacted_text_map.get(ent.text.lower().strip()+ent.label_)
                if text_based_replacement is not None:
                    redacted_entity_text = text_based_replacement
                else:
                    redacted_entity_text, last_group_id = self._redact_entity(ent, entity_groups,last_group_id)
                    redacted_text_map[ent.text.lower().strip()+ent.label_] = redacted_entity_text
                redacted_text = redacted_text + redacted_entity_text + "$%#" + ent.text+"$%#"
                if i < len(entities) - 1:
                    redacted_text = redacted_text + doc.text[ent.end_char:entities[i + 1].start_char]
                else:
                    redacted_text = redacted_text + doc.text[entities[-1].end_char:]

                original_redacted_map.append({"original_text": ent.text,
                                              "original_span": (ent.start_char, ent.end_char),
                                              "entity_type": ent.label_,
                                              "redacted_text": redacted_entity_text})


        redaction_map_file_name = file_name.replace('.txt','_redaction_map.csv')
        original_redacted_df = pd.DataFrame(original_redacted_map)
        original_redacted_df.to_csv(os.path.join(self.redacted_output_path ,redaction_map_file_name), index=False)

        redacted_file_name = file_name.replace('.txt', '_redacted.txt')
        with open(os.path.join(self.redacted_output_path,redacted_file_name) , 'w') as f:
            f.write(redacted_text)

    def redact(self):
        for file_path in tqdm(glob.glob(self.input_dir_path + '/*.txt'),desc = 'Data Redaction'):
            text = open(file_path).read()
            doc = self.nlp(text)
            entities = [i for i in doc.ents]
            entities = sorted(entities, key=lambda x: x.start_char)
            file_name = os.path.basename(file_path)
            self._redact_extracted_entities_and_write(doc, entities,file_name)


if __name__ == '__main__':
    input_dir_path = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review/output/test'
    redacted_output_path = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review/output/test/redacted/'
    n = DataRedaction(input_dir_path, redacted_output_path)
    n.redact()

