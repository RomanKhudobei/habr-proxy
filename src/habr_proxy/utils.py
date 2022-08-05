import json
import re

from bs4 import BeautifulSoup


def insert_tm_into_string(string):
    string_with_tm = ''
    char_counter = 0

    word_breakers = [' ', ',', '.', '!', '?', '(', ')', '"', "'", '«', '»', '–', '-' '\n', '\t']

    for char in string:

        if char in word_breakers:

            if char_counter == 6 and not string_with_tm[-6:].isnumeric():
                string_with_tm += '™'

            string_with_tm += char
            char_counter = 0
            continue

        string_with_tm += char
        char_counter += 1

    if char_counter == 6 and not string_with_tm[-6:].isnumeric():
        string_with_tm += '™'

    return string_with_tm


def is_html(string):
    return bool(BeautifulSoup(string, 'html.parser').find())


def insert_tm_into_dicts(obj: dict):

    for key, value in obj.items():
        # some key values is another keys, so if we modify them, then we will broke something.
        # also, this key values may hold titles, which we want to modify.
        # usually keys are not capitalized and titles are, so we use it as criteria
        if isinstance(key, str) and key == 'value' and isinstance(value, str) and value != value.capitalize():
            continue

        if isinstance(value, str):

            if not value.isdigit():
                if is_html(value):
                    obj[key] = insert_tm_into_html(value)
                else:
                    obj[key] = insert_tm_into_string(value)

            continue

        if isinstance(value, dict):
            obj[key] = insert_tm_into_dicts(value)
            continue

        if isinstance(value, list):

            for index, element in enumerate(value):

                if isinstance(element, str):

                    if not element.isdigit():
                        if is_html(element):
                            value[index] = insert_tm_into_html(element)
                        else:
                            value[index] = insert_tm_into_string(element)

                    continue

                if isinstance(element, dict):
                    value[index] = insert_tm_into_dicts(element)
                    continue

    return obj


def insert_tm_into_html(string):
    soup = BeautifulSoup(string, 'lxml')

    processed_elements = set()

    for element in soup.descendants:

        if element.__class__.__name__ == 'Tag':

            if element.string:

                if element.string in processed_elements:
                    continue

                if element.string.__class__.__name__ == 'Script':
                    element_string = str(element.string)
                    if '__INITIAL_STATE__' in element_string:
                        import logging
                        logger = logging.getLogger('default')
                        logger.debug(f'element_string {element}')
                        json_string = re.findall('\{.*\};', element_string)[0].strip(';')
                        logger.debug(f'json_string {json_string}')
                        initial_state = json.loads(json_string)
                        initial_state = insert_tm_into_dicts(initial_state)
                        logger.debug(f'modified_json {initial_state}')

                        def unicode_escape(s):
                            return "".join(map(lambda c: rf"\u{ord(c):04x}", s))

                        # print(unicode_escape(initial_state.get('articlesList').get('articlesList').get('586612').get('titleHtml')))
                        # print()
                        # print(json.dumps(initial_state).encode('unicode_escape').decode()[:1000])
                        # print()
                        # print(json.dumps(initial_state)[:1000])
                        element_string = re.sub('window.__INITIAL_STATE__.*\};', f"window.__INITIAL_STATE__={json.dumps(initial_state).encode('unicode_escape').decode()};", element_string)
                        # element_string = re.sub('window.__INITIAL_STATE__.*\};', f"window.__INITIAL_STATE__={unicode_escape(json.dumps(initial_state))};", element_string)
                        # element_string = re.sub('window.__INITIAL_STATE__.*\};', f"window.__INITIAL_STATE__={json.dumps(initial_state)};", element_string)
                        logger.debug(f'replaced_string {element_string}')
                        element.string.replace_with(element_string)
                        logger.debug(f'replaced_element {element.string}')
                        processed_elements.add(element.string)
                        continue

                if element.string.__class__.__name__ == 'NavigableString':
                    new_string = insert_tm_into_string(str(element.string))
                    element.string.replace_with(new_string)
                    processed_elements.add(element.string)

            else:
                # some text is not parsed in .string
                # so we need to find them!
                for child in element.children:

                    if child in processed_elements:
                        continue

                    if child.__class__.__name__ == 'NavigableString':
                        new_string = insert_tm_into_string(str(child))
                        child.replace_with(new_string)
                        processed_elements.add(child)

    return str(soup.html)
