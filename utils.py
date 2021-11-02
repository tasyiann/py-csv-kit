import csv          # Read/Write csv files.
import json         # json.dumps
import tree         # Custom tree with dictionaries.
import numpy as np  # np.unique


class DataMapping:

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

    def format_pricat_with_mappings(self, save_file=None):
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

        if save_file:
            self._export_in_csv(header_new, pricat_new, save_file)

        return header_new, pricat_new

    def _export_in_csv(self, header, pricat, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=";")
            writer.writeheader()
            for shoe_config in pricat:
                writer.writerow(shoe_config)

    def combine_fields_into_a_new_field(self, source_types, destination_type):
        pass

    # def create_catalogue_structure_using_grouping(self, pricat=None, tier_1_field="brand", tier_2_field="article_number"):
    #     # todo: The method is not correct!
    #     #       tier2 does not commune with tier1
    #     if not pricat:
    #         pricat=self.pricat
    #
    #     # Group into levels
    #     tier_2 = {'groups': {}, 'common_attributes': []}     # (e.g. Articles)
    #     tier_1 = {'groups': {}, 'common_attributes': []}     # (e.g. Catalogue)
    #
    #     for idx, shoe_config in enumerate(pricat):
    #         # Group tier 2 (e.g. by "article_number")
    #         if shoe_config[tier_2_field] not in tier_2['groups']:
    #             tier_2['groups'][shoe_config[tier_2_field]] = []
    #         tier_2['groups'][shoe_config[tier_2_field]].append(idx)
    #
    #         # Add new brands: Group tier 1 (e.g. by "brand")
    #         if shoe_config[tier_1_field] not in tier_1['groups']:
    #             tier_1['groups'][shoe_config[tier_1_field]] = []
    #
    #         # Add the Article to that brand:
    #         if shoe_config[tier_2_field] not in tier_1['groups'][shoe_config[tier_1_field]]:
    #             tier_1['groups'][shoe_config[tier_1_field]].append(shoe_config[tier_2_field])
    #
    #         # # Group tier 1 (e.g. by "brand")
    #         # if shoe_config[tier_1_field] not in tier_1:
    #         #     tier_1[shoe_config[tier_1_field]] = []
    #         # tier_1[shoe_config[tier_1_field]].append(shoe_config[])
    #
    #     return tier_1, tier_2
    #
    # def to_json_format(self, pricat, tier1, tier2):
    #     print("Catalog")
    #     for t1_key in tier1['groups']:
    #         print("\tbrand:%s" %t1_key)
    #         for t2_key in tier1['groups'][t1_key]:
    #             print("\t\tArticle\n\t\t\tarticle_number: "+t2_key)
    #             for t3_key in tier2['groups'][t2_key]:
    #                 print("\t\t\t\tVariation: %s" % pricat[t3_key])
    #
    #         #
    #         # for i in brands[brand_name]:
    #         #     # Tier 2: Articles for that brand
    #         #     article_num = pricat[i]['article_number']
    #         #     print("\t\tArticle\n\t\t\tarticle_number: "+article_num)
    #         #     for j in article_nums[article_num]:
    #         #         print("\t\t\t\tVariation: %d"%j)
    #
    # def export_as_JSON(self):
    #     pass

