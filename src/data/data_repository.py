import pandas as pd

from src.data.identifiers.identifier import Identifier

class DataRepository():
    """
    The DataRepository can hold any data, along with optional metadata; both identified by a 
      string identifier. You can also retrieve lists of identifiers based off of a filtering
      function with the filter calls.
    """

    def __init__(self):
        self._data = {}
        self._metadata = {}
    
    def add(self, identifier: Identifier, data: object, metadata: dict = {}):
        """
        Add data and metadata to the DataRepository with an Identifier, stores data and metadata
          in their respective dictionaries using the Identifier.
          
        Args:
            identifier (Identifier): The identifier for the data and metadata.
            data (object): The data to add
            metadata (dict): The metadata to add
        Returns:
            tuple[object, dict]: The data/metadata tuple.
        Raises:
            ValueError: The identifier is already in the repository, the metadata is None.
        """
        
        if(not issubclass(type(identifier), Identifier)):
            raise ValueError(f"Cannot add data for \"{identifier}\" identifier type \"{type(identifier)}\" is not a subclass of Identifier.")
        if(self.contains(identifier)):
            raise ValueError(f"Cannot add data for \"{identifier}\" it already exists in the repo.\nCurrent repo:\n  {"\n  ".join(str(key) for key in self._data.keys())}")
        if(metadata is None):
            raise ValueError(f"Metadata cannot be none.")

        self._data[identifier] = data
        self._metadata[identifier] = metadata

    def update_metadata(self, identifier: Identifier, metadata):
        """
        Update the metadata for a specific identifier.
          
        Args:
            identifier (Identifier): The identifier for the data and metadata.
            metadata (dict): The metadata to update

        Raises:
            ValueError: The identifier is already in the repository, the metadata is None.
        """
        if(not self.contains(identifier)):
            raise ValueError(f"Cannot update metadata for \"{identifier}\" it is not in the repo.")

        self._metadata[identifier] = metadata

    def remove(self, identifier: Identifier):
        """
        Remove the corresponding data and metadata from the repository.
          
        Args:
            identifier (Identifier): The identifier for the data and metadata.
        Raises:
            ValueError: The identifier is not in the repository.
        """
        if(not self.contains(identifier)):
            raise ValueError(f"Cannot remove data for \"{identifier}\" it is not in the repo.")

        self._data.pop(identifier)
        if(identifier in self._metadata):
            self._metadata.pop(identifier)

    def contains(self, identifier: Identifier) -> bool:
        """
        Check if the identifier is in the DataRepository.

        Args:
            identifier (Identifier): The identifier for the data and metadata.
        Returns:
            bool: Contains status.
        """
        return identifier in self._data.keys()

    def get(self, identifier: Identifier) -> tuple[object, dict]:
        """
        Get the corresponding data object and metadata dictionary as a tuple. Retrieving both in
          one call. Is a shortcut for the get_data & get_metadata calls.
          
        Args:
            identifier (Identifier): The identifier for the data and metadata.
        Returns:
            tuple[object, dict]: The data/metadata tuple.
        Raises:
            KeyError: The identifier is not in the repository.
        """
        if(not self.contains(identifier)):
            raise KeyError(f"Cannot get data/metadata for \"{identifier}\" it is not in the repo.")

        return (self.get_data(identifier), self.get_metadata(identifier))

    def get_data(self, identifier: Identifier) -> object:
        """
        Get the corresponding data object.
          
        Args:
            identifier (Identifier): The identifier for the data and metadata.
        Returns:
            object: The data object.
        Raises:
            KeyError: The identifier is not in the repository.
        """
        if(not self.contains(identifier)):
            raise KeyError(f"Cannot get data for \"{identifier}\" it is not in the repo.")

        return self._data[identifier]

    def get_metadata(self, identifier: Identifier) -> dict:
        """
        Get the corresponding metadata dictionary.
          
        Args:
            identifier (Identifier): The identifier for the data and metadata.
        Returns:
            dict: The metadata dictionary.
        Raises:
            KeyError: The identifier is not in the repository.
        """
        if(not self.contains(identifier)):
            raise KeyError(f"Cannot get metadata for \"{identifier}\" it is not in the repo.")
        if(identifier not in self._metadata.keys()):
            self._metadata[identifier] = {}

        return self._metadata[identifier]

    def get_ids(self):
        """
        Get the list of identifiers in the DataRepository.

        Returns:
            list[Identifier]: The list of identifiers.
        """
        return self._data.keys()

    def filter_ids(self, operation = lambda identifier: True) -> list:
        """
        Get a list of identifiers that satisfy an operation. The operation must return true/false.

        Args:
            operation (function): The operation to apply to each identifier.
        Returns:
            list[Identifier]: The list of identifiers that satisfy the operation.
        Raises:
            ValueError: Operation is none.    
        """
        if(operation is None):
            raise ValueError("Operation cannot be None.")

        out_list = []
        for identifier in self._data.keys():
            if(operation(identifier)):
                out_list.append(identifier)

        return out_list

    def get_chronological_periods(self):
        """
        Returns the set of periods identifying all DataFrames in sorted order.
        Guarantees: Unique periods, periods are ordered by starting order.
        """
        return sorted(set([full_identifier[0] for full_identifier in self.data_blocks.keys()]))

    def count(self):
        return len(self._data.keys())
    
    def print_summary(self):
        print("Summary of DataRepository:")
        for identifier in self.get_ids():
            data = self.get_data(identifier)
            datastr = ""
            if(isinstance(data, pd.DataFrame)):
                datastr = "DataFrame"
            else:
                datastr = str(data)
            print(f"ID {identifier}: \n  {"\n  ".join(datastr.split("\n"))}")
