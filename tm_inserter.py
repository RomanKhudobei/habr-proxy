import re

from bs4 import BeautifulSoup

from src.habr_proxy.utils import insert_tm_into_html


def get_html_string():
    with open('src/page.html', 'r', encoding='utf-8') as f:
        return f.read()


def insert_tm_regex(string):
    # pattern = r'>.*(?P<word>\w{6}).*<'
    # pattern = r'(?<=>.*)(?P<word>\w{6})(?=.*<)'
    # pattern = r'\w{6}\b'
    # pattern = r'>.*?(?P<word>\b\w{6}\b)'
    pattern = r'>[^<]*?(?P<word>\b\w{6}\b)[^>]*?<'

    for match in re.findall(pattern, string, re.DOTALL):
        print('match', type(match), dir(match))


def insert_tm_manual(string):
    string_with_tm = ''
    is_tag_markup = False
    ignore_tags = (
        'style',
        'script',
        'path',
        'svg',
    )
    tag_name = ''
    is_collecting_tag_name = False
    char_counter = 0

    for char in string:

        if char == '<':
            is_collecting_tag_name = True
            is_tag_markup = True
            char_counter = 0

        if char == '>':
            is_collecting_tag_name = False
            is_tag_markup = False
            char_counter = 0

        # check closing tag
        if char == '/':
            previous_char = string_with_tm[-1]

            if previous_char == '<':
                is_collecting_tag_name = False
                tag_name = ''

        if char in ' />':
            is_collecting_tag_name = False

        if is_tag_markup and is_collecting_tag_name:
            tag_name += char

        if not is_tag_markup and char in ' ()"\'' and tag_name not in ignore_tags:

            if char_counter == 6:
                string_with_tm += '™'

            string_with_tm += char
            char_counter = 0
            continue

        string_with_tm += char
        char_counter += 1

    return string_with_tm


def main():
    # html_string = get_html_string()
    # html_string = """<p>Согласно профилю LinkedIn, в 2010 году Mainsoft Corporation сменила название на Harmon™.ie (<a href="http://www.harmon™.ie" rel="noopener noreferrer nofollow">www.harmon™.ie</a>™).</p>"""
    html_string = """<html><body><img src="https://habrastorage.org/webt/gt/cy/4y/gtcy4yyx0cqp93kdwedc3lygpjw.jpeg"/><br/>
<p><i><a href="https://upload.wikimedia.org/wikipedia/en/4/4a/Giorgio_de_Chirico%2C_1917%2C_Il_grande_metafisico%2C_oil_on_canvas%2C_104.8_x_69.5_cm.jpg" rel="nofollow noopener noreferrer">Джорджо де Кирико™. Великий метафизик (The Grand Metaphysician), 1917</a>.<br/>
</i><br/>
Если посмотреть список хабов Хабра, то увидим, что в IT можно выделить много направлений. Для этой статьи возьмем классификацию попроще.</p><br/>
<p>1) CS — создание подходов, имеющих научную новизну. Разработка новых алгоритмов. Основная цель: научная новизна, развитие CS, решение проблем CS.</p><br/>
<p>2) Инженерно-конструкторская деятельность – комбинирование уже известных подходов (алгоритмов, ЯП, библиотек, технологий, исходных кодов), их адаптация под конкретную задачу™. Основная цель: создание продукта для решения конкретной практической задачи™.</p><br/>
<p>3) Техническое обеспечение — решение типовых (зачастую тривиальных) проблем в ходе эксплуатации “железа” и софта. Обеспечение бесперебойной работы™ ПО и оборудования с учетом™ возникающих требований.</p><br/>
<p>Очевидно, что в такой классификации риск неудачи убывает в каждом™ пункте™. При работе™ над новым алгоритмом или устройством обычно™ невозможно полностью гарантировать успех. При использовании уже известных алгоритмов, языков™, технологий, библиотек и готовых деталей машин – вероятность успешного исполнения работы™ возрастает. В последнем случае™ (обеспечение ) работник (должность может быть разная: инженер, системный программист, системный администратор и т.д.) исходит из минимизации замен по принципу: “не трогать то, что хорошо™ работает”.</p><br/>
<p>Как видим цели противоположные: для научной новизны бывают™ нужны новые рискованные решения, а для обеспечения – наоборот. Для успешной разработки продукта, желательно применять уже опробованные зарекомендовавшие себя решения, хотя при их отсутствии может понадобится и эксперимент, как в CS.</p><br/>
<p>Кому и насколько в IT нужна математика? — Попробуем ответить на этот вопрос™ (хотя бы частично).</p></body></html>"""

    # soup = BeautifulSoup(html_string, 'html.parser')
    # print('find', bool(soup.find()))
    # for el in soup.descendants:
    #     print('el', el)

    inserted_html_string = insert_tm_into_html(html_string)
    print(inserted_html_string)


if __name__ == '__main__':
    main()
