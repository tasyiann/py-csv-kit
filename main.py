from utils import DataProcessing

if __name__ == '__main__':

    # Initiate Data Processor
    data_processor = DataProcessing("./data/pricat.csv", "./data/mappings.csv")

    # todo: Report any abnormalities & Discard any faulty mappings
    data_processor.sanitize_data()

    # Format price catalogue using the mappings.
    updated_header, updated_pricat = data_processor.format_pricat_with_mappings()

    # Export updated price catalogue in csv format.
    data_processor.export_in_csv(updated_header, updated_pricat, "./results/mapped_pricat.csv")

    # todo: Execute the Grouping process.
    # structured_dict = data_processor.create_structured_dictionary(updated_pricat)

    # todo: Export results.
    # data_processor.export_as_JSON(structured_dict, "./results/structured_data.json")
