from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import (
    Usuario, Vicio, Habito, MetaUsuario, Recaida, Gatilho, RegistroGatilho,
    Rotina, Tarefa, Substituicao, Categoria, Recompensa, Conquista,
    Frase, Historico
)
from .forms import (
    LoginForm, CadastroForm, VicioForm, HabitoForm, MetaForm, RecaidaForm,
    GatilhoForm, RegistroGatilhoForm, RotinaForm, TarefaForm, SubstituicaoForm
)


# ─────────────────────────────────────────────
# HELPERS DE AUTENTICAÇÃO (sessão própria)
# ─────────────────────────────────────────────
def usuario_logado(request):
    """Retorna o objeto Usuario da sessão atual, ou None se não logado."""
    user_id = request.session.get('usuario_id')
    if not user_id:
        return None
    return Usuario.objects.filter(id=user_id).first()


def login_obrigatorio(view_func):
    """Decorator simples para exigir login (sem usar django.contrib.auth)."""
    def wrapper(request, *args, **kwargs):
        if not usuario_logado(request):
            messages.warning(request, 'Você precisa entrar para acessar essa página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def registrar_historico(usuario, descricao, tipo_evento='geral'):
    Historico.objects.create(usuario=usuario, descricao=descricao, tipo_evento=tipo_evento)


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def login_view(request):
    if usuario_logado(request):
        return redirect('index')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username'].strip()
        senha = form.cleaned_data['senha']
        usuario = Usuario.objects.filter(username__iexact=username).first()

        if usuario and usuario.checar_senha(senha):
            request.session['usuario_id'] = usuario.id
            messages.success(request, f'Bem-vindo(a) de volta, {usuario.nome}!')
            return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'login.html', {'form': form})


# ─────────────────────────────────────────────
# CADASTRO DE USUÁRIO
# ─────────────────────────────────────────────
def cadastro_view(request):
    if usuario_logado(request):
        return redirect('index')

    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        novo_usuario = Usuario(
            nome=form.cleaned_data['nome'],
            username=form.cleaned_data['username'],
            apelido=form.cleaned_data['nome'].split(' ')[0],
        )
        novo_usuario.set_senha(form.cleaned_data['senha'])
        novo_usuario.save()

        registrar_historico(novo_usuario, 'Conta criada no sistema', 'cadastro')

        request.session['usuario_id'] = novo_usuario.id
        messages.success(request, 'Conta criada com sucesso! Bem-vindo(a) ao DesVício.')
        return redirect('index')

    return render(request, 'cadastro.html', {'form': form})


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
def logout_view(request):
    request.session.flush()
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
@login_obrigatorio
def index(request):
    usuario = usuario_logado(request)
    vicios = Vicio.objects.filter(usuario=usuario)

    context = {
        'vicios': vicios,
        'total_vicios': vicios.count(),
        'total_habitos': Habito.objects.filter(usuario=usuario).count(),
        'total_metas': MetaUsuario.objects.filter(usuario=usuario).count(),
        'total_recaidas': Recaida.objects.filter(usuario=usuario).count(),
        'usuario': usuario,
    }
    return render(request, 'index.html', context)


# ─────────────────────────────────────────────
# VÍCIO — criar / editar / deletar
# ─────────────────────────────────────────────
@login_obrigatorio
def criar_vicio(request):
    usuario = usuario_logado(request)
    form = VicioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vicio = form.save(commit=False)
        vicio.usuario = usuario
        vicio.save()
        registrar_historico(usuario, f'Cadastrou o vício "{vicio.nome}"', 'cadastro')
        messages.success(request, 'Vício cadastrado com sucesso!')
        return redirect('index')
    return render(request, 'criar_vicio.html', {'form': form})


@login_obrigatorio
def editar_vicio(request, vicio_id):
    usuario = usuario_logado(request)
    vicio = get_object_or_404(Vicio, id=vicio_id, usuario=usuario)
    form = VicioForm(request.POST or None, instance=vicio)
    if request.method == 'POST' and form.is_valid():
        form.save()
        registrar_historico(usuario, f'Atualizou o vício "{vicio.nome}"', 'edicao')
        messages.success(request, 'Vício atualizado com sucesso!')
        return redirect('index')
    return render(request, 'editar_vicio.html', {'form': form, 'vicio': vicio})


