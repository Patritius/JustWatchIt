from django.test import TestCase

from catalog.models import Screenwriter

class ScreenwriterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Screenwriter.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        screenwriter = Screenwriter.objects.get(id=1)
        field_label = screenwriter._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_date_of_death_label(self):
        screenwriter = Screenwriter.objects.get(id=1)
        field_label = screenwriter._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'Died')

    def test_first_name_max_length(self):
        screenwriter = Screenwriter.objects.get(id=1)
        max_length = screenwriter._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        screenwriter = Screenwriter.objects.get(id=1)
        expected_object_name = f'{screenwriter.last_name}, {screenwriter.first_name}'
        self.assertEqual(str(screenwriter), expected_object_name)

    def test_get_absolute_url(self):
        screenwriter = Screenwriter.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(screenwriter.get_absolute_url(), '/catalog/screenwriter/1')
