import random

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib import messages
import json

from books_library.navigation.sentiment import get_sentiment, POSITIVE
from books_library.recomendation.views import get_rec
from books_library.users.models import User
from .forms import BookForm, CommentCreateForm
from .models import Book, Category

from ..navigation.models import Search, BookHistory
from books_library.recomendation import collaborative_filtering as recsys


def index(request, category_slug=None, search_terms=None):
    # Get all the books
    books = Book.objects.all()
    books_length = len(books)

    # Get all users
    users = User.objects.all()

    # Get all the categories
    categories = Category.objects.all()

    # Init the search terms
    search = None

    print search_terms
    print category_slug

    # If request is post
    if request.method == 'POST':
        search = request.POST.get('search')

    # If search by category and search terms
    if search_terms and search_terms != 'None':
        search = search_terms

    # Category filter
    if category_slug:
        books = books.filter(categories__slug=category_slug)

    # Search filter
    if search:
        # Split the search into terms
        terms = search.split(',')

        # Decalre an empty query
        q_books = Q()

        # Go through each term
        for term in terms:
            q_books |= Q(name__contains=term)
            q_books |= Q(author__contains=term)
            q_books |= Q(tags__name__contains=term)
            q_books |= Q(tags__slug__contains=term)

        books = books.filter(q_books).distinct()

        books_length = len(books)


        # Decalre an empty query
        q_users = Q()

        # Go through each term
        for term in terms:
            q_users |= Q(name__contains=term)
            q_users |= Q(username__contains=term)
            q_users |= Q(email__contains=term)

        users = users.filter(q_users).distinct()

        # If the search has results, save the searched terms
        if len(books) > 0 and request.user.is_authenticated():
            # Create a new search history entry and save it into the
            # logged in user history fields
            search_history = Search()
            search_history.terms = search
            search_history.save()

            # Save the search history with the logged in user
            request.user.history.searchs.add(search_history)

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
        'books': books,
        'categories': categories,
        'users': users,
        'category_slug': category_slug,
        'search': search,
        'books_length' : books_length
    }
    return render(request, 'books/index.html', context)

def search_terms(request, search_terms=None):
    # Get all the books
    books = Book.objects.all()
    books_length = len(books)

    # Get all users
    users = User.objects.all()

    # Get all the categories
    categories = Category.objects.all()

    # Init the search terms
    search = None

    # If request is post
    if request.method == 'POST':
        search = request.POST.get('search')

    # If search by category and search terms
    if search_terms and search_terms != 'None':
        search = search_terms

    # Search filter
    if search:
        # Split the search into terms
        terms = search.split('-')

        # Decalre an empty query
        q_books = Q()

        # Go through each term
        for term in terms:
            q_books |= Q(name__contains=term)
            q_books |= Q(author__contains=term)
            q_books |= Q(tags__name__contains=term)
            q_books |= Q(tags__slug__contains=term)

        books = books.filter(q_books).distinct()

        books_length = len(books)


        # Decalre an empty query
        q_users = Q()

        # Go through each term
        for term in terms:
            q_users |= Q(name__contains=term)
            q_users |= Q(username__contains=term)
            q_users |= Q(email__contains=term)

        users = users.filter(q_users).distinct()

        # If the search has results, save the searched terms
        if len(books) > 0 and request.user.is_authenticated():
            # Create a new search history entry and save it into the
            # logged in user history fields
            search_history = Search()
            search_history.terms = search
            search_history.save()

            # Save the search history with the logged in user
            request.user.history.searchs.add(search_history)

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
        'books': books,
        'categories': categories,
        'users': users,
        'category_slug': '',
        'search': search,
        'books_length' : books_length
    }
    return render(request, 'books/index.html', context)


