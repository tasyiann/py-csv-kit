from utils import DataMapping, DataGrouping

if __name__ == '__main__':

    # Initiate Mapping Data Processor
    mapping_processor = DataMapping("./data/pricat.csv", "./data/mappings.csv")

    # Format price catalogue using the mappings.
    mapping_processor.format_pricat_with_mappings("./results/mapped_pricat.csv")

    # Initiate Grouping Data Processor
    groupping_processor = DataGrouping("./results/mapped_pricat.csv")

    # [Tree-based Method] Convert flat data to structured data.
    # groupping_processor.group_recursively("./results/group_recursively_test_A.json")

    # [Tree-based Method] Convert flat data to structured data.
    groupping_processor.group_b(save_file="./results/group_recursively_test_B.json", max_tiers=3)

    # [Non-recursive & 3-Depth] Convert flat data to structured data.
    # data = mapping_processor._read_csv("./results/mapped_pricat.csv")
    # by_brand, by_article_num = mapping_processor.create_catalogue_structure_using_grouping(updated_pricat)
    # mapping_processor.to_json_format(updated_pricat, by_brand, by_article_num)
