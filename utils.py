import csv
import json
import numpy as np
from itertools import groupby

class DataProcessing:

    def __init__(self, pricat_filename="./data/pricat.csv", mappings_filename="./data/mappings.csv"):
        self.pricat_header, self.pricat = self._read_csv(pricat_filename)
        _, self.mappings = self._read_csv(mappings_filename)

    @staticmethod
    def _read_csv(file_name):
        csv_reader = csv.DictReader(open(file_name), delimiter=";")
        return csv_reader.fieldnames, [dict(d) for d in csv_reader]

    @staticmethod
    def _mapping_detector(m, source_types, shoe_config):
        source_values = m['source'].split('|')
        for source_value, source_type in zip(source_values, source_types):
            if source_type not in shoe_config or shoe_config[source_type] != source_value:
                return False
        return True

    @staticmethod
    def _update_header(header, source_type, destination_type):
        if source_type in header:
            header.remove(source_type)
        if destination_type not in header:
            header.append(destination_type)

    def format_pricat_with_mappings(self):
        # todo: try other methods instead of brute force.
        #       do plots and explain the improvements
        #       Maybe see it as a 2D matrix? + 1D of fields?
        pricat_new = self.pricat.copy()
        header_new = self.pricat_header.copy()

        for m in self.mappings:

            # Get all "sub" source_types. (e.g. : size_group_code|size_code)
            source_types = m['source_type'].split('|')
            for shoe_config, shoe_config_new in zip(self.pricat, pricat_new):

                # Do the mapping:
                if self._mapping_detector(m, source_types, shoe_config):
                    shoe_config_new[m['destination_type']] = m['destination']

                # Remove the old source type (from pricat_new) if it's mapped to a different type.
                for source_type in source_types:
                    if source_type in shoe_config_new and source_type != m['destination_type']:
                        shoe_config_new.pop(source_type)
                        self._update_header(header_new, source_type, m['destination_type'])

        return header_new, pricat_new

    def export_in_csv(self, header, pricat, filename):
        # todo: remove empty columns?
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=";")
            writer.writeheader()
            for shoe_config in pricat:
                writer.writerow(shoe_config)

    def combine_fields_into_a_new_field(self, source_types, destination_type):
        pass

    def create_catalogue_structure_using_grouping(self, pricat=None, tier_1_field="brand", tier_2_field="article_number"):
        # todo: The method is not correct!
        #       tier2 does not commune with tier1
        if not pricat:
            pricat=self.pricat

        # Group into levels
        tier_2 = {'groups': {}, 'common_attributes': []}     # (e.g. Articles)
        tier_1 = {'groups': {}, 'common_attributes': []}     # (e.g. Catalogue)

        for idx, shoe_config in enumerate(pricat):
            # Group tier 2 (e.g. by "article_number")
            if shoe_config[tier_2_field] not in tier_2['groups']:
                tier_2['groups'][shoe_config[tier_2_field]] = []
            tier_2['groups'][shoe_config[tier_2_field]].append(idx)

            # Add new brands: Group tier 1 (e.g. by "brand")
            if shoe_config[tier_1_field] not in tier_1['groups']:
                tier_1['groups'][shoe_config[tier_1_field]] = []

            # Add the Article to that brand:
            if shoe_config[tier_2_field] not in tier_1['groups'][shoe_config[tier_1_field]]:
                tier_1['groups'][shoe_config[tier_1_field]].append(shoe_config[tier_2_field])

            # # Group tier 1 (e.g. by "brand")
            # if shoe_config[tier_1_field] not in tier_1:
            #     tier_1[shoe_config[tier_1_field]] = []
            # tier_1[shoe_config[tier_1_field]].append(shoe_config[])

        return tier_1, tier_2

    def to_json_format(self, pricat, tier1, tier2):
        # todo: this is not it!
        #       we need to merge more fileds than the brand or article_number. I'm sorry.
        #       Can you do it merge more fields? Like select the fileds to be merged or something?
        #       Is there a structure to use to help us do this thing? Set or tree or something?
        print("Catalog")
        for t1_key in tier1['groups']:
            print("\tbrand:%s" %t1_key)
            for t2_key in tier1['groups'][t1_key]:
                print("\t\tArticle\n\t\t\tarticle_number: "+t2_key)
                for t3_key in tier2['groups'][t2_key]:
                    print("\t\t\t\tVariation: %s" % pricat[t3_key])

            #
            # for i in brands[brand_name]:
            #     # Tier 2: Articles for that brand
            #     article_num = pricat[i]['article_number']
            #     print("\t\tArticle\n\t\t\tarticle_number: "+article_num)
            #     for j in article_nums[article_num]:
            #         print("\t\t\t\tVariation: %d"%j)

    def export_as_JSON(self):
        pass