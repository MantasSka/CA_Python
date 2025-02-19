from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .forms import BookReviewForm
from django.views.generic.edit import FormMixin


def index(request):

    # Suskaičiuokime keletą pagrindinių objektų
    book_count = Book.objects.all().count()
    book_instance_count = BookInstance.objects.all().count()

    # Laisvos knygos (tos, kurios turi statusą 'av')
    available_book_instances_available = BookInstance.objects.filter(
        status='av').count()

    # Autorių skaičius
    author_count = Author.objects.all().count()

    # Papildome kintamuoju num_visits, įkeliame jį į kontekstą.

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'book_count': book_count,
        'book_instance_count': book_instance_count,
        'available_book_instances_available': available_book_instances_available,
        'author_count': author_count,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    page_number = request.GET.get('page')
    paged_authors = paginator.get_page(page_number)
    context = {
        'authors': paged_authors
    }

    return render(request, 'authors.html', context=context)


def author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    context = {
        'author': author
    }
    return render(request, 'author.html', context=context)


def search(request):
    """
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą knygų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės 
    didžiosios/mažosios.
    """
    query = request.GET.get('query')
    search_results = Book.objects.filter(
        Q(title__icontains=query) | Q(summary__icontains=query))
    return render(request, 'search.html', {'books': search_results, 'query': query})


class BookListView(generic.ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'book_list'
    template_name = 'book_list.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['duomenys'] = 'Random text'
        return context


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = 'book_detail.html'
    form_class = BookReviewForm

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'user_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user).filter(status__exact='t').order_by('due_back')


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(
                    request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(
                        request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(
                        username=username, email=email, password=password)
                    messages.info(
                        request, f'Vartotojas {username} užregistruotas!')
                    return redirect('login')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'register.html')