class BookDetailView(DetailView):
    model = Book

    def get_object(self):
        """Return the requested book and save the navigation"""
        # Get the object from the super class method
        book = super(BookDetailView, self).get_object()

        # If the user is logged in, save the book history actions
        if self.request.user.is_authenticated():

            # Get the logged in user
            user = self.request.user

            # If the user has not viewed the book, create a new BookAction model and save
            # in the user history field
            if not user.history.books_action.filter(book=book).exists():
                book_actions = BookHistory(book=book, viewed=True)
                book_actions.score += 1
                book_actions.save()
                user.history.books_action.add(book_actions)
            else:
                books_action = user.history.books_action.get(book=book)
                if not books_action.viewed:
                    books_action.viewed = True
                    books_action.score += 1
                    books_action.save()

        return book

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        # Setup the commenting form
        context['form'] = CommentCreateForm()
        if self.request.user.is_authenticated():
            # Get the logged in user
            user = self.request.user
        dataset = {}
        try:
            if user:
                all_users = User.objects.all()
                # import pdb; pdb.set_trace()
                # for person in all_users:
                #     rated_books = person.history.books_action.all()
                #     for rated_book in rated_books:
                #         if person.id not in dataset:
                #             dataset[person.id] = {rated_book.book.id : rated_book.sc}
                #         else:
                #             dataset[person.id][rated_book.book.id] = rated_book.sc
                with open('books_library/recomendation/result.json') as data_file:
                    dataset = json.load(data_file)
                recsys.dataset = dataset
                rec_books = [rec_book for _, rec_book in recsys.user_recommendations_pearson(user.id, 100)]
                print rec_books
                books_no_sort = Book.objects.in_bulk(rec_books)
                books = [books_no_sort[int(id)] for id in rec_books]
                # Recommended books
                context['rec_books'] = books[:10]
            else:
                context['rec_books'] = Book.objects.all()[:10]
        except:
            context['rec_books'] = Book.objects.all()[:10]

        return context

class BookDetailReadView(BookDetailView):
    model = Book
    template_name = 'books/book_read.html'


class BookCreateView(CreateView):
    model = Book
    form_class = BookForm


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm


@login_required
def book_read(request, slug):
    """Returns the book link pdf"""
    # Get the logged in user
    user = request.user

    # Get the Book to read
    book = get_object_or_404(Book, slug=slug)

    # If the user has a book history
    if user.history.books_action.filter(book=book).exists():
        book_action = user.history.books_action.get(book=book)
        if not book_action.read:
            book_action.read = True
            book_action.score += 1
            book_action.save()

    else:
        book_action = BookHistory(book=book)
        book_action.read = True
        book_action.score += 1
        book_action.save()
        user.history.books_action.add(book_action)

    # Return the PDF link
    return render(request, 'books/book_read.html', {'book' : book})


@login_required
def book_like(request, id):
    """Take the id of the book to like"""
    try:
        # Get the logged in user
        user = request.user

        # Get the Book to read
        book = get_object_or_404(Book, pk=id)

        # If the book is in the user history
        if user.history.books_action.filter(book=book).exists():
            book_history = user.history.books_action.get(book=book)

            if not book_history.liked:
                book_history.liked = True
                book_history.score += 1
                book_history.save()

                book.likes.add(user)
                book.save()
            else:
                res = JsonResponse({'message': "Can't like a book more then one time"})
                res.status_code = 400
                return res
        else:
            book_history = BookHistory(book=book)
            book_history.liked = True
            book_history.score += 1
            book_history.save()
            user.history.books_action.add(book_history)

            # Increse the like by one
            book.likes.add(user)
            book.save()

        return JsonResponse({'message': 'book {0} is liked by the user {1}'.format(book.name, user.username),
                             'likes': book.likes.count()})

    except:
        res = JsonResponse({'message': 'error'})
        res.status_code = 400
        return res


