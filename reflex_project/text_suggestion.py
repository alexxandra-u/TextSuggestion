from collections import defaultdict, Counter
from typing import List, Tuple, Union


class PrefixTreeNode:
    def __init__(self):
        self.children: dict[str, PrefixTreeNode] = {}
        self.is_end_of_word = False


class PrefixTree:
    def __init__(self, vocabulary: List[str]):
        """
        vocabulary: список всех уникальных токенов в корпусе
        """
        self.root = PrefixTreeNode()

        # создаем дерево
        for word in vocabulary:
            node = self.root
            for char in word:
                # если такого листа еще не было, то создаем его
                if char not in node.children:
                    node.children[char] = PrefixTreeNode()
                node = node.children[char]
            node.is_end_of_word = True

    def search_prefix(self, prefix: str) -> List[str]:
        """
        Возвращает все слова, начинающиеся на prefix
        prefix: str – префикс слова
        """
        node = self.root
        for char in prefix:
            # префикса может вообще не быть
            if char not in node.children:
                return []
            node = node.children[char]
        # рекурсивно идем вниз по дереву
        return self.go_deeper(node, prefix)

    # функция, которая рекурсивно идет вниз по дереву в поиске слов
    def go_deeper(self, node: PrefixTreeNode, prefix: str) -> List[str]:
        words = []
        # если нашли конец слова, то добавляем его в результат
        if node.is_end_of_word:
            words.append(prefix)

        # идем глубже в детей искать дальше
        for char, child_node in node.children.items():
            words.extend(self.go_deeper(child_node, prefix + char))
        return words


class WordCompletor:
    def __init__(self, corpus: List[List[str]]):
        """
        corpus: list – корпус текстов
        """

        # Подсчет частоты слов и удаление редких
        self.word_frequencies = defaultdict(int)
        cnt_all = 0
        for texts in corpus:
            for word in texts:
                cnt_all += 1
                self.word_frequencies[word] += 1
        self.word_frequencies = {k: v/cnt_all for k, v in self.word_frequencies.items() if v/cnt_all >= 0.05}

        # Формирование дерева
        vocabulary = self.word_frequencies.keys()
        self.prefix_tree = PrefixTree(list(vocabulary))

    def get_words_and_probs(self, prefix: str):
        """
        Возвращает список слов, начинающихся на prefix,
        с их вероятностями (нормировать ничего не нужно)
        """
        words = self.prefix_tree.search_prefix(prefix)
        return words, [self.word_frequencies[word] for word in words]


class NGramLanguageModel:
    def __init__(self, corpus: List[List[str]], n: int):
        """
        corpus: список текстов, каждый текст - это список слов
        n: размерность n-граммы
        """
        self.n = n
        self.n_gram_counts = defaultdict(Counter)

        # Проходим по корпусу и сбор n-грамм
        for sentence in corpus:

            # дополняем фразы короче n
            if len(sentence) < n:
                for i in range(n-len(sentence)):
                    sentence.insert(0, '')

            # создаем n-граммы из остальных
            for i in range(len(sentence) - n):
                prefix = tuple(sentence[i:i + n])
                next_word = sentence[i + n]
                self.n_gram_counts[prefix][next_word] += 1

    def get_next_words_and_probs(self, prefix: List[str]) -> Tuple[List[str], List[float]]:
        """
        Возвращает список слов, которые могут идти после prefix,
        а также список вероятностей этих слов
        """
        prefix_tuple = tuple(prefix[-self.n:])
        next_words_counter = self.n_gram_counts.get(prefix_tuple, Counter())

        total_count = sum(next_words_counter.values())
        if total_count == 0:
            return [], []

        next_words = list(next_words_counter.keys())
        probs = [count / total_count for count in next_words_counter.values()]

        return next_words, probs


class TextSuggestion:
    def __init__(self, word_completor, n_gram_model):
        self.word_completor = word_completor
        self.n_gram_model = n_gram_model

    def suggest_text(self, text: Union[str, List[str]], n_words=3, n_texts=1) -> List[List[str]]:
        """
        Возвращает возможные варианты продолжения текста (по умолчанию только один)

        text: строка или список слов – написанный пользователем текст
        n_words: число слов, которые дописывает n-граммная модель
        n_texts: число возвращаемых продолжений (пока что только одно)

        return: list[list[str]] – список из n_texts списков слов, по 1 + n_words слов в каждом
        Первое слово – это то, которое WordCompletor дополнил до целого.
        """
        # Если входной текст строка, превращаем её в список слов
        if type(text) == str:
            text = text.split()

        suggestions = []
        current_suggestion = []
        current_suggestion.extend(text)

        if len(text) > 0:
            last_word = text[-1]
            words, probs = self.word_completor.get_words_and_probs(last_word)
            if words:
                # жадно выбираем слово
                best_index = probs.index(max(probs))
                best_word = words[best_index]
                current_suggestion[-1] = best_word
            else:
                # если не смогли дополнить, оставляем слово как есть
                current_suggestion[-1] = last_word

        for j in range(n_words):
            words, probs = self.n_gram_model.get_next_words_and_probs(current_suggestion)
            if words:
                # жадно выбираем слово
                best_index = probs.index(max(probs))
                best_word = words[best_index]
                current_suggestion.append(best_word)
            else:
                # если не знаем как продолжить, то не дополняем
                text = text[1:]
                break

        # Добавляем в итоговые предложения
        suggestions.append(current_suggestion[len(current_suggestion) - n_words - 1:])
        return suggestions

