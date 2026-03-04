from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Chamado
from .permissoes import only_secretaria

from .forms import ChamadoForm, StatusChamadoForm
from django.shortcuts import redirect

from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .forms import ComentarioForm

from .models import Chamado, Categoria
from django.core.paginator import Paginator


@login_required
def meus_chamados(request):
    chamados = Chamado.objects.filter(aluno=request.user)
    return render(request, "chamados/meus_chamados.html", {"chamados": chamados})


@only_secretaria
def chamados_secretaria(request):
    chamados = Chamado.objects.all().select_related("categoria", "aluno")

    status = request.GET.get("status")
    categoria = request.GET.get("categoria")
    ordenar = request.GET.get("ordenar", "-criado_em")

    if status:
        chamados = chamados.filter(status=status)

    if categoria:
        chamados = chamados.filter(categoria_id=categoria)

    chamados = chamados.order_by(ordenar)

    paginator = Paginator(chamados, 5)  # 5 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.all().order_by("nome")

    return render(
        request,
        "chamados/chamados_secretaria.html",
        {
            "page_obj": page_obj,
            "categorias": categorias,
            "status_atual": status or "",
            "categoria_atual": categoria or "",
            "ordenar": ordenar,
        },
    )

@login_required
def abrir_chamado(request):
    if request.method == "POST":
        form = ChamadoForm(request.POST)
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.aluno = request.user
            chamado.save()
            return redirect("meus_chamados")
    else:
        form = ChamadoForm()

    return render(request, "chamados/abrir_chamado.html", {"form": form})

@login_required
def detalhe_chamado(request, id):
    chamado = get_object_or_404(Chamado, id=id)

    # Regra de acesso: aluno só vê o próprio
    is_secretaria = request.user.is_superuser or request.user.groups.filter(name="Secretaria").exists()
    if not is_secretaria and chamado.aluno != request.user:
        return HttpResponseForbidden("Acesso negado.")

    # Forms
    comentario_form = ComentarioForm()
    status_form = StatusChamadoForm(instance=chamado)

    if request.method == "POST":
        # Atualizar status (só secretaria/admin)
        if "atualizar_status" in request.POST:
            if not is_secretaria:
                return HttpResponseForbidden("Acesso negado.")
            status_form = StatusChamadoForm(request.POST, instance=chamado)
            if status_form.is_valid():
                status_form.save()

        # Adicionar comentário (aluno ou secretaria)
        elif "enviar_comentario" in request.POST:
            comentario_form = ComentarioForm(request.POST)
            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.autor = request.user
                comentario.chamado = chamado
                comentario.save()

    return render(
        request,
        "chamados/detalhe_chamado.html",
        {
            "chamado": chamado,
            "comentario_form": comentario_form,
            "status_form": status_form,
            "is_secretaria": is_secretaria,
        },
    )

@login_required
def minha_area(request):
    chamados = Chamado.objects.filter(aluno=request.user)

    total_abertos = chamados.filter(status="ABERTO").count()
    total_em_atendimento = chamados.filter(status="EM_ATENDIMENTO").count()
    total_concluidos = chamados.filter(status="CONCLUIDO").count()

    return render(
        request,
        "chamados/minha_area.html",
        {
            "total_abertos": total_abertos,
            "total_em_atendimento": total_em_atendimento,
            "total_concluidos": total_concluidos,
            "ultimos": chamados[:5],
        },
    )

@only_secretaria
def chamados_secretaria(request):
    chamados = Chamado.objects.all().select_related("categoria", "aluno")

    status = request.GET.get("status")
    categoria = request.GET.get("categoria")

    if status:
        chamados = chamados.filter(status=status)

    if categoria:
        chamados = chamados.filter(categoria_id=categoria)

    categorias = Categoria.objects.all().order_by("nome")

    return render(
        request,
        "chamados/chamados_secretaria.html",
        {
            "chamados": chamados,
            "categorias": categorias,
            "status_atual": status or "",
            "categoria_atual": categoria or "",
        },
    )