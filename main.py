from utils import DataProcessing

if __name__ == '__main__':

    # Initiate Data Processor
    catalog_processor = DataProcessing("./data/pricat.csv", "./data/mappings.csv")

    # Format price catalogue using the mappings.
    catalog_processor.format_pricat_with_mappings()

    # Export updated price catalogue in csv format.
    catalog_processor.export_pricat_in_csv("./results/mapped_pricat.csv")
