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
from .forms import BookReviewForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


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


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'profile.html', context)


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


# class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
#     model = BookInstance
#     template_name = 'user_books.html'
#     paginate_by = 10

#     def get_queryset(self):
#         return BookInstance.objects.filter(reader=self.request.user).filter(status__exact='t').order_by('due_back')

# tas pats kas virsuj class based view, tiesiog naudojame funkcija klasikine

def get_loaned_books(request):
    paginator = Paginator(BookInstance.objects.all(), 10)
    page_number = request.GET.get('page')
    paged_bookinstances = paginator.get_page(page_number)
    context = {
        'bookinstance_list': paged_bookinstances
    }

    return render(request, 'user_books.html', context=context)


class BookByUserDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance
    template_name = 'user_book.html'


def get_loaned_book(request, book_id):
    book = get_object_or_404(BookInstance, pk=book_id)
    context = {
        'object': book
    }
    return render(request, 'user_book.html', context=context)


class BookByUserCreateView(LoginRequiredMixin, generic.CreateView):
    model = BookInstance
    fields = ['book']
    success_url = "/library/mybooks/"
    template_name = 'user_book_new.html'

    def form_valid(self, form):
        form.instance.reader = self.request.user
        form.instance.status = "t"
        return super().form_valid(form)


class BookByUserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = BookInstance
    success_url = "/library/mybooks/"
    template_name = 'user_book_delete.html'

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader


def delete_loaned_book(request, book_id):
    book = BookInstance.objects.get(id=book_id)
    book.delete()
    return render(request, 'user_books.html')
