import csv


class DataProcessing:

    def __init__(self, pricat_filename="./data/pricat.csv", mappings_filename="./data/mappings.csv"):
        self.fieldnames, self.pricat = self._read_csv(pricat_filename)
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

    def _update_fieldnames(self, source_type, destination_type):
        if source_type in self.fieldnames:
            self.fieldnames.remove(source_type)
        if destination_type not in self.fieldnames:
            self.fieldnames.append(destination_type)

    def format_pricat_with_mappings(self):

        pricat_new = self.pricat.copy()

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
                        self._update_fieldnames(source_type, m['destination_type'])

        return pricat_new

    def export_in_csv(self, pricat, filename):
        # todo: remove empty columns?
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, delimiter=";")
            writer.writeheader()
            for shoe_config in pricat:
                writer.writerow(shoe_config)

    def combine_fields_into_a_new_field(self, source_types, destination_type):
        pass

