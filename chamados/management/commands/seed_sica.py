from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from chamados.models import Categoria, Chamado, Comentario


class Command(BaseCommand):
    help = "Popula o sistema SICA com dados iniciais de exemplo"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Iniciando seed do SICA..."))

        # Grupos
        grupo_aluno, _ = Group.objects.get_or_create(name="Aluno")
        grupo_secretaria, _ = Group.objects.get_or_create(name="Secretaria")

        self.stdout.write(self.style.SUCCESS("Grupos verificados/criados."))

        # Usuários
        admin, admin_created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@sica.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if admin_created:
            admin.set_password("@Abc12345")
            admin.save()
        else:
            admin.is_staff = True
            admin.is_superuser = True
            admin.email = "admin@sica.com"
            admin.save()

        aluno1, aluno1_created = User.objects.get_or_create(
            username="aluno1",
            defaults={"email": "aluno1@sica.com"},
        )
        if aluno1_created:
            aluno1.set_password("@Abc12345")
            aluno1.save()
        aluno1.groups.add(grupo_aluno)

        aluno2, aluno2_created = User.objects.get_or_create(
            username="aluno2",
            defaults={"email": "aluno2@sica.com"},
        )
        if aluno2_created:
            aluno2.set_password("@Abc12345")
            aluno2.save()
        aluno2.groups.add(grupo_aluno)

        secretaria, secretaria_created = User.objects.get_or_create(
            username="secretaria",
            defaults={"email": "secretaria@sica.com"},
        )
        if secretaria_created:
            secretaria.set_password("@Abc12345")
            secretaria.save()
        secretaria.groups.add(grupo_secretaria)

        self.stdout.write(self.style.SUCCESS("Usuários verificados/criados."))

        # Categorias
        categorias_nomes = [
            "Emissão de Diploma",
            "Dispensa de Materiais",
            "Ajuste de Matrículas",
            "Desistência de Disciplina",
            "Informações sobre estágio",
        ]

        categorias = {}
        for nome in categorias_nomes:
            categoria, _ = Categoria.objects.get_or_create(nome=nome)
            categorias[nome] = categoria

        self.stdout.write(self.style.SUCCESS("Categorias verificadas/criadas."))

        # Chamados
        chamados_dados = [
            {
                "aluno": aluno1,
                "categoria": categorias["Ajuste de Matrículas"],
                "titulo": "Emissão de diploma",
                "descricao": "Gostaria de informações sobre o processo de emissão do diploma.",
                "status": Chamado.Status.ABERTO,
            },
            {
                "aluno": aluno1,
                "categoria": categorias["Informações sobre estágio"],
                "titulo": "Estágio obrigatório",
                "descricao": "Preciso saber quais documentos são necessários para o estágio obrigatório.",
                "status": Chamado.Status.EM_ATENDIMENTO,
            },
            {
                "aluno": aluno2,
                "categoria": categorias["Dispensa de Materiais"],
                "titulo": "Dispensa de materiais",
                "descricao": "Solicito análise para dispensa de disciplina já cursada anteriormente.",
                "status": Chamado.Status.CONCLUIDO,
            },
        ]

        chamados_criados = []

        for item in chamados_dados:
            chamado, created = Chamado.objects.get_or_create(
                aluno=item["aluno"],
                titulo=item["titulo"],
                defaults={
                    "categoria": item["categoria"],
                    "descricao": item["descricao"],
                    "status": item["status"],
                },
            )

            if not created:
                chamado.categoria = item["categoria"]
                chamado.descricao = item["descricao"]
                chamado.status = item["status"]
                chamado.save()

            chamados_criados.append(chamado)

        self.stdout.write(self.style.SUCCESS("Chamados verificados/criados."))

        # Comentários
        comentarios_dados = [
            {
                "chamado": chamados_criados[0],
                "autor": aluno1,
                "mensagem": "Abri este chamado para entender os prazos e documentos necessários.",
            },
            {
                "chamado": chamados_criados[1],
                "autor": secretaria,
                "mensagem": "Estamos analisando sua solicitação. Em breve retornaremos.",
            },
            {
                "chamado": chamados_criados[2],
                "autor": secretaria,
                "mensagem": "Solicitação analisada e concluída com sucesso.",
            },
        ]

        for item in comentarios_dados:
            Comentario.objects.get_or_create(
                chamado=item["chamado"],
                autor=item["autor"],
                mensagem=item["mensagem"],
            )

        self.stdout.write(self.style.SUCCESS("Comentários verificados/criados."))
        self.stdout.write(self.style.SUCCESS("Seed do SICA finalizada com sucesso!"))