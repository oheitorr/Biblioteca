from django import forms
from .models import (
    Usuario, Vicio, Habito, MetaUsuario, Recaida, Gatilho,
    RegistroGatilho, Rotina, Substituicao, Tarefa
)


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'placeholder': 'Digite seu usuário', 'autofocus': True})
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'})
    )


# ─────────────────────────────────────────────
# CADASTRO DE USUÁRIO
# ─────────────────────────────────────────────
class CadastroForm(forms.Form):
    nome = forms.CharField(
        label='Nome completo',
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome'})
    )
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'placeholder': 'Escolha um nome de usuário'})
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 6 caracteres'})
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'})
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_senha(self):
        senha = self.cleaned_data['senha']
        if len(senha) < 6:
            raise forms.ValidationError('A senha deve ter no mínimo 6 caracteres.')
        return senha

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get('senha')
        confirmar = cleaned.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned


# ─────────────────────────────────────────────
# VÍCIO
# ─────────────────────────────────────────────
class VicioForm(forms.ModelForm):
    class Meta:
        model = Vicio
        fields = ['categoria', 'nome', 'descricao', 'nivel_dependencia', 'data_inicio_jornada']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Cigarro'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Breve descrição', 'rows': 3}),
            'data_inicio_jornada': forms.DateInput(attrs={'type': 'date'}),
        }


# ─────────────────────────────────────────────
# HÁBITO
# ─────────────────────────────────────────────
class HabitoForm(forms.ModelForm):
    class Meta:
        model = Habito
        fields = ['nome', 'descricao', 'dificuldade']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Meditação'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Breve descrição', 'rows': 3}),
        }


# ─────────────────────────────────────────────
# META
# ─────────────────────────────────────────────
class MetaForm(forms.ModelForm):
    class Meta:
        model = MetaUsuario
        fields = ['titulo', 'descricao', 'prazo', 'status']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: 30 dias sem cigarro'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Detalhe sua meta', 'rows': 3}),
            'prazo': forms.DateInput(attrs={'type': 'date'}),
        }


# ─────────────────────────────────────────────
# RECAÍDA
# ─────────────────────────────────────────────
class RecaidaForm(forms.ModelForm):
    class Meta:
        model = Recaida
        fields = ['vicio', 'motivo', 'data']
        widgets = {
            'motivo': forms.Textarea(attrs={'placeholder': 'O que motivou a recaída?', 'rows': 3}),
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['vicio'].queryset = Vicio.objects.filter(usuario=usuario)


# ─────────────────────────────────────────────
# GATILHO
# ─────────────────────────────────────────────
class GatilhoForm(forms.ModelForm):
    class Meta:
        model = Gatilho
        fields = ['nome', 'descricao', 'intensidade']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Estresse'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Breve descrição', 'rows': 3}),
        }


# ─────────────────────────────────────────────
# REGISTRO DE GATILHO
# ─────────────────────────────────────────────
class RegistroGatilhoForm(forms.ModelForm):
    class Meta:
        model = RegistroGatilho
        fields = ['gatilho', 'observacao', 'data']
        widgets = {
            'observacao': forms.Textarea(attrs={'placeholder': 'O que aconteceu?', 'rows': 3}),
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['gatilho'].queryset = Gatilho.objects.filter(usuario=usuario)


# ─────────────────────────────────────────────
# ROTINA
# ─────────────────────────────────────────────
class RotinaForm(forms.ModelForm):
    class Meta:
        model = Rotina
        fields = ['titulo', 'descricao', 'horario']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Manhã Produtiva'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Breve descrição', 'rows': 3}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }


# ─────────────────────────────────────────────
# TAREFA
# ─────────────────────────────────────────────
class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['rotina', 'nome', 'concluida']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Meditar 10 min'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['rotina'].queryset = Rotina.objects.filter(usuario=usuario)

class SubstituicaoForm(forms.ModelForm):
    class Meta:
        model = Substituicao
        fields = ['vicio', 'habito', 'observacao', 'data_inicio']
        widgets = {
            'observacao': forms.Textarea(attrs={'placeholder': 'Observações sobre a troca', 'rows': 3}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['vicio'].queryset = Vicio.objects.filter(usuario=usuario)
            self.fields['habito'].queryset = Habito.objects.filter(usuario=usuario)