from flask import Flask, render_template, redirect, request, flash, session
import json
import os

app = Flask(__name__)
# É essencial usar uma chave secreta segura e única.
# NUNCA use 'THIMENDES' em produção.
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_e_longa_aqui'

# Função para carregar os usuários do arquivo JSON
def carregar_usuarios():
    try:
        with open('usuarios.json', 'r') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver vazio/corrompido, retorna uma lista vazia
        return []

# Função para salvar os usuários no arquivo JSON
def salvar_usuarios(usuarios):
    with open('usuarios.json', 'w') as arquivo:
        json.dump(usuarios, arquivo, indent=4)

@app.route('/')
def home():
    # Limpa a sessão ao retornar para a página inicial
    session.pop('logado', None)
    return render_template('login.html')

@app.route('/adm')
def adm():
    # Verifica se o usuário está logado usando a sessão
    if session.get('logado'):
        usuarios = carregar_usuarios()
        return render_template('administrador.html', usuarios=usuarios)
    else:
        # Redireciona para a página de login se não estiver logado
        flash('Você precisa estar logado para acessar a página de administrador.')
        return redirect('/')

@app.route('/usuarios')
def usuarios():
    if logado == True:
        arquivo = []
    for documento in os.path.join(app.root_path, 'static', 'arquivos'):
        arquivo.append(documento)
        return render_template("usuarios.html", arquivos=arquivo)
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    
    if not nome or not senha:
        flash('Nome de usuário e senha são obrigatórios.')
        return redirect('/')

    # Credenciais do administrador
    if nome == 'adm' and senha == '000':
        session['logado'] = True
        return redirect('/adm')

    # Validação de usuário normal
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario['nome'] == nome and usuario['senha'] == senha:
            # Redireciona para uma página de usuário ou exibe uma mensagem
            flash(f"Bem-vindo, {nome}!")
            return render_template("usuarios.html", user=usuario)
    
    # Se nenhuma credencial corresponder
    flash('Nome de usuário ou senha inválidos.')
    return redirect("/")
    
@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    if not session.get('logado'):
        flash('Você precisa estar logado para cadastrar um usuário.')
        return redirect('/')

    nome = request.form.get('nome')
    senha = request.form.get('senha')

    if not nome or not senha:
        flash('Nome e senha são obrigatórios para o cadastro.')
        return redirect('/adm')

    usuarios = carregar_usuarios()
    
    # Adiciona o novo usuário
    novo_usuario = {"nome": nome, "senha": senha}
    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)
    
    flash(f'{nome} Cadastrado com sucesso!')
    return redirect('/adm')

@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():
    if not session.get('logado'):
        flash('Você precisa estar logado para excluir um usuário.')
        return redirect('/')

    nome_para_excluir = request.form.get('usuarioPexcluir')

    usuarios = carregar_usuarios()
    
    # Filtra o usuário a ser excluído
    usuarios_atualizados = [u for u in usuarios if u['nome'] != nome_para_excluir]
    
    # Verifica se algum usuário foi realmente removido
    if len(usuarios_atualizados) < len(usuarios):
        salvar_usuarios(usuarios_atualizados)
        # Use a variável nome_para_excluir, que foi definida.
        flash(f'Usuário {nome_para_excluir} Excluído com sucesso!')
    else:
        flash(f'Usuário {nome_para_excluir} não encontrado.')
    
    return redirect('/adm')

if __name__ == "__main__":
    # Garante que o arquivo usuarios.json exista ao iniciar a aplicação
    if not os.path.exists('usuarios.json'):
        salvar_usuarios([])
    app.run(debug=True)