@login_obrigatorio
def deletar_vicio(request, vicio_id):
    usuario = usuario_logado(request)
    vicio = get_object_or_404(Vicio, id=vicio_id, usuario=usuario)
    nome = vicio.nome
    vicio.delete()
    registrar_historico(usuario, f'Removeu o vício "{nome}"', 'remocao')
    messages.success(request, 'Vício removido.')
    return redirect('index')


# ─────────────────────────────────────────────
# HÁBITOS
# ─────────────────────────────────────────────
@login_obrigatorio
def habitos_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = HabitoForm(request.POST)
        if form.is_valid():
            habito = form.save(commit=False)
            habito.usuario = usuario
            habito.save()
            registrar_historico(usuario, f'Cadastrou o hábito "{habito.nome}"', 'cadastro')
            messages.success(request, 'Hábito cadastrado com sucesso!')
            return redirect('habitos')
    else:
        form = HabitoForm()

    habitos = Habito.objects.filter(usuario=usuario).order_by('-id')
    return render(request, 'habitos.html', {'habitos': habitos, 'form': form})


@login_obrigatorio
def deletar_habito(request, habito_id):
    usuario = usuario_logado(request)
    habito = get_object_or_404(Habito, id=habito_id, usuario=usuario)
    habito.delete()
    messages.success(request, 'Hábito removido.')
    return redirect('habitos')


# ─────────────────────────────────────────────
# METAS
# ─────────────────────────────────────────────
@login_obrigatorio
def metas_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = MetaForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = usuario
            meta.save()
            registrar_historico(usuario, f'Definiu a meta "{meta.titulo}"', 'cadastro')
            messages.success(request, 'Meta cadastrada com sucesso!')
            return redirect('metas')
    else:
        form = MetaForm()

    metas = MetaUsuario.objects.filter(usuario=usuario).order_by('prazo')
    return render(request, 'metas.html', {'metas': metas, 'form': form})


@login_obrigatorio
def concluir_meta(request, meta_id):
    usuario = usuario_logado(request)
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=usuario)
    meta.status = not meta.status
    meta.save()
    if meta.status:
        registrar_historico(usuario, f'Concluiu a meta "{meta.titulo}"', 'conquista')
        messages.success(request, 'Meta marcada como concluída! Parabéns!')
    return redirect('metas')


@login_obrigatorio
def deletar_meta(request, meta_id):
    usuario = usuario_logado(request)
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=usuario)
    meta.delete()
    messages.success(request, 'Meta removida.')
    return redirect('metas')


# ─────────────────────────────────────────────
# RECAÍDAS
# ─────────────────────────────────────────────
@login_obrigatorio
def recaidas_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = RecaidaForm(request.POST, usuario=usuario)
        if form.is_valid():
            recaida = form.save(commit=False)
            recaida.usuario = usuario
            recaida.save()
            registrar_historico(
                usuario,
                f'Registrou uma recaída em "{recaida.vicio.nome}"',
                'recaida'
            )
            messages.info(request, 'Recaída registrada. O importante é continuar tentando — seu streak foi recalculado.')
            return redirect('recaidas')
    else:
        form = RecaidaForm(usuario=usuario)

    recaidas = Recaida.objects.filter(usuario=usuario).order_by('-data')
    return render(request, 'recaidas.html', {'recaidas': recaidas, 'form': form})


@login_obrigatorio
def deletar_recaida(request, recaida_id):
    usuario = usuario_logado(request)
    recaida = get_object_or_404(Recaida, id=recaida_id, usuario=usuario)
    recaida.delete()
    messages.success(request, 'Registro de recaída removido. Streak recalculado.')
    return redirect('recaidas')


# ─────────────────────────────────────────────
# GATILHOS
# ─────────────────────────────────────────────
@login_obrigatorio
def gatilhos_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = GatilhoForm(request.POST)
        if form.is_valid():
            gatilho = form.save(commit=False)
            gatilho.usuario = usuario
            gatilho.save()
            registrar_historico(usuario, f'Mapeou o gatilho "{gatilho.nome}"', 'cadastro')
            messages.success(request, 'Gatilho cadastrado com sucesso!')
            return redirect('gatilhos')
    else:
        form = GatilhoForm()

    gatilhos = Gatilho.objects.filter(usuario=usuario).order_by('-id')
    return render(request, 'gatilhos.html', {'gatilhos': gatilhos, 'form': form})


