from collections import Counter
import re
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dropbox 

#nltk.download('punkt')
#nltk.download('stopwords')

# Read the text from the file
DROPBOX_ACCESS_TOKEN= os.environ.get('DROPBOX_ACCESS_TOKEN')
# Dropbox file path
DROPBOX_FILE_PATH = "/taler.txt"

# Initialize Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)


# Download the file
metadata, response = dbx.files_download(DROPBOX_FILE_PATH)

    # Decode the content as a string and create a Pandas DataFrame
content_str = response.content.decode('utf-8')
text =  with open(file_path, 'r', encoding='utf-8') as file:
            t = file.read()

# Tokenize the text into words
words = nltk.word_tokenize(t)

# Get Danish stopwords and punctuation
stop_words = set(stopwords.words('danish'))
punctuation = set(string.punctuation)

# Remove stopwords and punctuation from the list of words
filtered_words = [word.lower() for word in words if word.lower() not in stop_words and word.lower() not in punctuation]

# Reconstruct the text from the filtered words
text = ' '.join(filtered_words)
#text = ' '.join(sorted(set(text.split()), key=text.split().index))

app = dash.Dash(__name__)



def calculate_word_probabilities(text):
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Split the text into words
    words = text.split()

    # Count the occurrences of each word
    word_counts = Counter(words)

    # Calculate the total number of words in the text
    total_words = len(words)

    # Calculate the probabilities of each word
    word_probabilities = [(word, count / total_words) for word, count in word_counts.items()]

    # Sort the word probabilities in descending order by probability
    word_probabilities = sorted(word_probabilities, key=lambda x: x[1], reverse=True)

    return word_probabilities

word_probabilities = calculate_word_probabilities(text)

app.layout = html.Div([
    html.H1("Word Probabilities Dashboard"),
    dcc.Input(id='word-input', type='text', value='', placeholder='Enter a word'),
    html.Div(id='output-container', children=[]),
    dcc.Graph(
        id='word-probabilities',
        figure={
            'data': [
                {'x': [word for word, _ in word_probabilities], 'y': [prob for _, prob in word_probabilities], 'type': 'bar', 'name': 'Word Probabilities'},
            ],
            'layout': {
                'title': 'Word Probabilities in the Text',
                'xaxis': {'title': 'Words'},
                'yaxis': {'title': 'Probabilities'}
            }
        }
    )
])

@app.callback(
    Output('output-container', 'children'),
    [Input('word-input', 'value')]
)
def update_output(selected_word):
    if selected_word:
        selected_word = selected_word.lower()
        probability = next((prob for word, prob in word_probabilities if word == selected_word), None)
        if probability is not None:
            return f'The probability of "{selected_word}" is {probability:.4f}'
        else:
            return f'Word "{selected_word}" not found in the text.'
    else:
        return ''

if __name__ == '__main__':
    app.run_server(debug=True, port=8090)