from collections import defaultdict
class DataGrouping:
    def __init__(self, pricat_filename="./data/pricat.csv"):
        self.pricat_header, self.pricat_data = self._read_csv_file(pricat_filename)
        self._remove_empty_columns()

    @staticmethod
    def _read_csv_file(file_name):
        data = list(csv.reader(open(file_name), delimiter=";"))
        pricat_header = data[0]
        pricat_data = np.array(data[1:])
        return pricat_header, pricat_data

    def _remove_empty_columns(self):
        empty_columns = []
        for i in range(len(self.pricat_header)):
            if all(self.pricat_data[:, i] == ''):
                empty_columns.append(i)
        self.pricat_header = np.delete(self.pricat_header, empty_columns)
        self.pricat_data = np.delete(self.pricat_data, empty_columns, axis=1)
        pass

    def _get_hierarchical_order(self):
        # Track uniqueness in each column.
        uniqueness = {}
        # Find unique values in each column.
        for i, column_name in enumerate(self.pricat_header):
            uniqueness[i] = np.unique(self.pricat_data[:, i])
        # Get order of hierarchy between columns.
        order_indices, _ = zip(*sorted(uniqueness.items(), key=lambda item: len(item[1])))
        order_indices = list(order_indices)
        return order_indices

    def group_recursively(self, save_file=None):
        # Sort columns in a hierarchical matter.
        # order_indices = self._get_hierarchical_order()
        tiers, order_indices = self._get_hierarchy_structure_modified()
        sorted_column_data = self.pricat_data[:, order_indices]
        sorted_column_names = list(self.pricat_header[order_indices])
        # Add rows in tree
        t = tree.tree()
        # root = {"catalog":tree.tree()}
        # my_tree = defaultdict(list)
        for row in sorted_column_data:
            tree.add(t, row, sorted_column_names)
            # tree.add_flat(t, row, sorted_column_names)
            # tree.add_x(my_tree, row, sorted_column_names, tiers)
        # Group recursively
        w = tree.dicts(t)
        # w = tree.normalize_dict(t, my_tree)
        # e = tree.exper(t)
        # p = tree.walk_dict(t)
        # h = tree.h
        # w = tree.dicts_x(t, my_tree, sorted_column_names, 0, tiers)
        json_str = w
        # json_str["'catalog'"] = w
        x = json.dumps(json_str, indent=4)\
            .replace(": {}", "")\
            .replace("\"", "")\
            .replace("'","\"") \
            .replace("{", "[{") \
            .replace("}", "}]").replace(": [{", ", \"get\": [{")\
            # .replace("\"catalog\", \"get\":", "\"catalog\":")
            # .replace("\"article_number\"", "\"Article\" : [\"article_number\"")\
        # more_structured = tree.prettify(t, tiers, sorted_column_names)
        pass
        # Save file
        if save_file:
            f = open(save_file, "w")
            f.write(x)
            f.close()
        return x

    def _get_hierarchy_structure_modified(self, max_tiers=3):
        # Track uniqueness in each column.
        uniqueness = {}
        # Find unique values in each column.
        for i, column_name in enumerate(self.pricat_header):
            uniqueness[i] = np.unique(self.pricat_data[:, i])
        # Get order of hierarchy between columns.
        order_indices, sorted_uniqueness = zip(*sorted(uniqueness.items(), key=lambda item: len(item[1])))
        order_indices = list(order_indices)
        # Sort column names
        # Merge, to create levels of hierarchy.
        structure = defaultdict(list)
        for col_id, x in enumerate(sorted_uniqueness):
            structure[len(x)].append(col_id)
        # Keep the max_tiers-1 separate and merge the rest.
        d = {}
        for i, x in enumerate(structure.values()):
            if i < max_tiers:
                d["tier_%d"%i] = x
            else:
                d["tier_%d" % (max_tiers-1)] += x
        pass
        return d, order_indices

    def group_b(self, save_file, max_tiers=3):
        # Get structure & sort
        tiers_structure, order = self._get_hierarchy_structure_modified(max_tiers)
        sorted_column_data = self.pricat_data[:, order]
        sorted_column_names = list(self.pricat_header[order])
        tiers_names = list(tiers_structure.keys())
        # Initialize tree
        root = defaultdict(list)
        root['catalog'] = defaultdict(list)
        # for tier_name in tiers_structure:
        #     root[tier_name] = []

        catalog = {'tier_0':
                       [
                           {'tier_1':
                                [
                                    {'tier_2':
                                         []
                                     }
                                ]
                           }
                       ]
        }

        # For each row
        for row in sorted_column_data:
            # Create the tier of that shoe_config
            parent = root['catalog']
            for tier_id, (tier_name, tier_attribute_ids) in enumerate(tiers_structure.items()):
                tier = defaultdict(list)
                for idx in tier_attribute_ids:
                    tier[sorted_column_names[idx]] = row[idx]

                # Child tier_name:
                if tier_id < len(tiers_structure)-1:
                    child_tier_name = tiers_names[tier_id+1]
                else:
                    child_tier_name = ""
                child = self.continue_chain(tier, parent[tier_name],tier_name, child_tier_name, parent)
                print("%s has a new sibling. It's len now: %d"% (tier_name, len(parent[tier_name])))
                parent = child

        # Traverse tree
        pass

    def continue_chain(self, item, tier, tier_name, child_tier_name, parent):
        for variation in tier:
            temp = variation.copy()
            if child_tier_name in temp:
                temp.pop(child_tier_name)
            if item == temp:
                return variation

        parent[tier_name].append(item)
        return item

























































    def _get_hierarchy_structure(self):
        # Track uniqueness in each column.
        uniqueness = {}
        # Find unique values in each column.
        for i, column_name in enumerate(self.pricat_header):
            uniqueness[column_name] = np.unique(self.pricat_data[:, i])
        # Sort column_names by their uniqueness.
        sorted_column_names = sorted(uniqueness.items(), key=lambda item: len(item[1]))
        # Merge, to create levels of hierarchy.
        structure = defaultdict(list)
        for x in sorted_column_names:
            structure[len(x[1])].append(x)
        return structure

    def _set_parents(self):
        structure = self._get_hierarchy_structure()
        pass

    def _get_parent(self, key, value, next_tier_array):
        next_tier_array[0].index()
        self._get_parent()
        print("parent: (%s:%s)" % ())

    def group(self, max_tiers=3):
        self._set_parents()





    def dicts(self, t):
        for k in t:
            return {k: self.dicts(t[k])}

    def group_3(self):
        # this one.
        import collections
        # Synthesize the hierarchy tree.
        structure = self._get_hierarchy_structure()
        structure = collections.OrderedDict(sorted(structure.items(), reverse=True))
        # Start from leaves (lowest tier)
        root = {}
        dict_tier = defaultdict(list)
        for tier_label, tier_attributes in structure.items():
            for attribute_name, attribute_values in tier_attributes:
                for value in attribute_values:
                    dict_tier[value].append(defaultdict(list))
            # pprint.pprint(dict_tier)



    def group_2(self):
        # Sort data
        structure, order_indices = self._get_hierarchy_structure()
        sorted_column_names = self.pricat_header[order_indices]
        sorted_column_data = self.pricat_data[:, order_indices]
        t = tree.tree()
        for row in sorted_column_data:
            tree.add(t, row)
        x = tree.dicts(t)
        jobj = json.dumps(x, indent=4)
        print(jobj)
        pass


    def get_occurrences_of_unique_values_2(self):
        d = {}
        for col, column_name in enumerate(self.pricat_header):
            occurrences_in_column = defaultdict(list)
            for row, value in enumerate(self.pricat_data[:, col]):
                occurrences_in_column[value].append(row)
            d[column_name] = occurrences_in_column
        sorted_d = sorted(d.items(), key=lambda item: len(item[1]))
        pass

    def hierarchical_sorted_pricat(self):
        pass

    def get_occurrences_of_unique_values_3(self):
        x = self.dicts(self.pricat_data)
        pass

