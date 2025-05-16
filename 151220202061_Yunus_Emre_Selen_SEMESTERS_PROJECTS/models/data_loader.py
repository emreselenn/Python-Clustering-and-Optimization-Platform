# File: models/data_loader.py
import numpy as np
import pandas as pd
from typing import Any

class DataLoader:
    """
    @class DataLoader
    @brief Loads numeric datasets from text files.

    The `DataLoader` class is responsible for loading numeric data from text files and returning 
    the data as a pandas DataFrame. It supports loading `.txt` files where data is separated by 
    whitespace and checks for the validity of the loaded data.
    """
    
    def load_txt(self, file_path: str) -> pd.DataFrame:
        """
        @brief Loads a .txt file containing numeric data into a DataFrame.

        This method reads a text file containing numeric data, parses the file into a pandas DataFrame, 
        and validates that the data has at least two columns.

        @param file_path: The path to the `.txt` file containing numeric data.
        @return: A pandas DataFrame containing the loaded numeric data.
        @throws ValueError: If the data is invalid (less than two columns) or missing.
        """
        try:
            # Load the data using pandas read_csv, assuming space-separated values
            df = pd.read_csv(file_path, sep="\s+", header=None)
            if df.shape[1] < 2:
                raise ValueError("Data must have at least two columns.")
            return df
        except Exception as e:
            # If any error occurs while loading, raise an exception
            raise ValueError(f"Failed to load data: {e}")
