from utils import DataMapping, DataGrouping

if __name__ == '__main__':

    # Initiate Mapping Data Processor
    mapping_processor = DataMapping("./data/pricat.csv", "./data/mappings.csv")

    # Format price catalogue using the mappings.
    mapping_processor.format_pricat_with_mappings("./results/mapped_pricat.csv")

    # Initiate Grouping Data Processor
    groupping_processor = DataGrouping("./results/mapped_pricat.csv")

    # Grouping : A Tree-based Method & Automatic detection of tiers (levels)
    groupping_processor.group(save_file="./results/group.json", max_tiers=3)

    # [A Different Approach on Grouping]: Tree-based, utilizing the dictionary keys.
    # Do not evaluate this method. It's just for fun & discussion.
    groupping_processor.group_key_based("./experimental_results/group_experimental.json")
