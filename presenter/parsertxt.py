import re


class ParserText:
    """
    ParserText принимает file path или str и возвращает dict вида:
    {block_id -> int: data -> str}
    """

    __PATTERN_TEXT = r'\n\s+'

    def __init__(self, text_string: str):
        self.text_string = text_string

    def __parser_text(self, user_text: str) -> list:
        # проверяем наличие паттерна в тексте
        if re.search(self.__PATTERN_TEXT, user_text):
            # делаем split() по паттерну
            split_text = re.split(self.__PATTERN_TEXT, user_text)
            # заменяем \n на пробел для тех случаев, когда \n остается после применения паттерна
            return [(re.sub(r'[\n]', ' ', i)).capitalize() for i in split_text]
        # возвращаем текст с заменой \n на пробелы, если паттерн не обнаружен
        return [re.sub(r'[\n]', ' ', user_text).capitalize()]

    def __get_text(self) -> str:
        try:
            # определяем, является ли пользовательский ввод file path
            with open(self.text_string, 'r', encoding='UTF-8') as file:
                return file.read().strip()

        except Exception:
            # возвращаем пользовательский ввод без пробелов и табуляций в начале и в конце текста
            return self.text_string.strip()

    def get(self):
        text = self.__get_text()
        blocks_list = self.__parser_text(text)
        return {blocks_list.index(i): i for i in blocks_list}


if __name__ == '__main__':
    print(ParserText('Пошел на\nхуй.\n не балуйся, а то мы тебя накажем.\n  С уважением, Правообладатели.').get())
