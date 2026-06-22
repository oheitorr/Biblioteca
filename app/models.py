from django.db import models
from django.utils import timezone
import hashlib



class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    senha_hash = models.CharField(max_length=128)
    apelido = models.CharField(max_length=50, blank=True)
    objetivo_pessoal = models.CharField(max_length=200, blank=True, default='Superar meus vícios')
    nivel_progresso = models.IntegerField(default=1)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def set_senha(self, senha_pura):
        self.senha_hash = hashlib.sha256(senha_pura.encode('utf-8')).hexdigest()

    def checar_senha(self, senha_pura):
        return self.senha_hash == hashlib.sha256(senha_pura.encode('utf-8')).hexdigest()

    def __str__(self):
        return self.username
class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
class Vicio(models.Model):
    NIVEL_CHOICES = [
        ('Baixo', 'Baixo'),
        ('Médio', 'Médio'),
        ('Alto', 'Alto'),
        ('Muito Alto', 'Muito Alto'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='vicios')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    nivel_dependencia = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='Médio')
    data_inicio_jornada = models.DateField(default=timezone.now)

    def __str__(self):
        return self.nome
    @property
    def dias_sem_vicio(self):
        """
        Conta os dias desde a última recaída registrada para este vício.
        Se nunca houve recaída, conta a partir da data_inicio_jornada.
        """
        ultima_recaida = self.recaidas.order_by('-data').first()
        data_base = ultima_recaida.data if ultima_recaida else self.data_inicio_jornada
        delta = (timezone.now().date() - data_base).days
        return max(delta, 0)
    @property
    def streak_atual(self):
        return self.dias_sem_vicio
    @property
    def recorde_pessoal(self):
        """
        Maior sequência já alcançada: olha o intervalo entre recaídas
        consecutivas (e entre o início da jornada e a primeira recaída),
        além do streak atual em andamento.
        """
        recaidas = list(self.recaidas.order_by('data'))
        if not recaidas:
            return self.streak_atual

        maior = 0
        data_anterior = self.data_inicio_jornada
        for r in recaidas:
            intervalo = (r.data - data_anterior).days
            maior = max(maior, intervalo)
            data_anterior = r.data

        maior = max(maior, self.streak_atual)
        return maior

    @property
    def percentual_evolucao(self):
        """
        Percentual de progresso em relação à meta de 90 dias (configurável).
        Limitado em 100%.
        """
        META_DIAS = 90
        pct = round((self.dias_sem_vicio / META_DIAS) * 100)
        return min(pct, 100)

class Habito(models.Model):
    DIFICULDADE_CHOICES = [
        ('Baixa', 'Baixa'),
        ('Média', 'Média'),
        ('Alta', 'Alta'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='habitos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    dificuldade = models.CharField(max_length=10, choices=DIFICULDADE_CHOICES, default='Média')
    data_cadastro = models.DateField(default=timezone.now)

    def __str__(self):
        return self.nome


class MetaUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='metas')
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    prazo = models.DateField()
    status = models.BooleanField(default=False)  # False = Em andamento, True = Concluída

    def __str__(self):
        return self.titulo


class Recaida(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='recaidas')
    vicio = models.ForeignKey(Vicio, on_delete=models.CASCADE, related_name='recaidas')
    motivo = models.TextField(blank=True)
    data = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'{self.vicio.nome} — {self.data}'

class Gatilho(models.Model):
    INTENSIDADE_CHOICES = [
        ('Baixa', 'Baixa'),
        ('Média', 'Média'),
        ('Alta', 'Alta'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gatilhos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    intensidade = models.CharField(max_length=10, choices=INTENSIDADE_CHOICES, default='Média')

    def __str__(self):
        return self.nome


class RegistroGatilho(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros_gatilho')
    gatilho = models.ForeignKey(Gatilho, on_delete=models.CASCADE, related_name='registros')
    observacao = models.TextField(blank=True)
    data = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'{self.gatilho.nome} — {self.data}'
    
class Rotina(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='rotinas')
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    horario = models.TimeField()

    def __str__(self):
        return self.titulo

class Tarefa(models.Model):
    rotina = models.ForeignKey(Rotina, on_delete=models.CASCADE, related_name='tarefas')
    nome = models.CharField(max_length=150)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

class Substituicao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='substituicoes')
    vicio = models.ForeignKey(Vicio, on_delete=models.CASCADE, related_name='substituicoes')
    habito = models.ForeignKey(Habito, on_delete=models.CASCADE, related_name='substituicoes')
    observacao = models.TextField(blank=True)
    data_inicio = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.vicio.nome} → {self.habito.nome}'

class Recompensa(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    criterio = models.CharField(max_length=100, help_text='Ex: 7 dias, 30 dias')
    dias_necessarios = models.IntegerField(default=7)

    def __str__(self):
        return self.nome

class Conquista(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='conquistas')
    recompensa = models.ForeignKey(Recompensa, on_delete=models.CASCADE)
    data_desbloqueio = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.usuario.username} — {self.recompensa.nome}'

class Frase(models.Model):
    frase = models.TextField()
    autor = models.CharField(max_length=100, default='Anônimo')
    categoria = models.CharField(max_length=50, default='Motivação')

    def __str__(self):
        return self.frase[:50]

class Historico(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historicos')
    descricao = models.CharField(max_length=255)
    tipo_evento = models.CharField(max_length=50, default='geral')
    data_evento = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_evento']

    def __str__(self):
        return self.descricao