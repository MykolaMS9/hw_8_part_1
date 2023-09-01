import json

from models import Authors, Qoutes
import connect


def load_from_json(filename):
    with open(filename, encoding='utf-8') as file:
        file_data = json.load(file)
    return file_data


def main():
    filenames = ['authors.json', 'quotes.json']
    authors_filename = 'authors.json'
    quotes_filename = 'quotes.json'

    authors_obj = {}
    for author in load_from_json(authors_filename):
        authors_obj[author['fullname']] = Authors(
            fullname=author['fullname'],
            born_date=author['born_date'],
            born_location=author['born_location'],
            description=author['description']
        ).save()

    for quote_f in load_from_json(quotes_filename):
        quote_ = Qoutes(
            author=authors_obj[quote_f['author']],
            qoute=quote_f['quote'],
            tags=quote_f['tags']
        ).save()


if __name__ == '__main__':
    main()
    print('Done')
