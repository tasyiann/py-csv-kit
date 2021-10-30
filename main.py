from utils import DataProcessing

if __name__ == '__main__':

    # Initiate Data Processor
    data_processor = DataProcessing("./data/pricat.csv", "./data/mappings.csv")

    # Format price catalogue using the mappings.
    updated_header, updated_pricat = data_processor.format_pricat_with_mappings()

    # Export updated price catalogue in csv format.
    data_processor.export_in_csv(updated_header, updated_pricat, "./results/mapped_pricat.csv")

    # Create the structure of the Catalogue, using Grouping.
    tier1_group_by = "brand"  # todo: Do it automatically determine that field (the one with the most similarities))
    # todo: export multiple variations of that Grouping Catalogue (each different from the group_by value)
    tier2_group_by = "article_number"
    by_brand, by_article_num = data_processor.create_catalogue_structure_using_grouping(updated_pricat)

    # To JSON
    data_processor.to_json_format(updated_pricat, by_brand, by_article_num)
