import csv


class DataProcessing:

    def __init__(self, pricat_filename="./data/pricat.csv", mappings_filename="./data/mappings.csv"):
        self.pricat_header, self.pricat = self._read_csv(pricat_filename)
        _, self.mappings = self._read_csv(mappings_filename)

    def sanitize_data(self):
        # todo: discard any faulty mappings & report them
        pass

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

    def create_structured_dictionary(self, pricat=None):
        if not pricat:
            pricat=self.pricat

        for shoe_config in pricat:
            pass

    def export_as_JSON(self):
        pass