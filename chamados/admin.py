from django.contrib import admin
from .models import Categoria, Chamado, Comentario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ("nome",)
    ordering = ("nome",)


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    autocomplete_fields = ("autor",)
    fields = ("autor", "mensagem", "criado_em")
    readonly_fields = ("criado_em",)


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "categoria", "aluno", "status", "criado_em", "atualizado_em")
    list_filter = ("status", "categoria", "criado_em")
    search_fields = ("id", "titulo", "descricao", "aluno__username", "aluno__email")
    ordering = ("-criado_em",)
    date_hierarchy = "criado_em"

    autocomplete_fields = ("aluno", "categoria")
    inlines = (ComentarioInline,)

    fieldsets = (
        ("Dados do chamado", {"fields": ("aluno", "categoria", "titulo", "descricao")}),
        ("Atendimento", {"fields": ("status",)}),
        ("Datas", {"fields": ("criado_em", "atualizado_em")}),
    )

    readonly_fields = ("criado_em", "atualizado_em")