from datetime import datetime, time

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ChamadoForm, ComentarioForm, StatusChamadoForm, AnexoForm
from .models import Categoria, Chamado, Anexo, HistoricoChamado
from .permissoes import is_secretaria, only_aluno_area, only_secretaria


@login_required
@only_aluno_area
def meus_chamados(request):
    chamados = Chamado.objects.filter(aluno=request.user).order_by("-criado_em")
    return render(request, "chamados/meus_chamados.html", {"chamados": chamados})


@login_required
@only_secretaria
def chamados_secretaria(request):
    qs = Chamado.objects.all().select_related("categoria", "aluno")

    status = request.GET.get("status", "")
    categoria = request.GET.get("categoria", "")
    busca = request.GET.get("q", "").strip()

    if status:
        qs = qs.filter(status=status)

    if categoria:
        qs = qs.filter(categoria_id=categoria)

    if busca:
        qs = qs.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    qs = qs.order_by("-criado_em")

    paginator = Paginator(qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.all().order_by("nome")

    return render(
        request,
        "chamados/chamados_secretaria.html",
        {
            "chamados": page_obj,
            "page_obj": page_obj,
            "categorias": categorias,
            "status_atual": status,
            "categoria_atual": categoria,
            "busca": busca,
        },
    )


@login_required
@only_aluno_area
def abrir_chamado(request):
    if request.method == "POST":
        form = ChamadoForm(request.POST)
        arquivos = request.FILES.getlist("arquivos")

        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.aluno = request.user
            chamado.save()

            # 🔥 HISTÓRICO (NOVO)
            HistoricoChamado.objects.create(
                chamado=chamado,
                usuario=request.user,
                descricao="Abriu o chamado"
            )

            for arquivo in arquivos:
                Anexo.objects.create(
                    chamado=chamado,
                    arquivo=arquivo,
                    enviado_por=request.user
                )

            return redirect("meus_chamados")
    else:
        form = ChamadoForm()

    return render(request, "chamados/abrir_chamado.html", {"form": form})


@login_required
def detalhe_chamado(request, id):
    chamado = get_object_or_404(Chamado, id=id)

    usuario_eh_secretaria = is_secretaria(request.user)

    if not usuario_eh_secretaria and chamado.aluno != request.user:
        return HttpResponseForbidden("Acesso negado.")

    comentario_form = ComentarioForm()
    status_form = StatusChamadoForm(instance=chamado)

    if request.method == "POST":
        if "atualizar_status" in request.POST:
            if not usuario_eh_secretaria:
                return HttpResponseForbidden("Acesso negado.")

            status_form = StatusChamadoForm(request.POST, instance=chamado)
            if status_form.is_valid():
                status_form.save()

                # 🔥 HISTÓRICO (NOVO)
                HistoricoChamado.objects.create(
                    chamado=chamado,
                    usuario=request.user,
                    descricao=f"Alterou status para {chamado.status}"
                )

                Chamado.objects.filter(id=chamado.id).update(
                    ultima_interacao_em=timezone.now()
                )
                return redirect("detalhe_chamado", id=chamado.id)

        elif "enviar_comentario" in request.POST:
            comentario_form = ComentarioForm(request.POST)
            arquivos = request.FILES.getlist("arquivos")

            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.autor = request.user
                comentario.chamado = chamado
                comentario.save()

                # ❌ REMOVIDO HISTÓRICO DUPLICADO DAQUI

                for arquivo in arquivos:
                    Anexo.objects.create(
                        chamado=chamado,
                        arquivo=arquivo,
                        enviado_por=request.user
                    )

                Chamado.objects.filter(id=chamado.id).update(
                    ultima_interacao_em=timezone.now()
                )
                return redirect("detalhe_chamado", id=chamado.id)

    return render(
        request,
        "chamados/detalhe_chamado.html",
        {
            "chamado": chamado,
            "comentario_form": comentario_form,
            "status_form": status_form,
            "is_secretaria": usuario_eh_secretaria,
        },
    )


@login_required
def minha_area(request):
    usuario_eh_secretaria = is_secretaria(request.user)
    busca = request.GET.get("q", "").strip()

    if request.user.is_superuser:
        chamados = Chamado.objects.all()

        if busca:
            chamados = chamados.filter(
                Q(titulo__icontains=busca) |
                Q(descricao__icontains=busca)
            )

        data_inicial = request.GET.get("data_inicial", "").strip()
        data_final = request.GET.get("data_final", "").strip()

        if data_inicial:
            try:
                data_inicial_obj = datetime.strptime(data_inicial, "%Y-%m-%d").date()
                data_inicial_dt = timezone.make_aware(
                    datetime.combine(data_inicial_obj, time.min)
                )
                chamados = chamados.filter(criado_em__gte=data_inicial_dt)
            except ValueError:
                data_inicial = ""

        if data_final:
            try:
                data_final_obj = datetime.strptime(data_final, "%Y-%m-%d").date()
                data_final_dt = timezone.make_aware(
                    datetime.combine(data_final_obj, time.max)
                )
                chamados = chamados.filter(criado_em__lte=data_final_dt)
            except ValueError:
                data_final = ""

        total_abertos = chamados.filter(status="ABERTO").count()
        total_em_atendimento = chamados.filter(status="EM_ATENDIMENTO").count()
        total_concluidos = chamados.filter(status="CONCLUIDO").count()
        total_geral = chamados.count()

        return render(
            request,
            "chamados/minha_area.html",
            {
                "dashboard_admin": True,
                "dashboard_secretaria": False,
                "total_abertos": total_abertos,
                "total_em_atendimento": total_em_atendimento,
                "total_concluidos": total_concluidos,
                "total_geral": total_geral,
                "ultimos": chamados.order_by("-ultima_interacao_em")[:8],
                "data_inicial": data_inicial,
                "data_final": data_final,
                "busca": busca,
            },
        )

    if usuario_eh_secretaria:
        chamados = Chamado.objects.all()

        if busca:
            chamados = chamados.filter(
                Q(titulo__icontains=busca) |
                Q(descricao__icontains=busca)
            )

        chamados = chamados.order_by("-ultima_interacao_em")

        total_abertos = chamados.filter(status="ABERTO").count()
        total_em_atendimento = chamados.filter(status="EM_ATENDIMENTO").count()
        total_concluidos = chamados.filter(status="CONCLUIDO").count()

        return render(
            request,
            "chamados/minha_area.html",
            {
                "dashboard_admin": False,
                "dashboard_secretaria": True,
                "total_abertos": total_abertos,
                "total_em_atendimento": total_em_atendimento,
                "total_concluidos": total_concluidos,
                "ultimos": chamados[:5],
                "busca": busca,
            },
        )

    chamados = Chamado.objects.filter(aluno=request.user)

    if busca:
        chamados = chamados.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    total_abertos = chamados.filter(status="ABERTO").count()
    total_em_atendimento = chamados.filter(status="EM_ATENDIMENTO").count()
    total_concluidos = chamados.filter(status="CONCLUIDO").count()

    return render(
        request,
        "chamados/minha_area.html",
        {
            "dashboard_admin": False,
            "dashboard_secretaria": False,
            "total_abertos": total_abertos,
            "total_em_atendimento": total_em_atendimento,
            "total_concluidos": total_concluidos,
            "ultimos": chamados.order_by("-criado_em")[:5],
            "busca": busca,
        },
    )