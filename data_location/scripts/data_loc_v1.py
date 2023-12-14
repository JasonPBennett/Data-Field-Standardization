import pandas as pd
import unicodedata
import re
import string
import nltk
from nltk.stem import WordNetLemmatizer
import contractions

# Load the Excel file
excel_file_path = './data_location/data/data_location10_5_23.xlsx'
data = pd.read_excel(excel_file_path)

# Function to load a dictionary of English words
def load_english_dictionary(file_path):
    with open(file_path, 'r') as file:
        return {line.strip().lower() for line in file}

# Load the English dictionary
english_dict_file_path = './data_location/data/words.txt'
english_words = load_english_dictionary(english_dict_file_path)

# Function to convert to ASCII and strip white spaces
def to_ascii_and_strip(text):
    text_ascii = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text_ascii.strip()

# Initialize the lemmatizer
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()

# Function to preprocess and check for typos
def preprocess_and_check_typos(text, dictionary, is_strict):
    # Convert to lowercase, fix contractions, remove special characters
    text = text.lower()
    text = contractions.fix(text)
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    text = text.strip(string.punctuation)

    # Check for specific valid patterns first - maybe expand this?
    pattern = re.compile(r'\b(?:additional file) \d+\b', re.IGNORECASE)
    if pattern.search(text):
        return text  # Return as is if it matches the pattern

    # Split and process the rest of the text
    words = re.split('\s+|[-/]', text)  # Split on spaces, hyphens, and slashes
    processed_words = []
    for word in words:
        word = lemmatizer.lemmatize(word)  # Lemmatize the word
        if not is_strict and (word.lower() in dictionary or re.match(r'^\d+$', word)):
            processed_words.append(word)  # Keep numbers and dictionary words
        elif is_strict and word.lower() in dictionary:
            processed_words.append(word)  # Strict check: only keep dictionary words
        else:
            processed_words.append('[typo]')  # Mark as typo
    return ' '.join(processed_words)

# Apply the functions
data['location'] = data['location'].astype(str).apply(to_ascii_and_strip)
data['corrected_location_strict'] = data['location'].apply(lambda x: preprocess_and_check_typos(x, english_words, True))
data['corrected_location_numeric_allowed'] = data['location'].apply(lambda x: preprocess_and_check_typos(x, english_words, False))

# Exporting the data to a CSV file
output_file = './data_location/outputs/ascii_typo_comparison.csv'
data.to_csv(output_file, index=False)
