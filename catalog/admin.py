from django.contrib import admin

from .models import Screenwriter, Genre, Movie, MovieInstance, Director

class MovieInline(admin.TabularInline):
    model = Movie
    extra = 0

class ScreenwriterAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [MovieInline]

class DirectorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [MovieInline]

class MovieInstanceInline(admin.TabularInline):
    model = MovieInstance
    extra = 0

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'screenwriter', 'director', 'display_genre')

    inlines = [MovieInstanceInline]

@admin.register(MovieInstance)
class MovieInstanceAdmin(admin.ModelAdmin):
    list_display = ('movie', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('movie', 'production', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )


admin.site.register(Screenwriter, ScreenwriterAdmin)
admin.site.register(Genre)
admin.site.register(Director, DirectorAdmin)
