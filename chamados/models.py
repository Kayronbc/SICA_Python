from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO = "ABERTO", "Aberto"
        EM_ATENDIMENTO = "EM_ATENDIMENTO", "Em atendimento"
        CONCLUIDO = "CONCLUIDO", "Concluído"

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chamados_abertos",
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="chamados")
    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTO)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"#{self.id} - {self.titulo}"


class Comentario(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["criado_em"]

    def __str__(self):
        return f"Comentário {self.id} no chamado #{self.chamado_id}"