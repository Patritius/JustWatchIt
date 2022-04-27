from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.MoviesListView.as_view(), name='movies'),
    path('movie/<int:pk>', views.MovieDetailView.as_view(), name='movie-detail'),
    path('screenwriters/', views.ScreenwritersListView.as_view(), name='screenwriters'),
    path('screenwriter/<int:pk>', views.ScreenwriterDetailView.as_view(), name='screenwriter-detail'),
    path('directors/', views.DirectorsListView.as_view(), name='directors'),
    path('director/<int:pk>', views.DirectorDetailView.as_view(), name='director-detail'),
    path('mymovies/', views.LoanedMoviesByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.LoanedMoviesListView.as_view(), name='all-borrowed'),
    path('movie/<uuid:pk>/renew/', views.renew_movie_worker, name='renew-movie-worker'),
    path('screenwriter/create/', views.ScreenwriterCreate.as_view(), name='screenwriter-create'),
    path('screenwriter/<int:pk>/update/', views.ScreenwriterUpdate.as_view(), name='screenwriter-update'),
    path('screenwriter/<int:pk>/delete/', views.ScreenwriterDelete.as_view(), name='screenwriter-delete'),
    path('director/create/', views.DirectorCreate.as_view(), name='director-create'),
    path('director/<int:pk>/update/', views.DirectorUpdate.as_view(), name='director-update'),
    path('director/<int:pk>/delete/', views.DirectorDelete.as_view(), name='director-delete'),
    path('movie/create/', views.MovieCreate.as_view(), name='movie-create'),
    path('movie/<int:pk>/update/', views.MovieUpdate.as_view(), name='movie-update'),
    path('movie/<int:pk>/delete/', views.MovieDelete.as_view(), name='movie-delete'),
]
