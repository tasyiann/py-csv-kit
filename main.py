from utils import DataProcessing

if __name__ == '__main__':

    # Initiate Data Processor
    data_processor = DataProcessing("./data/pricat.csv", "./data/mappings.csv")

    # Format price catalogue using the mappings.
    updated_pricat = data_processor.format_pricat_with_mappings()

    # Export updated price catalogue in csv format.
    data_processor.export_in_csv(updated_pricat, "./results/mapped_pricat.csv")

    # Grouping process
    pass