@login_obrigatorio
def deletar_gatilho(request, gatilho_id):
    usuario = usuario_logado(request)
    gatilho = get_object_or_404(Gatilho, id=gatilho_id, usuario=usuario)
    gatilho.delete()
    messages.success(request, 'Gatilho removido.')
    return redirect('gatilhos')


# ─────────────────────────────────────────────
# REGISTRO DE GATILHOS (ocorrências)
# ─────────────────────────────────────────────
@login_obrigatorio
def registro_gatilhos_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = RegistroGatilhoForm(request.POST, usuario=usuario)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = usuario
            registro.save()
            registrar_historico(
                usuario,
                f'Registrou ocorrência do gatilho "{registro.gatilho.nome}"',
                'gatilho'
            )
            messages.success(request, 'Ocorrência registrada com sucesso!')
            return redirect('registro_gatilhos')
    else:
        form = RegistroGatilhoForm(usuario=usuario)

    registros = RegistroGatilho.objects.filter(usuario=usuario).order_by('-data')

    if not Gatilho.objects.filter(usuario=usuario).exists():
        messages.warning(request, 'Cadastre um gatilho antes de registrar uma ocorrência.')

    return render(request, 'registro_gatilhos.html', {'registros': registros, 'form': form})


@login_obrigatorio
def deletar_registro_gatilho(request, registro_id):
    usuario = usuario_logado(request)
    registro = get_object_or_404(RegistroGatilho, id=registro_id, usuario=usuario)
    registro.delete()
    messages.success(request, 'Registro removido.')
    return redirect('registro_gatilhos')


# ─────────────────────────────────────────────
# ROTINAS
# ─────────────────────────────────────────────
@login_obrigatorio
def rotinas_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = RotinaForm(request.POST)
        if form.is_valid():
            rotina = form.save(commit=False)
            rotina.usuario = usuario
            rotina.save()
            registrar_historico(usuario, f'Criou a rotina "{rotina.titulo}"', 'cadastro')
            messages.success(request, 'Rotina cadastrada com sucesso!')
            return redirect('rotinas')
    else:
        form = RotinaForm()

    rotinas = Rotina.objects.filter(usuario=usuario).order_by('horario')
    return render(request, 'rotinas.html', {'rotinas': rotinas, 'form': form})


@login_obrigatorio
def deletar_rotina(request, rotina_id):
    usuario = usuario_logado(request)
    rotina = get_object_or_404(Rotina, id=rotina_id, usuario=usuario)
    rotina.delete()
    messages.success(request, 'Rotina removida.')
    return redirect('rotinas')


# ─────────────────────────────────────────────
# TAREFAS
# ─────────────────────────────────────────────
@login_obrigatorio
def tarefas_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = TarefaForm(request.POST, usuario=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa cadastrada com sucesso!')
            return redirect('tarefas')
    else:
        form = TarefaForm(usuario=usuario)

    if not Rotina.objects.filter(usuario=usuario).exists():
        messages.warning(request, 'Cadastre uma rotina antes de criar tarefas.')

    tarefas = Tarefa.objects.filter(rotina__usuario=usuario).order_by('rotina__horario')
    return render(request, 'tarefas.html', {'tarefas': tarefas, 'form': form})


@login_obrigatorio
def concluir_tarefa(request, tarefa_id):
    usuario = usuario_logado(request)
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, rotina__usuario=usuario)
    tarefa.concluida = not tarefa.concluida
    tarefa.save()
    return redirect('tarefas')


@login_obrigatorio
def deletar_tarefa(request, tarefa_id):
    usuario = usuario_logado(request)
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, rotina__usuario=usuario)
    tarefa.delete()
    messages.success(request, 'Tarefa removida.')
    return redirect('tarefas')


