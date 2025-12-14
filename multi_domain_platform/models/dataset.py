#Applying OOP to the datasets.py from week8

#defining class for Dataset
class Dataset:
    """Represents a dataset."""

    #securing all my columns from datasets.py(week8)
    def __init__(
        self,
        dataset_id: int,
        dataset_name: str,
        category: str,
        source: str,
        last_updated: str,
        record_count: int,
        file_size_mb: float,
        created_at: str
    ):  
        #making it privates with __
        self.__id = dataset_id
        self.__dataset_name = dataset_name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb
        self.__created_at = created_at

    #gettings from lab and filling the remaining columns from my datasets.py
    def get_datasetID(self) -> int:
        return self.__id
    
    def get_dataset_name(self) -> str:
        return self.__dataset_name

    def get_category(self) -> str:
        return self.__category

    def get_source(self) -> str:
        return self.__source

    def get_last_updated(self) -> str:
        return self.__last_updated

    def get_record_count(self) -> int:
        return self.__record_count

    def get_file_size_mb(self) -> float:
        return self.__file_size_mb

    def get_created_at(self) -> str:
        return self.__created_at

    def is_large(self) -> bool:
        """Return True if dataset is larger than 100 MB."""
        return self.__file_size_mb >= 100

    def __str__(self) -> str:
        return (
            f"Dataset {self.__id}: {self.__dataset_name} "
            f"(Category: {self.__category}, {self.__file_size_mb} MB, "
            f"{self.__record_count} records, source={self.__source}, "
            f"last updated={self.__last_updated}, created at={self.__created_at})"
        )
"""   
#testing and printing example
test = Dataset(
    1,
    "wada12",
    "Sales",
    "external",
    "2025-12-03",
    12344,
    250,
    "2025-11-13"
)

print(test)"""
