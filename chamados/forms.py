from django import forms

from .models import Chamado, Comentario, Anexo


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["mensagem"]


class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ["categoria", "titulo", "descricao"]


class StatusChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ["status"]

class AnexoForm(forms.ModelForm):
    class Meta:
        model = Anexo
        fields = ["arquivo"]