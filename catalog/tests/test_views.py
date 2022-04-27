from django.test import TestCase
from django.urls import reverse
import datetime
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from catalog.forms import RenewMovieForm
from catalog.models import Screenwriter, Director, MovieInstance, Movie, Genre
import uuid

class ScreenwritersListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_screenwriters = 13

        for screenwriter_id in range(number_of_screenwriters):
            Screenwriter.objects.create(
                first_name=f'Christian {screenwriter_id}',
                last_name=f'Surname {screenwriter_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/screenwriters/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('screenwriters'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('screenwriters'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/screenwriter_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('screenwriters'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['screenwriter_list']), 10)

    def test_lists_all_screenwriters(self):
        response = self.client.get(reverse('screenwriters')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['screenwriter_list']), 3)

class LoanedMovieInstancesByUserListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        test_screenwriter = Screenwriter.objects.create(first_name='John', last_name='Smith')
        test_director = Director.objects.create(first_name='Michael', last_name='Cash')
        test_genre = Genre.objects.create(name='Fantasy')
        test_movie = Movie.objects.create(
            title='Movie Title',
            summary='My movie summary',
            year_of_production='2004',
            screenwriter=test_screenwriter,
            director=test_director,
        )

        genre_objects_for_movie = Genre.objects.all()
        test_movie.genre.set(genre_objects_for_movie)
        test_movie.save()

        number_of_movie_copies = 30
        for movie_copy in range(number_of_movie_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=movie_copy%5)
            the_borrower = test_user1 if movie_copy % 2 else test_user2
            status = 'm'
            MovieInstance.objects.create(
                movie=test_movie,
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mymovies/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/movieinstance_list_borrowed_user.html')

    def test_only_borrowed_movies_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('movieinstance_list' in response.context)
        self.assertEqual(len(response.context['movieinstance_list']), 0)

        movies = MovieInstance.objects.all()[:10]

        for movie in movies:
            movie.status = 'o'
            movie.save()

        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('movieinstance_list' in response.context)

        for movieitem in response.context['movieinstance_list']:
            self.assertEqual(response.context['user'], movieitem.borrower)
            self.assertEqual(movieitem.status, 'o')

    def test_pages_ordered_by_due_date(self):
        for movie in MovieInstance.objects.all():
            movie.status='o'
            movie.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['movieinstance_list']), 10)

        last_date = 0
        for movie in response.context['movieinstance_list']:
            if last_date == 0:
                last_date = movie.due_back
            else:
                self.assertTrue(last_date <= movie.due_back)
                last_date = movie.due_back

class RenewMovieInstancesViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set movie as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_screenwriter = Screenwriter.objects.create(first_name='John', last_name='Smith')
        test_director = Director.objects.create(first_name='Michael', last_name='Cash')
        test_genre = Genre.objects.create(name='Fantasy')
        test_movie = Movie.objects.create(
            title='Movie Title',
            summary='My movie summary',
            year_of_production='2004',
            screenwriter=test_screenwriter,
            director=test_director,
        )

        genre_objects_for_movie = Genre.objects.all()
        test_movie.genre.set(genre_objects_for_movie)
        test_movie.save()

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_movieinstance1 = MovieInstance.objects.create(
            movie=test_movie,
            production='USA',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_movieinstance2 = MovieInstance.objects.create(
            movie=test_movie,
            production='USA',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_movie(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance2.pk}))
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_movie(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_movie_if_logged_in(self):
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk':test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/movie_renew_worker.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_movie_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-movie-worker', kwargs={'pk':self.test_movieinstance1.pk,}), {'renewal_date':valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}), {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-movie-worker', kwargs={'pk': self.test_movieinstance1.pk}), {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')