@login_required
def book_dislike(request, id):
    """Take the id of the book to dislike"""
    try:
        # Get the logged in user
        user = request.user

        # Get the Book to read
        book = get_object_or_404(Book, pk=id)

        # If the book is in the user history
        if user.history.books_action.filter(book=book).exists():
            book_history = user.history.books_action.get(book=book)

            if book_history.liked:
                book_history.liked = False
                book.likes.remove(user)
                book.save()
            else:
                res = JsonResponse({'message': "Can't dislike a book more then one time"})
                res.status_code = 400
                return res

            book_history.save()

        return JsonResponse({'message': 'book {0} is disliked by the user {1}'.format(book.name, user.username),
                             'likes': book.likes.count()})

    except:
        res = JsonResponse({'message': 'error'})
        res.status_code = 400
        return res


@login_required
def book_bookmark(request, id):
    """Take the id of the book to bookmark"""
    try:
        # Get the logged in user
        user = request.user

        # Get the Book to read
        book = get_object_or_404(Book, pk=id)

        # If the book is in the user history
        if user.history.books_action.filter(book=book).exists():
            book_history = user.history.books_action.get(book=book)

            if not book_history.bookmarked:
                book_history.bookmarked = True
                book_history.score += 1
                book_history.save()

            else:
                res = JsonResponse({'message': "Can't bookmark a book more then one time"})
                res.status_code = 400
                return res
        else:
            book_history = BookHistory(book=book)
            book_history.bookmarked = True
            book_history.score += 1
            book_history.save()
            user.history.books_action.add(book_history)

        return JsonResponse({'message': 'book {0} is bookmarked by the user {1}'.format(book.name, user.username)})

    except:
        res = JsonResponse({'message': 'error'})
        res.status_code = 400
        return res


@login_required
def book_unbookmark(request, id):
    """Take the id of the book to unboomark"""
    try:
        # Get the logged in user
        user = request.user

        # Get the Book to read
        book = get_object_or_404(Book, pk=id)

        # If the book is in the user history
        if user.history.books_action.filter(book=book).exists():
            book_history = user.history.books_action.get(book=book)

            if book_history.bookmarked:
                book_history.bookmarked = False
            else:
                res = JsonResponse({'message': "Can't unbookmarked a book more then one time"})
                res.status_code = 400
                return res

            book_history.save()

        return JsonResponse({'message': 'book {0} is unbookmarked by the user {1}'.format(book.name, user.username)})

    except:
        res = JsonResponse({'message': 'error'})
        res.status_code = 400
        return res


@login_required
def book_share(request, id):
    """Take the id of the book to share"""
    try:
        # Get the logged in user
        user = request.user

        # Get the Book to read
        book = get_object_or_404(Book, pk=id)

        # If the book is in the user history
        if user.history.books_action.filter(book=book).exists():
            book_history = user.history.books_action.get(book=book)

            if not book_history.shared:
                book_history.shared = True
                book_history.score += 1
                book_history.save()

        else:
            book_history = BookHistory(book=book)
            book_history.shared = True
            book_history.score += 1
            book_history.save()
            user.history.books_action.add(book_history)

        return JsonResponse({'message': 'book {0} is shared by the user {1}'.format(book.name, user.username)})

    except:
        res = JsonResponse({'message': 'error'})
        res.status_code = 400
        return res


@login_required
def add_comment(request):
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)

        book_id = request.POST.get('book_id')
        book = Book.objects.get(pk=book_id)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            sentiment = get_sentiment(comment.content)
            comment.sentiment = sentiment
            comment.save()

            if sentiment == POSITIVE:
                books_action = request.user.history.books_action.get(book=book)
                books_action.score += 1
                books_action.save()

            book.comments.add(comment)

            users = User.objects.filter(history__books_action__book=book).distinct().exclude(username__exact=request.user.username)
            link = reverse('books:detail', kwargs={'slug': book.slug}) + '#{0}'.format(comment.id)
            content = 'has commented on {1}'.format(request.user.username, book.name)
            for user in users:
                user.notify(sender=request.user, content=content, link=link)

            messages.success(request, 'Comment created')

        else:
            messages.error(request, 'Form is invalid')

        return redirect(reverse('books:detail', kwargs={'slug': book.slug}))

    else:
        messages.error(request, 'Error when creating comment waiting for POST method')
        return redirect('books:index')
