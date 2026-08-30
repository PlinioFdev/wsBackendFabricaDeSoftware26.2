"""Views da página web, feitas com template do Django."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LivroForm
from .models import Estante
from .services import completar_campos_vazios


def pagina_inicial(request):
    """Lista todas as estantes com os livros de cada uma."""
    estantes = Estante.objects.prefetch_related('livros')
    return render(request, 'biblioteca/pagina_inicial.html', {'estantes': estantes})


@login_required
def cadastrar_livro(request):
    """Cadastra um livro pelo formulário, completando com a Open Library."""
    if request.method == 'POST':
        formulario = LivroForm(request.POST)
        if formulario.is_valid():
            livro = formulario.save(commit=False)
            aviso = completar_campos_vazios(livro)
            livro.save()

            if aviso:
                messages.warning(request, f'Livro salvo, mas: {aviso}')
            else:
                messages.success(request, f'"{livro.titulo}" cadastrado.')

            return redirect('pagina_inicial')
    else:
        formulario = LivroForm()

    return render(request, 'biblioteca/livro_form.html', {'formulario': formulario})
