import json
import random
import requests

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

# Create your views here.
from taggit.models import Tag

from books_library.books.models import Book, Category
from books_library.users.models import User
from books_library.navigation.models import BookHistory
from books_library.recomendation.models import Recommender
from books_library.recomendation import collaborative_filtering as recsys


class Decoder(json.JSONDecoder):
    def decode(self, s):
        result = super(Decoder, self).decode(s)  # result = super(Decoder, self).decode(s) for Python 2.x
        return self._decode(result)

    def _decode(self, o):
        if isinstance(o, str) or isinstance(o, unicode):
            try:
                return int(o)
            except ValueError:
                return o
        elif isinstance(o, dict):
            return {k: self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o

@login_required
def suggestion(request):
    """ Suggest books according to the logged in user profile data"""
    books = Book.objects.all()
    categories = Category.objects.all()
    tags = Tag.objects.all()

    user = request.user
    dataset = {}
    all_users = User.objects.all()
    dataset = {}
    with open('books_library/recomendation/result.json') as data_file:
        dataset = json.load(data_file, cls=Decoder)
    recsys.dataset = dataset
    # import pdb; pdb.set_trace()
    rec_books = [rec_book for _, rec_book in recsys.user_recommendations_pearson(user.id, 100)]
    print rec_books
    books_no_sort = Book.objects.in_bulk(rec_books)
    books = [books_no_sort[int(id)] for id in rec_books]

    # Show 25 contacts per page
    paginator = Paginator(books, 25)

    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        books = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        books = paginator.page(paginator.num_pages)

    context = {
        "books": books,
        'categories' : categories,
        'tags' : tags
    }
    return render(request, 'recomendation/suggestion.html', context)


def get_rec(book_id):
    rec = Recommender.objects.get(name='my-recommender')
    return rec.similar_books(book_id=book_id)['payload']
