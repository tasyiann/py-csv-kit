import csv          # Read/Write csv files.
import json         # json.dumps
import tree         # Custom tree with dictionaries.
import numpy as np  # np.unique
from collections import defaultdict


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

    def _get_hierarchy_structure(self, max_tiers=3):
        """
        Defines the tiers (level) by the uniqueness in each attribute.

        Pipeline:
        --------
            1.  We compute the number of unique values in each column, and we call it uniqueness.
                In that way, we automatically define the hierarchy in the JSON.

                defaultdict(<class 'list'>,
                {   1: [0, 1, 2, 3, 4, 5],
                    2: [6, 7, 8, 9],
                    3: [10, 11],
                    4: [12, 13],
                    7: [14, 15],
                    49: [16]
                })

                The above structure, will define the tiers in the JSON. For example:
                    - Attributes [0, 1, 2, 3, 4, 5] have only 1 possible value.
                    - Attributes [6, 7, 8, 9] have only 2 possible values.
                    - (...)


        :param max_tiers:
        :return:
        """
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
        return d, order_indices

    def group(self, save_file=None, max_tiers=3):
        """
        Creates a multi-tier data structure (JSON), from flat data.

        Pipeline:
        --------
            1. Automatically define the tiers (levels).
            2. Sort data.
            3. In each level, we keep track of the parent & the new child.
            4. Add a tier to the tree, only if new child does not already exist.

        :param save_file:
        :param max_tiers:
        :return:
        """
        # Get structure & sort
        tiers_structure, order = self._get_hierarchy_structure(max_tiers)
        sorted_column_data = self.pricat_data[:, order]
        sorted_column_names = list(self.pricat_header[order])
        tiers_names = list(tiers_structure.keys())

        # Initialize tree
        root = defaultdict(list)
        root['catalog'] = defaultdict(list)

        # For each row
        for row in sorted_column_data:
            # Create the tier of that shoe_config
            parent = root['catalog']
            for tier_id, (tier_name, tier_attribute_ids) in enumerate(tiers_structure.items()):
                tier = defaultdict(list)
                for idx in tier_attribute_ids:
                    tier[sorted_column_names[idx]] = row[idx]
                # Continue chain
                child = self.continue_chain(tier, parent[tier_name],tier_name, tier_id, tiers_structure, tiers_names, parent)
                parent = child

        # Traverse tree
        x = json.dumps(root, indent=4)
        if save_file:
            f = open(save_file, "w")
            f.write(x)
            f.close()
        print(x)

    def continue_chain(self, item, tier, tier_name, tier_id, tiers_structure, tiers_names, parent):
        # Child tier_name:
        if tier_id < len(tiers_structure) - 1:
            child_tier_name = tiers_names[tier_id + 1]
        else:
            child_tier_name = ""

        for variation in tier:
            temp = variation.copy()
            if child_tier_name in temp:
                temp.pop(child_tier_name)
            if item == temp:
                return variation
        # print("%s has a new sibling. It's len now: %d"% (tier_name, len(parent[tier_name])))
        parent[tier_name].append(item)
        return item

    def group_key_based(self, save_file=None):
        """
        EXPERIMENTAL
        -----------

        It's just for fun & discussion.
        Do not evaluate this method.

        This is a different approach on grouping.
        We let the dictionaries to do the job!

        First, we initialize a tree, which is a dict that has dict in his nodes, and so on...
        We sort the columns, then we add each attribute to the tree.
        The result would be something like this:
        (...):{"'size_name': '38'": {"'ean': '8719245200978'": {}},(..)

        It will need some modification on the JSON format.

        :param save_file:
        :return:
        """
        # Sort columns in a hierarchical matter.
        tiers, order_indices = self._get_hierarchy_structure()
        sorted_column_data = self.pricat_data[:, order_indices]
        sorted_column_names = list(self.pricat_header[order_indices])
        # Add rows in tree. That's it!
        t = tree.tree()
        for row in sorted_column_data:
            tree.add(t, row, sorted_column_names)
        # Simplify their type recursively: (from defaultdict(tree) to dict())
        w = tree.dicts(t)
        # This method does not return a correct JSON.
        x = json.dumps(w, indent=4)\
            .replace(": {}", "")\
            .replace("\"", "")\
            .replace("'","\"") \
            .replace("{", "[{") \
            .replace("}", "}]").replace(": [{", ", \"get\": [{")
        if save_file:
            f = open(save_file, "w")
            f.write(x)
            f.close()
        return x