# ─────────────────────────────────────────────
# SUBSTITUIÇÕES
# ─────────────────────────────────────────────
@login_obrigatorio
def substituicoes_view(request):
    usuario = usuario_logado(request)

    if request.method == 'POST':
        form = SubstituicaoForm(request.POST, usuario=usuario)
        if form.is_valid():
            substituicao = form.save(commit=False)
            substituicao.usuario = usuario
            substituicao.save()
            registrar_historico(
                usuario,
                f'Criou substituição: "{substituicao.vicio.nome}" → "{substituicao.habito.nome}"',
                'cadastro'
            )
            messages.success(request, 'Substituição cadastrada com sucesso!')
            return redirect('substituicoes')
    else:
        form = SubstituicaoForm(usuario=usuario)

    falta_vicio = not Vicio.objects.filter(usuario=usuario).exists()
    falta_habito = not Habito.objects.filter(usuario=usuario).exists()
    if falta_vicio or falta_habito:
        messages.warning(request, 'Cadastre ao menos um vício e um hábito antes de criar substituições.')

    substituicoes = Substituicao.objects.filter(usuario=usuario).order_by('-data_inicio')
    return render(request, 'substituicoes.html', {'substituicoes': substituicoes, 'form': form})


@login_obrigatorio
def deletar_substituicao(request, substituicao_id):
    usuario = usuario_logado(request)
    substituicao = get_object_or_404(Substituicao, id=substituicao_id, usuario=usuario)
    substituicao.delete()
    messages.success(request, 'Substituição removida.')
    return redirect('substituicoes')


# ─────────────────────────────────────────────
# STREAKS (calculado automaticamente a partir do Vício)
# ─────────────────────────────────────────────
@login_obrigatorio
def streaks_view(request):
    usuario = usuario_logado(request)
    vicios = Vicio.objects.filter(usuario=usuario)

    streaks = [
        {
            'usuario': usuario.nome,
            'vicio': vicio.nome,
            'dias_consecutivos': vicio.streak_atual,
            'recorde': vicio.recorde_pessoal,
        }
        for vicio in vicios
    ]
    return render(request, 'streaks.html', {'streaks': streaks})


# ─────────────────────────────────────────────
# PROGRESSOS (calculado automaticamente a partir do Vício)
# ─────────────────────────────────────────────
@login_obrigatorio
def progressos_view(request):
    usuario = usuario_logado(request)
    vicios = Vicio.objects.filter(usuario=usuario)

    progressos = [
        {
            'usuario': usuario.nome,
            'vicio': vicio.nome,
            'dias_sem_vicio': vicio.dias_sem_vicio,
            'percentual_evolucao': vicio.percentual_evolucao,
        }
        for vicio in vicios
    ]
    return render(request, 'progressos.html', {'progressos': progressos})


# ─────────────────────────────────────────────
# DEMAIS PÁGINAS (somente leitura / já existiam)
# ─────────────────────────────────────────────
@login_obrigatorio
def categorias_view(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias.html', {'categorias': categorias})


@login_obrigatorio
def conquistas_view(request):
    usuario = usuario_logado(request)
    conquistas = Conquista.objects.filter(usuario=usuario).select_related('recompensa')
    conquistas_fmt = [
        {
            'usuario': c.usuario.nome,
            'recompensa': c.recompensa.nome,
            'data_desbloqueio': c.data_desbloqueio,
        }
        for c in conquistas
    ]
    return render(request, 'conquistas.html', {'conquistas': conquistas_fmt})


@login_obrigatorio
def recompensas_view(request):
    recompensas = Recompensa.objects.all()
    return render(request, 'recompensas.html', {'recompensas': recompensas})


@login_obrigatorio
def frases_view(request):
    frases = Frase.objects.all()
    return render(request, 'frases.html', {'frases': frases})


@login_obrigatorio
def historicos_view(request):
    usuario = usuario_logado(request)
    historicos = Historico.objects.filter(usuario=usuario)
    historicos_fmt = [
        {
            'usuario': h.usuario.nome,
            'descricao': h.descricao,
            'tipo_evento': h.tipo_evento,
            'data_evento': h.data_evento,
        }
        for h in historicos
    ]
    return render(request, 'historicos.html', {'historicos': historicos_fmt})


@login_obrigatorio
def perfis_view(request):
    usuarios = Usuario.objects.all()
    perfis = [
        {
            'apelido': u.apelido or u.nome,
            'usuario': u.username,
            'objetivo_pessoal': u.objetivo_pessoal,
            'nivel_progresso': u.nivel_progresso,
        }
        for u in usuarios
    ]
    return render(request, 'perfis.html', {'perfis': perfis})