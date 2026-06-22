from app.models import *
from django.utils import timezone
from datetime import date

# ---------------- USUÁRIO ----------------

usuario, criado = Usuario.objects.get_or_create(

    username='heitor',

    defaults={

        'nome': 'Heitor',

        'apelido': 'Heitor',

        'objetivo_pessoal': 'Superar meus vícios'

    }

)

if criado:

    usuario.set_senha('123456')

    usuario.save()


# ---------------- CATEGORIAS ----------------

categorias = []

for nome in [

    'Redes Sociais',

    'Jogos',

    'Açúcar',

    'Café',

    'Procrastinação'

]:

    categoria, _ = Categoria.objects.get_or_create(

        nome=nome

    )

    categorias.append(categoria)


# ---------------- VÍCIOS ----------------

vicios = []

nomes_vicios = [

    'Instagram',

    'TikTok',

    'Videogame',

    'Doces',

    'Procrastinação'

]

for categoria, nome in zip(categorias, nomes_vicios):

    vicio, _ = Vicio.objects.get_or_create(

        usuario=usuario,

        nome=nome,

        defaults={

            'categoria': categoria,

            'descricao': 'Registro de teste.',

            'nivel_dependencia': 'Médio'

        }

    )

    vicios.append(vicio)


# ---------------- HÁBITOS ----------------

habitos = []

for nome in [

    'Leitura',

    'Caminhada',

    'Academia',

    'Meditação',

    'Estudo'

]:

    habito, _ = Habito.objects.get_or_create(

        usuario=usuario,

        nome=nome,

        defaults={

            'descricao': 'Hábito saudável.',

            'dificuldade': 'Média'

        }

    )

    habitos.append(habito)


# ---------------- METAS ----------------

for i in range(5):

    MetaUsuario.objects.get_or_create(

        usuario=usuario,

        titulo=f'Meta {i+1}',

        defaults={

            'descricao': 'Meta de teste.',

            'prazo': date(2026, 12, 31)

        }

    )


# ---------------- RECAÍDAS ----------------

for vicio in vicios:

    Recaida.objects.get_or_create(

        usuario=usuario,

        vicio=vicio,

        defaults={

            'motivo': 'Teste',

            'data': timezone.now()

        }

    )


# ---------------- GATILHOS ----------------

gatilhos = []

for nome in [

    'Ansiedade',

    'Tédio',

    'Estresse',

    'Solidão',

    'Cansaço'

]:

    gatilho, _ = Gatilho.objects.get_or_create(

        usuario=usuario,

        nome=nome,

        defaults={

            'descricao': 'Teste',

            'intensidade': 'Média'

        }

    )

    gatilhos.append(gatilho)


# ---------------- REGISTRO GATILHOS ----------------

for gatilho in gatilhos:

    RegistroGatilho.objects.get_or_create(

        usuario=usuario,

        gatilho=gatilho,

        defaults={

            'observacao': 'Teste'

        }

    )


# ---------------- ROTINAS ----------------

rotinas = []

for nome in [

    'Matinal',

    'Estudos',

    'Noturna',

    'Exercícios',

    'Fim de semana'

]:

    rotina, _ = Rotina.objects.get_or_create(

        usuario=usuario,

        titulo=nome,

        defaults={

            'descricao': 'Rotina diária.',

            'horario': '08:00'

        }

    )

    rotinas.append(rotina)


# ---------------- TAREFAS ----------------

for i, rotina in enumerate(rotinas):

    Tarefa.objects.get_or_create(

        rotina=rotina,

        nome=f'Tarefa {i+1}'

    )


# ---------------- SUBSTITUIÇÕES ----------------

for vicio, habito in zip(vicios, habitos):

    Substituicao.objects.get_or_create(

        usuario=usuario,

        vicio=vicio,

        habito=habito,

        defaults={

            'observacao': 'Substituição saudável.'

        }

    )


# ---------------- RECOMPENSAS ----------------

recompensas = []

for nome in [

    'Filme',

    'Descanso',

    'Sobremesa',

    'Passeio',

    'Lazer'

]:

    recompensa, _ = Recompensa.objects.get_or_create(

        nome=nome,

        defaults={

            'descricao': 'Recompensa de teste.',

            'criterio': '7 dias',

            'dias_necessarios': 7

        }

    )

    recompensas.append(recompensa)


# ---------------- CONQUISTAS ----------------

for recompensa in recompensas:

    Conquista.objects.get_or_create(

        usuario=usuario,

        recompensa=recompensa

    )


# ---------------- FRASES ----------------

for frase in [

    'Um dia de cada vez.',

    'Persistir é vencer.',

    'A disciplina vence a motivação.',

    'Pequenos passos geram grandes mudanças.',

    'Você é maior que seus hábitos.'

]:

    Frase.objects.get_or_create(

        frase=frase

    )


# ---------------- HISTÓRICO ----------------

for i in range(5):

    Historico.objects.get_or_create(

        usuario=usuario,

        descricao=f'Evento {i+1}'

    )


print('Banco populado com sucesso.')