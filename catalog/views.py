from django.shortcuts import render, get_object_or_404
from .models import Movie, Screenwriter, Director, MovieInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from catalog.forms import RenewMovieForm
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView


def index(request):
    num_movies = Movie.objects.all().count()
    num_instances = MovieInstance.objects.all().count()


    num_instances_available = MovieInstance.objects.filter(status__exact='a').count()

    num_screenwriters = Screenwriter.objects.count()
    num_directors = Director.objects.count()
    num_genres = Genre.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_movies': num_movies,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_screenwriters': num_screenwriters,
        'num_directors': num_directors,
        'num_genres': num_genres,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)

class MoviesListView(generic.ListView):
    model = Movie
    paginate_by = 10

class MovieDetailView(generic.DetailView):
    model = Movie

class ScreenwritersListView(generic.ListView):
    model = Screenwriter
    paginate_by = 10

class ScreenwriterDetailView(generic.DetailView):
    model = Screenwriter

class DirectorsListView(generic.ListView):
    model = Director
    paginate_by = 10

class DirectorDetailView(generic.DetailView):
    model = Director

class LoanedMoviesByUserListView(LoginRequiredMixin,generic.ListView):
    model = MovieInstance
    template_name ='catalog/movieinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return MovieInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedMoviesListView(PermissionRequiredMixin, generic.ListView):
    model = MovieInstance
    template_name ='catalog/movieinstance_list_borrowed_movies.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return MovieInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_movie_worker(request, pk):
    movie_instance = get_object_or_404(MovieInstance, pk=pk)

    if request.method == 'POST':

        form = RenewMovieForm(request.POST)

        if form.is_valid():
            movie_instance.due_back = form.cleaned_data['renewal_date']
            movie_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed') )

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewMovieForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'movie_instance': movie_instance,
    }

    return render(request, 'catalog/movie_renew_worker.html', context)

class ScreenwriterCreate(PermissionRequiredMixin, CreateView):
    model = Screenwriter
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class ScreenwriterUpdate(PermissionRequiredMixin, UpdateView):
    model = Screenwriter
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class ScreenwriterDelete(PermissionRequiredMixin, DeleteView):
    model = Screenwriter
    success_url = reverse_lazy('screenwriters')
    permission_required = 'catalog.can_mark_returned'

class DirectorCreate(PermissionRequiredMixin, CreateView):
    model = Director
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class DirectorUpdate(PermissionRequiredMixin, UpdateView):
    model = Director
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class DirectorDelete(PermissionRequiredMixin, DeleteView):
    model = Director
    success_url = reverse_lazy('directors')
    permission_required = 'catalog.can_mark_returned'

class MovieCreate(PermissionRequiredMixin, CreateView):
    model = Movie
    fields = ['title', 'screenwriter', 'director', 'summary', 'year_of_production', 'genre']
    permission_required = 'catalog.can_mark_returned'

class MovieUpdate(PermissionRequiredMixin, UpdateView):
    model = Movie
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class MovieDelete(PermissionRequiredMixin, DeleteView):
    model = Movie
    success_url = reverse_lazy('movies')
    permission_required = 'catalog.can_mark_returned'
