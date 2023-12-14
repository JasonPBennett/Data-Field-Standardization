import pandas as pd
import unicodedata
import json
import re

# Function to check if a string matches a given pattern based on specific id
# type - only counts (change this to labeling function later)
def conforms_to_pattern(text, id_type):
    if id_type == "PDB" and bool(re.match(r'pdb [A-Za-z0-9]{4}$', text)):
        return True
    elif id_type == "WEB" and bool(re.match(r'^https://hla-ligand-atlas.org/peptide/', text)):
        return True
    else:
        return False

def combine_rows(loc_df):
    """
    Processes a DataFrame containing location data. Combines rows with
    identical 'location' values while summing their 'location_count', sorts 
    the data in descending order based on 'location_count', and rearranges the
    columns.

    :param loc_df: The DataFrame file containing location data.
    :return: A DataFrame with processed location data.
    """

    # Combining rows with the same 'location' and summing their 'location_count'
    combined_locations_df = loc_df.groupby('location').sum().reset_index()

    # Sorting the combined data in descending order by 'location_count'
    sorted_locations_df = combined_locations_df.sort_values(by='location_count', ascending=False).reset_index(drop=True)

    # Rearranging columns so 'location_count' comes before 'location'
    rearranged_locations_df = sorted_locations_df[['location_count', 'location']]

    return rearranged_locations_df

def location_spellcheck(location, location_dict):
    """
    Spell checks a location string using data from a JSON file containing 
    approved locations and their common typos or synonyms. Each word in the 
    location is checked individually.

    :param location: The location string to be spell-checked.
    :param location_dict: The dict containing approved locations and their 
                          common typos or synonyms.
    :return: Spell-checked location string.
    """
    # Split the location into individual words
    words = location.split()

    # Spellcheck each word
    corrected_words = []
    for word in words:
        corrected_word = word
        for approved_location, loc_options in location_dict.items():
            if word in loc_options:
                corrected_word = approved_location
                break
        corrected_words.append(corrected_word)

    # Reassemble the location string
    corrected_location = ' '.join(corrected_words)
    return corrected_location

def standardize_location(location):
    """
    Standardizes a location string by removing unnecessary whitespaces,
    converting to ASCII, and converting to lowercase.

    :param location: The location string to be standardized.
    :return: Standardized location string.
    """
    # Remove unnecessary whitespaces
    location = location.strip()

    # Convert to ASCII
    location = unicodedata.normalize('NFKD', location).encode('ascii', 'ignore').decode('ascii')

    # Convert to lowercase
    location = location.lower()

    return location

if __name__ == "__main__":
    # Data and spellcheck file paths
    file_path = './data_location/data/location_and_counts.csv'
    spellcheck_file = './data_location/data/common_corrections.json'
    locations_df = pd.read_csv(file_path)
    with open(spellcheck_file, 'r') as file:
        location_dict = json.load(file)
    
    # Process location data and standardize location names
    processed_locations_df = combine_rows(locations_df)
    print(processed_locations_df.head())
    processed_locations_df['location'] = processed_locations_df['location'].apply(standardize_location)
    print(f'Number of locations (uncorrected & uncombined): {len(processed_locations_df)}\n')
    
    # Combine locations with identical names
    processed_locations_df = combine_rows(processed_locations_df)
    print(processed_locations_df.head())
    print(f'Number of locations (uncorrected & combined): {len(processed_locations_df)}\n')
    
    # Perform spellcheck on location names
    processed_locations_df['location'] = processed_locations_df['location'].apply(location_spellcheck, args=(location_dict,))
    processed_locations_df = combine_rows(processed_locations_df)
    print(processed_locations_df.head())
    print(f'Number of locations (corrected & combined): {len(processed_locations_df)}\n')
    
    # Output to csv for quick checking
    #processed_locations_df.to_csv('~/Desktop/processed_locations_spellcheck.csv', index=False)
    
    # Find number of locations that match each pattern and type
    print(processed_locations_df['location'].apply(lambda x: conforms_to_pattern(x, 'WEB')).value_counts()) # 221,254
    print(processed_locations_df['location'].apply(lambda x: conforms_to_pattern(x, 'PDB')).value_counts()) # 1,705