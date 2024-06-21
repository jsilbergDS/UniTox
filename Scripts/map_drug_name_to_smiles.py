"""Map drug names to SMILES using PubChem."""
import requests
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from tqdm import tqdm


# Get SMILES
def get_smiles_from_pubchem(drug_name: str) -> list[str] | None:
    """Looks up a drug name in PubChem to identify its SMILES.

    :param drug_name: The name of the drug.
    :return: The SMILES associated with this drug name. If the drug name has an exact match (case insensitive)
        to a name in PubChem, then only the SMILES associated with that name are returned. If there is no exact
        match, then all SMILES found are returned. If no match is found, None is returned.
    """
    # Lower case drug name
    drug_name = drug_name.lower()

    # Set up PubChem URL
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/property/CanonicalSMILES,Title/JSON"

    # Make PubChem API call
    response = requests.get(url)

    # Process PubChem API response
    if response.status_code == 200:
        data = response.json()

        # Canonicalize SMILES using RDKit
        all_smiles = [
            Chem.MolToSmiles(Chem.MolFromSmiles(prop['CanonicalSMILES']))
            for prop in data['PropertyTable']['Properties']
        ]

        # Get lower case titles
        titles = [prop['Title'].lower() for prop in data['PropertyTable']['Properties']]

        # Map each unique title to all possible canonical SMILES
        title_to_smiles = defaultdict(list)
        for smiles, title in zip(all_smiles, titles):
            title_to_smiles[title].append(smiles)

        # Deduplicate SMILES while preserving order
        for title, in list(title_to_smiles):
            title_to_smiles[title] = list(dict.fromkeys(title_to_smiles[title]))

        # Error if no SMILES found
        if len(all_smiles) == 0:
            raise ValueError(f"No SMILES found for {drug_name}")

        # If exact drug name match, get only those SMILES, otherwise get all SMILES
        selected_smiles = title_to_smiles.get(drug_name, all_smiles)

        return selected_smiles
    else:
        return None


def map_drug_names_to_smiles(
        data_path: Path,
        drug_name_column: str = "generic_name",
        smiles_column: str = "smiles",
        all_smiles_column: str = "all_smiles",
        smiles_delimiter: str = "|",
) -> None:
    """Map drug names to SMILES using PubChem.

    :param data_path: Path to CSV file containing drug names.
    :param drug_name_column: Name of the column in data_path containing drug names.
    :param smiles_column: Name of the column where one SMILES matching the drug name will be saved.
    :param all_smiles_column: Name of the column where all SMILES matching the drug name will be saved.
    :param smiles_delimiter: The delimiter between SMILES in the all_smiles_column.
    """
    # Load data
    data = pd.read_csv(drug_name_column)

    # Map drug names to all SMILES
    all_smiles = [get_smiles_from_pubchem(drug_name) for drug_name in tqdm(data["generic_name"])]

    # Get individual SMILES (first among available SMILES)
    data[smiles_column] = [smiles_list[0] for smiles_list in all_smiles]

    # Join all SMILES
    data[all_smiles_column] = [smiles_delimiter.join(smiles_list) for smiles_list in all_smiles]

    # Save data
    data.to_csv(data_path, index=False)
