import pandas as pd



def get_books():
    book_cols = ['ISBN', 'Book-Title', 'Book-Author',
                 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
    books = pd.read_csv('BX-CSV-Dump/BX-Books.csv', sep=';',
                        names=book_cols, usecols=range(8), encoding='utf-8')

    return books
