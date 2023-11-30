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

# Load the English dictionary (https://github.com/dwyl/english-words/blob/master/words.txt)
english_dict_file_path = './data_location/data/words.txt'
english_words = load_english_dictionary(english_dict_file_path)

# Function to convert to ASCII and strip white spaces
def to_ascii_and_strip(text):
    text_ascii = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text_ascii.strip()

# Download required NLTK data and initialize the lemmatizer
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()

# Apply rules for each word - includes reducing words to their roots (lemmatization)
#  (https://www.educative.io/answers/difference-between-tokenization-and-lemmatization-in-nlp)
def preprocess_word(word):
    # Lowercase the word
    word = word.lower()
    # Expand contractions
    word = contractions.fix(word)
    # Remove special characters (keeping only alphanumeric and spaces)
    word = re.sub(r'[^a-zA-Z0-9\s]', '', word)
    # Remove punctuation at the ends of the word
    word = word.strip(string.punctuation)
    # Split hyphenated words and handle slashes
    words = re.split('-|/', word)
    # Process each word in the split
    processed_words = []
    for w in words:
        # Lemmatize the words
        w = lemmatizer.lemmatize(w)
        # Append processed word to the list
        processed_words.append(w)
    return processed_words

# Function to check for typos against the English dictionary
def check_typos(text, dictionary):
    tokens = text.split()
    processed_tokens = [preprocess_word(token) for token in tokens]
    flattened_tokens = [item for sublist in processed_tokens for item in sublist]
    corrected_tokens = []
    for token in flattened_tokens:
        if token.lower() not in dictionary:
            corrected_token = '[typo]'
        else:
            corrected_token = token
        corrected_tokens.append(corrected_token)
    return ' '.join(corrected_tokens)

# Apply the functions
data['location'] = data['location'].astype(str).apply(to_ascii_and_strip)
data['corrected_location'] = data['location'].apply(lambda x: check_typos(x, english_words))

# Counting the non-unique rows after typo correction
non_unique_counts = data['corrected_location'].value_counts()
non_unique_rows = non_unique_counts[non_unique_counts > 1]

# Results
non_unique_rows_count = len(non_unique_rows)
non_unique_rows_occurrences = non_unique_rows.sum()

# Displaying the final output
print(f"Number of non-unique rows: {non_unique_rows_count}")
print(f"Total occurrences of non-unique rows: {non_unique_rows_occurrences}")
print("Top non-unique rows:")
print(non_unique_rows.head())

# Exporting the corrected data to a CSV file
output_file = './data_location/outputs/ascii_typo.csv'
data.to_csv(output_file, index=False)
