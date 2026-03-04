from django import forms
from .models import Chamado
from .models import Comentario
from .models import Chamado

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