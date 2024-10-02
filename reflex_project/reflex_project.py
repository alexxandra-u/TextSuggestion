import reflex as rx

from reflex_project.text_suggestion import WordCompletor, NGramLanguageModel, TextSuggestion
from reflex_project.corpus_collection import collect_corpus, extract_corpus

data_path = "reflex_project/emails_processed.csv"
print('extracting corpus...')
corpus = extract_corpus(data_path)
print('creating word completor...')
word_completor = WordCompletor(corpus)
print('creating n_gram_model...')
n_gram_model = NGramLanguageModel(corpus=corpus, n=3)
print('creating text_suggestion...')
text_suggestion = TextSuggestion(word_completor, n_gram_model)
print('ready')


class State(rx.State):
    input_text: str = ""
    result: str = ""
    answer_color: str = "black"
    result_old_1: str = ""
    result_old_2: str = ""
    result_old_3: str = ""

    def search(self):
        if len(self.input_text.split()) < 3:
            self.result = 'Phrase is too short to continue'
            self.answer_color = 'red'
        else:
            text = self.input_text.lower().strip()
            result = ' '.join(text_suggestion.suggest_text(text, n_words=10, n_texts=1)[0])
            self.result_old_3 = self.result_old_2
            self.result_old_2 = self.result_old_1
            self.result_old_1 = self.result
            self.result = '...' + result
            self.answer_color = 'black'

    def clear(self):
        self.result = ''
        self.result_old_1 = ''
        self.result_old_2 = ''
        self.result_old_3 = ''

    def set_input_text(self, text):
        self.input_text = text


def index():
    return rx.center(
        rx.vstack(
            rx.icon("notepad-text", size=70),
            rx.heading("Text suggestion app", size='6'),
            rx.text("Enter the beginning of your text and clic 'Continue'", sm='8px'),
            rx.hstack(
                rx.input(
                    placeholder="Enter your text...",
                    on_change=lambda value: State.set_input_text(value),
                    width="500px",
                ),
                rx.button(
                    "Continue",
                    on_click=State.search,
                ),
                rx.button(
                    "Clear",
                    on_click=State.clear,
                    color_scheme='gray'
                ),
            ),
            rx.text(State.result, color=State.answer_color),
            rx.spacer(),
            rx.heading("История запросов", size='3'),
            rx.text(State.result_old_1, sm='10px', color='gray'),
            rx.text(State.result_old_2, sm='10px', color='gray'),
            rx.text(State.result_old_3, sm='10px', color='gray'),
            spacing="20px",
        ),
        height="100vh"
    )


app = rx.App()
app.add_page(index)
