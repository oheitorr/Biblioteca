from django.contrib import admin
from .models import *

admin.site.register(Cidade)
admin.site.register(Editora)
admin.site.register(Leitor)
admin.site.register(Genero)
admin.site.register(Livro)
admin.site.register(Emprestimo)

class LivroInline(admin.TabularInline):
    model = Livro
    extra = 1

class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    inlines = [LivroInline]

admin.site.register(Autor, AutorAdmin)