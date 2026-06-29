from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from src.metrics import gerar_metricas_dashboard, buscar_ultimas_transacoes, gerar_insights
from src.transform import tratar_transacoes
from src.load import carregar_transacoes_mysql, limpar_transacoes_mysql, obter_engine, garantir_colunas_usuario
from src.transacoes import buscar_todas_transacoes, criar_transacao, editar_transacao, excluir_transacao
from src.metas import buscar_meta_ativa, criar_meta, atualizar_meta, excluir_meta
from src.categorias import buscar_todas_categorias, criar_categoria, atualizar_categoria, excluir_categoria, obter_estatisticas_categoria, inicializar_categorias_padrao
from src.financial_agent import responder_pergunta as responder_pergunta_local
from src.ai_financial_agent import responder_pergunta_openai
from src.relatorios import obter_relatorio
from src.investimentos import atualizar_investimento, buscar_investimento_por_id, criar_investimento, excluir_investimento, listar_investimentos, obter_resumo_investimentos
from src.auth import criar_usuario, buscar_usuario_por_email, verificar_senha
from src.usuario_contexto import definir_usuario_id, limpar_usuario_id
from src.configuracoes import (
    obter_configuracoes_usuario,
    restaurar_configuracoes_padrao,
    salvar_configuracoes_usuario,
)


import os
import pandas as pd
from functools import wraps

app = Flask(__name__)
# Configura Flask para retornar JSON com acentos corretamente
app.config['JSON_AS_ASCII'] = False

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Configura secret key para sessões (exigida)
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("A variável de ambiente SECRET_KEY é obrigatória")
app.secret_key = SECRET_KEY

# Configurações de segurança de sessão
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# SESSION_COOKIE_SECURE: ativo apenas em produção (HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'

# Configuração de debug
DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true' or os.getenv('APP_ENV') == 'development'

# Garante colunas de isolamento por usuário em bancos já existentes
# antes de processar qualquer rota.
garantir_colunas_usuario()

@app.before_request
def definir_contexto_usuario_por_sessao():
    if 'usuario_id' in session:
        definir_usuario_id(session['usuario_id'])
    else:
        limpar_usuario_id()


@app.teardown_request
def limpar_contexto_usuario_por_sessao(_erro=None):
    limpar_usuario_id()


# Decorator para exigir login
def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            # Se a rota for uma API (prefixo /api/), retornamos JSON 401
            if request.path.startswith('/api/'):
                return jsonify({'erro': 'Autenticação necessária.'}), 401
            # Para páginas HTML, redirecionamos para a página de login
            return redirect(url_for('pagina_login'))
        return f(*args, **kwargs)
    return decorated_function


def _configuracoes_da_sessao():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return None
    return obter_configuracoes_usuario(usuario_id)


@app.context_processor
def disponibilizar_preferencias_usuario():
    configuracoes = _configuracoes_da_sessao()
    return {
        'configuracoes': configuracoes or {},
        'usuario_nome': (
            configuracoes.get('nome') if configuracoes else None
        ) or session.get('usuario_nome'),
    }

# Rota principal - exibe a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota do dashboard - exibe a dashboard
@app.route('/dashboard')
@login_obrigatorio
def dashboard():
    return render_template('dashboard.html')

# Rota de transações - exibe a página de transações
@app.route('/transacoes')
@login_obrigatorio
def transacoes():
    return render_template('transacoes.html')

# Rota de metas - exibe a página de metas
@app.route('/metas')
@login_obrigatorio
def metas():
    return render_template('metas.html')

# Rota de categorias - exibe a página de categorias
@app.route('/categorias')
@login_obrigatorio
def categorias():
    return render_template('categorias.html')

# Rota de assistente - exibe a página do assistente financeiro
@app.route('/assistente')
@login_obrigatorio
def assistente():
    return render_template('assistente.html')

@app.route("/relatorios")
@login_obrigatorio
def pagina_relatorios():
    return render_template("relatorios.html")   


@app.route("/investimentos")
@login_obrigatorio
def pagina_investimentos():
    return render_template("investimentos.html")


@app.route("/configuracoes")
@login_obrigatorio
def pagina_configuracoes():
    return render_template("configuracoes.html")


@app.route("/api/configuracoes", methods=["GET", "PUT"])
@login_obrigatorio
def api_configuracoes():
    usuario_id = session['usuario_id']
    try:
        if request.method == "GET":
            return jsonify(obter_configuracoes_usuario(usuario_id)), 200

        dados = request.get_json(silent=True) or {}
        configuracoes = salvar_configuracoes_usuario(usuario_id, dados)
        session['usuario_nome'] = configuracoes['nome'] or session.get('usuario_nome')
        return jsonify({
            "mensagem": "Configurações salvas com sucesso.",
            "configuracoes": configuracoes,
        }), 200
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except Exception as erro:
        print(f"[ERRO] Não foi possível salvar as configurações: {erro}")
        return jsonify({
            "erro": "Não foi possível salvar as configurações.",
        }), 500


@app.route("/api/configuracoes/restaurar", methods=["POST"])
@login_obrigatorio
def api_restaurar_configuracoes():
    try:
        configuracoes = restaurar_configuracoes_padrao(session['usuario_id'])
        session['usuario_nome'] = configuracoes['nome'] or session.get('usuario_nome')
        return jsonify({
            "mensagem": "Configurações padrão restauradas.",
            "configuracoes": configuracoes,
        }), 200
    except Exception as erro:
        print(f"[ERRO] Não foi possível restaurar as configurações: {erro}")
        return jsonify({
            "erro": "Não foi possível restaurar as configurações.",
        }), 500


@app.route("/login")
def pagina_login():
    return render_template("login.html")


@app.route("/cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")


# Rota de API - cadastro de usuário
@app.route('/api/cadastro', methods=['POST'])
def api_cadastro():
    try:
        dados = request.get_json()
        
        # Valida campos obrigatórios
        campos_obrigatorios = ['nome', 'email', 'senha', 'confirmacao_senha']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400
        
        # Valida nome
        nome = dados['nome'].strip()
        if len(nome) < 3:
            return jsonify({'erro': 'Nome deve ter pelo menos 3 caracteres'}), 400
        
        # Valida email
        email = dados['email'].strip().lower()
        if '@' not in email or '.' not in email:
            return jsonify({'erro': 'Email inválido'}), 400
        
        # Valida telefone (opcional)
        telefone = dados.get('telefone', '').strip() if dados.get('telefone') else None
        
        # Valida senha
        senha = dados['senha']
        if len(senha) < 6:
            return jsonify({'erro': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        # Valida confirmação de senha
        confirmacao_senha = dados['confirmacao_senha']
        if senha != confirmacao_senha:
            return jsonify({'erro': 'Senhas não conferem'}), 400
        
        # Cria usuário
        resultado = criar_usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            senha=senha
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 201
        else:
            return jsonify({'erro': resultado['erro']}), 400
            
    except Exception as e:
        print(f"[ERRO] Falha ao criar usuário: {e}")
        return jsonify({'erro': 'Falha ao criar usuário'}), 500


# Rota de API - login de usuário
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        dados = request.get_json()
        
        # Valida campos obrigatórios
        if 'email' not in dados or not dados['email']:
            return jsonify({'erro': 'Email é obrigatório'}), 400
        
        if 'senha' not in dados or not dados['senha']:
            return jsonify({'erro': 'Senha é obrigatória'}), 400
        
        email = dados['email'].strip().lower()
        senha = dados['senha']
        
        # Busca usuário por email
        usuario = buscar_usuario_por_email(email)
        
        if not usuario:
            return jsonify({'erro': 'Email ou senha incorretos'}), 401
        
        # Verifica senha
        if not verificar_senha(usuario['senha_hash'], senha):
            return jsonify({'erro': 'Email ou senha incorretos'}), 401
        
        # Cria sessão com dados do usuário
        session['usuario_id'] = usuario['id']
        session['usuario_nome'] = usuario['nome']
        session['usuario_email'] = usuario['email']
        
        return jsonify({
            'mensagem': 'Login realizado com sucesso',
            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email']
            }
        }), 200
            
    except Exception as e:
        print(f"[ERRO] Falha ao realizar login: {e}")
        return jsonify({'erro': 'Falha ao realizar login'}), 500


# Rota de API - logout de usuário
@app.route('/api/logout', methods=['POST'])
def api_logout():
    try:
        # Remove dados da sessão
        session.pop('usuario_id', None)
        session.pop('usuario_nome', None)
        session.pop('usuario_email', None)
        
        return jsonify({'mensagem': 'Logout realizado com sucesso'}), 200
            
    except Exception as e:
        print(f"[ERRO] Falha ao realizar logout: {e}")
        return jsonify({'erro': 'Falha ao realizar logout'}), 500


# Rota de API - retorna métricas financeiras em JSON
@app.route('/api/metricas')
@login_obrigatorio
def api_metricas():
    try:
        usuario_id = session.get('usuario_id')
        # Busca e calcula as métricas filtradas pelo usuário
        metricas = gerar_metricas_dashboard(usuario_id=usuario_id)

        # Gera insights dinâmicos
        insights = gerar_insights(usuario_id=usuario_id)
        
        # Adiciona insights às métricas
        metricas['insights'] = insights
        
        # Retorna as métricas em formato JSON
        return jsonify(metricas)
        
    except Exception as e:
        print(f"[ERRO] Falha ao buscar métricas: {e}")
        return jsonify({'erro': 'Falha ao buscar métricas'}), 500

@app.route("/api/transacoes")
@login_obrigatorio
def api_transacoes():
    try:
        usuario_id = session.get('usuario_id')
        configuracoes = obter_configuracoes_usuario(usuario_id)
        transacoes = buscar_ultimas_transacoes(
            limite=configuracoes['qtd_transacoes_recentes'],
            usuario_id=usuario_id,
        )
        return jsonify(transacoes)
    except Exception as erro:
        print(f"[ERRO] Não foi possível buscar as últimas transações: {erro}")
        return jsonify({
            "erro": "Não foi possível buscar as últimas transações."
        }), 500

# Rota de API - retorna todas as transações em JSON
@app.route('/api/transacoes/todas')
@login_obrigatorio
def api_transacoes_todas():
    try:
        # Obtém filtros dos parâmetros da query
        filtros = {}
        if request.args.get('descricao'):
            filtros['descricao'] = request.args.get('descricao')
        if request.args.get('categoria'):
            filtros['categoria'] = request.args.get('categoria')
        if request.args.get('tipo'):
            filtros['tipo'] = request.args.get('tipo')
        if request.args.get('status'):
            filtros['status'] = request.args.get('status')
        
        # Busca transações com filtros
        usuario_id = session.get('usuario_id')
        df = buscar_todas_transacoes(filtros if filtros else None, usuario_id=usuario_id)
        
        # Converte DataFrame para lista de dicionários
        transacoes = df.to_dict('records')
        
        # Retorna as transações em formato JSON
        return jsonify(transacoes)
        
    except Exception as e:
        print(f"[ERRO] Falha ao buscar transações: {e}")
        return jsonify({'erro': 'Falha ao buscar transações'}), 500

# Rota de API - cria uma nova transação
@app.route('/api/transacoes', methods=['POST'])
@login_obrigatorio
def api_criar_transacao():
    try:
        # Obtém dados do JSON
        dados = request.get_json()
        
        # Valida campos obrigatórios
        campos_obrigatorios = ['data', 'descricao', 'categoria', 'tipo', 'valor', 'status']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400
        
        # Valida valor
        try:
            valor = float(dados['valor'])
            if valor <= 0:
                return jsonify({'erro': 'Valor deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'erro': 'Valor deve ser um número válido'}), 400
        
        # Valida tipo
        tipos_permitidos = ['entrada', 'saida', 'investimento']
        if dados['tipo'] not in tipos_permitidos:
            return jsonify({'erro': f'Tipo deve ser um de: {", ".join(tipos_permitidos)}'}), 400
        
        # Valida status
        status_permitidos = ['confirmado', 'pendente', 'cancelado']
        if dados['status'] not in status_permitidos:
            return jsonify({'erro': f'Status deve ser um de: {", ".join(status_permitidos)}'}), 400
        
        # Cria transação
        usuario_id = session.get('usuario_id')

        resultado = criar_transacao(
            data_transacao=dados['data'],
            descricao=dados['descricao'],
            categoria=dados['categoria'],
            tipo=dados['tipo'],
            valor=valor,
            conta=dados.get('conta', ''),
            instituicao=dados.get('instituicao', ''),
            status=dados['status'],
            usuario_id=usuario_id
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 201
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        print(f"[ERRO] Falha ao criar transação: {e}")
        return jsonify({'erro': 'Falha ao criar transação'}), 500

# Rota de API - edita uma transação existente
@app.route('/api/transacoes/<int:id>', methods=['PUT'])
@login_obrigatorio
def api_editar_transacao(id):
    try:
        # Obtém dados do JSON
        dados = request.get_json()
        
        # Valida campos obrigatórios
        campos_obrigatorios = ['data', 'descricao', 'categoria', 'tipo', 'valor', 'status']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400
        
        # Valida valor
        try:
            valor = float(dados['valor'])
            if valor <= 0:
                return jsonify({'erro': 'Valor deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'erro': 'Valor deve ser um número válido'}), 400
        
        # Valida tipo
        tipos_permitidos = ['entrada', 'saida', 'investimento']
        if dados['tipo'] not in tipos_permitidos:
            return jsonify({'erro': f'Tipo deve ser um de: {", ".join(tipos_permitidos)}'}), 400
        
        # Valida status
        status_permitidos = ['confirmado', 'pendente', 'cancelado']
        if dados['status'] not in status_permitidos:
            return jsonify({'erro': f'Status deve ser um de: {", ".join(status_permitidos)}'}), 400
        
        # Edita transação
        usuario_id = session.get('usuario_id')

        resultado = editar_transacao(
            id_transacao=id,
            data_transacao=dados['data'],
            descricao=dados['descricao'],
            categoria=dados['categoria'],
            tipo=dados['tipo'],
            valor=valor,
            conta=dados.get('conta', ''),
            instituicao=dados.get('instituicao', ''),
            status=dados['status'],
            usuario_id=usuario_id
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        print(f"[ERRO] Falha ao editar transação: {e}")
        return jsonify({'erro': 'Falha ao editar transação'}), 500

# Rota de API - exclui uma transação
@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
@login_obrigatorio
def api_excluir_transacao(id):
    try:
        # Exclui transação
        usuario_id = session.get('usuario_id')
        resultado = excluir_transacao(id, usuario_id=usuario_id)
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        print(f"[ERRO] Falha ao excluir transação: {e}")
        return jsonify({'erro': 'Falha ao excluir transação'}), 500
        
@app.route("/api/upload", methods=["POST"])
@login_obrigatorio
def api_upload():
    try:
        if "arquivo" not in request.files:
            return jsonify({
                "erro": "Nenhum arquivo foi enviado."
            }), 400

        arquivo = request.files["arquivo"]

        if arquivo.filename == "":
            return jsonify({
                "erro": "Nenhum arquivo foi selecionado."
            }), 400

        if not arquivo.filename.endswith(".csv"):
            return jsonify({
                "erro": "Envie apenas arquivos CSV."
            }), 400

        caminho_uploads = "uploads"
        os.makedirs(caminho_uploads, exist_ok=True)

        caminho_arquivo = os.path.join(caminho_uploads, arquivo.filename)
        arquivo.save(caminho_arquivo)

        df = pd.read_csv(caminho_arquivo)
        df_tratado, contador_categorizadas = tratar_transacoes(df)
        usuario_id = session.get('usuario_id')
        resultado_carga = carregar_transacoes_mysql(
            df_tratado,
            usuario_id=usuario_id,
        )

        return {
            "mensagem": "Planilha processada com sucesso.",
            "recebidos": resultado_carga["recebidos"],
            "importados": resultado_carga["importados"],
            "ignorados": resultado_carga["ignorados"],
            "categorizadas_automaticamente": contador_categorizadas
        }

    except Exception as erro:
        print(f"[ERRO] Não foi possível importar a planilha: {erro}")
        return jsonify({
            "erro": "Não foi possível importar a planilha."
        }), 500


@app.route("/api/transacoes/limpar", methods=["DELETE"])
@login_obrigatorio
def api_limpar_transacoes():
    try:
        usuario_id = session.get('usuario_id')
        # Limpa apenas as transações do usuário
        limpar_transacoes_mysql(usuario_id=usuario_id)

        return jsonify({
            "mensagem": "Todos os dados foram removidos com sucesso."
        })

    except Exception as erro:
        print(f"[ERRO] Não foi possível limpar os dados: {erro}")
        return jsonify({
            "erro": "Não foi possível limpar os dados."
        }), 500

# Rota de API - retorna a meta ativa
@app.route('/api/meta')
@login_obrigatorio
def api_meta():
    try:
        usuario_id = session.get('usuario_id')
        meta = buscar_meta_ativa(usuario_id=usuario_id)
        
        if meta is None:
            return jsonify({'meta': None})
        
        # Calcula percentual e valor restante
        valor_meta = meta['valor_meta']
        valor_atual = meta['valor_atual']
        
        # Calcula percentual (máximo 100%)
        if valor_meta > 0:
            percentual = (valor_atual / valor_meta) * 100
            percentual = min(percentual, 100)  # Limita a 100%
        else:
            percentual = 0
        
        # Calcula valor restante
        valor_restante = max(valor_meta - valor_atual, 0)
        
        # Adiciona campos calculados
        meta['percentual'] = round(percentual, 1)
        meta['valor_restante'] = round(valor_restante, 2)
        
        return jsonify(meta)
        
    except Exception as e:
        print(f"[ERRO] Falha ao buscar meta: {e}")
        return jsonify({'erro': 'Falha ao buscar meta'}), 500

# Rota de API - cria uma nova meta
@app.route('/api/meta', methods=['POST'])
@login_obrigatorio
def api_criar_meta():
    try:
        dados = request.get_json()
        
        # Valida campos obrigatórios
        if 'titulo' not in dados or not dados['titulo']:
            return jsonify({'erro': 'Campo título é obrigatório'}), 400
        
        if 'valor_meta' not in dados:
            return jsonify({'erro': 'Campo valor_meta é obrigatório'}), 400
        
        # Valida valor_meta
        try:
            valor_meta = float(dados['valor_meta'])
            if valor_meta <= 0:
                return jsonify({'erro': 'Valor da meta deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'erro': 'Valor da meta deve ser um número válido'}), 400
        
        # Valida valor_atual se fornecido
        valor_atual = 0.0
        if 'valor_atual' in dados:
            try:
                valor_atual = float(dados['valor_atual'])
                if valor_atual < 0:
                    return jsonify({'erro': 'Valor atual não pode ser negativo'}), 400
            except (ValueError, TypeError):
                return jsonify({'erro': 'Valor atual deve ser um número válido'}), 400
        
        # Valida status se fornecido
        status = dados.get('status', 'ativa')
        if status not in ['ativa', 'concluida', 'cancelada']:
            return jsonify({'erro': 'Status deve ser ativa, concluida ou cancelada'}), 400
        
        # Cria meta
        usuario_id = session.get('usuario_id')

        id_meta = criar_meta(
            titulo=dados['titulo'],
            valor_meta=valor_meta,
            valor_atual=valor_atual,
            data_limite=dados.get('data_limite'),
            status=status
            , usuario_id=usuario_id
        )
        
        return jsonify({'mensagem': 'Meta criada com sucesso', 'id': id_meta}), 201
        
    except Exception as e:
        print(f"[ERRO] Falha ao criar meta: {e}")
        return jsonify({'erro': 'Falha ao criar meta'}), 500

# Rota de API - atualiza uma meta existente
@app.route('/api/meta/<int:id>', methods=['PUT'])
@login_obrigatorio
def api_atualizar_meta(id):
    try:
        dados = request.get_json()
        
        # Valida valor_meta se fornecido
        if 'valor_meta' in dados:
            try:
                valor_meta = float(dados['valor_meta'])
                if valor_meta <= 0:
                    return jsonify({'erro': 'Valor da meta deve ser maior que zero'}), 400
                dados['valor_meta'] = valor_meta
            except (ValueError, TypeError):
                return jsonify({'erro': 'Valor da meta deve ser um número válido'}), 400
        
        # Valida valor_atual se fornecido
        if 'valor_atual' in dados:
            try:
                valor_atual = float(dados['valor_atual'])
                if valor_atual < 0:
                    return jsonify({'erro': 'Valor atual não pode ser negativo'}), 400
                dados['valor_atual'] = valor_atual
            except (ValueError, TypeError):
                return jsonify({'erro': 'Valor atual deve ser um número válido'}), 400
        
        # Valida status se fornecido
        if 'status' in dados:
            if dados['status'] not in ['ativa', 'concluida', 'cancelada']:
                return jsonify({'erro': 'Status deve ser ativa, concluida ou cancelada'}), 400
        
        # Atualiza meta
        usuario_id = session.get('usuario_id')

        sucesso = atualizar_meta(
            id_meta=id,
            titulo=dados.get('titulo'),
            valor_meta=dados.get('valor_meta'),
            valor_atual=dados.get('valor_atual'),
            data_limite=dados.get('data_limite'),
            status=dados.get('status')
            , usuario_id=usuario_id
        )
        
        if sucesso:
            return jsonify({'mensagem': 'Meta atualizada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Meta não encontrada'}), 404
            
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar meta: {e}")
        return jsonify({'erro': 'Falha ao atualizar meta'}), 500

# Rota de API - exclui uma meta
@app.route('/api/meta/<int:id>', methods=['DELETE'])
@login_obrigatorio
def api_excluir_meta(id):
    try:
        usuario_id = session.get('usuario_id')
        sucesso = excluir_meta(id, usuario_id=usuario_id)
        
        if sucesso:
            return jsonify({'mensagem': 'Meta excluída com sucesso'}), 200
        else:
            return jsonify({'erro': 'Meta não encontrada'}), 404
            
    except Exception as e:
        print(f"[ERRO] Falha ao excluir meta: {e}")
        return jsonify({'erro': 'Falha ao excluir meta'}), 500

# Rota de API - retorna todas as categorias
@app.route('/api/categorias')
@login_obrigatorio
def api_categorias():
    try:
        # Inicializa categorias padrão se necessário (por usuário)
        usuario_id = session.get('usuario_id')
        inicializar_categorias_padrao(usuario_id=usuario_id)

        categorias = buscar_todas_categorias(usuario_id=usuario_id)
        
        # Adiciona estatísticas para cada categoria
        for categoria in categorias:
            estatisticas = obter_estatisticas_categoria(categoria['nome'], usuario_id=usuario_id)
            categoria['quantidade_transacoes'] = estatisticas['quantidade']
            categoria['valor_total'] = estatisticas['valor_total']
        
        return jsonify(categorias)
        
    except Exception as e:
        print(f"[ERRO] Falha ao buscar categorias: {e}")
        return jsonify({'erro': 'Falha ao buscar categorias'}), 500

# Rota de API - cria uma nova categoria
@app.route('/api/categorias', methods=['POST'])
@login_obrigatorio
def api_criar_categoria():
    try:
        dados = request.get_json()
        
        # Valida campos obrigatórios
        if not dados.get('nome'):
            return jsonify({'erro': 'Nome da categoria é obrigatório'}), 400
        
        # Cria categoria
        usuario_id = session.get('usuario_id')

        resultado = criar_categoria(
            nome=dados['nome'],
            palavras_chave=dados.get('palavras_chave', []),
            cor=dados.get('cor'),
            usuario_id=usuario_id
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 201
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        print(f"[ERRO] Falha ao criar categoria: {e}")
        return jsonify({'erro': 'Falha ao criar categoria'}), 500

# Rota de API - atualiza uma categoria
@app.route('/api/categorias/<nome>', methods=['PUT'])
@login_obrigatorio
def api_atualizar_categoria(nome):
    try:
        dados = request.get_json()
        usuario_id = session.get('usuario_id')

        # Atualiza categoria
        resultado = atualizar_categoria(
            nome_atual=nome,
            novo_nome=dados.get('nome'),
            palavras_chave=dados.get('palavras_chave'),
            cor=dados.get('cor'),
            usuario_id=usuario_id
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar categoria: {e}")
        return jsonify({'erro': 'Falha ao atualizar categoria'}), 500

# Rota de API - exclui uma categoria
@app.route('/api/categorias/<nome>', methods=['DELETE'])
@login_obrigatorio
def api_excluir_categoria(nome):
    try:
        usuario_id = session.get('usuario_id')
        resultado = excluir_categoria(nome, usuario_id=usuario_id)
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        print(f"[ERRO] Falha ao excluir categoria: {e}")
        return jsonify({'erro': 'Falha ao excluir categoria'}), 500

# Rota de API - processa pergunta do assistente financeiro
@app.route('/api/assistente', methods=['POST'])
@login_obrigatorio
def api_assistente():
    try:
        dados = request.get_json()
        usuario_id = session.get("usuario_id")

        if not usuario_id:
            return jsonify({'erro': 'Autenticação necessária.'}), 401
        
        # Validação
        if not dados or 'pergunta' not in dados:
            return jsonify({'erro': 'Pergunta é obrigatória'}), 400
        
        pergunta = dados['pergunta'].strip()
        
        if not pergunta:
            return jsonify({'erro': 'Pergunta não pode estar vazia'}), 400
        
        if len(pergunta) > 500:
            return jsonify({'erro': 'Pergunta muito longa (máximo 500 caracteres)'}), 400
        
        # Tenta usar OpenAI primeiro
        try:
            resultado = responder_pergunta_openai(pergunta)
            print(f"[API] Resposta OpenAI obtida com sucesso")
            return jsonify(resultado), 200
        except Exception as e:
            print(f"[API] Fallback para agente local devido a erro: {e}")
            # Fallback para agente local
            resultado_local = responder_pergunta_local(pergunta)
            # Adiciona origem local
            resultado_local['origem'] = 'local'
            resultado_local['ferramenta'] = resultado_local.get('tipo')
            return jsonify(resultado_local), 200
        
    except Exception as e:
        print(f"[ERRO] Erro ao processar pergunta do assistente: {e}")
        return jsonify({'erro': 'Erro ao processar pergunta', 'resposta': 'Ocorreu um erro ao processar sua pergunta. Tente novamente.'}), 500
        
@app.route("/api/relatorios", methods=["GET"])
@login_obrigatorio
def api_relatorios():
    try:
        data_inicio = request.args.get("data_inicio")
        data_fim = request.args.get("data_fim")
        usuario_id = session.get("usuario_id")

        relatorio = obter_relatorio(
            data_inicio=data_inicio,
            data_fim=data_fim,
            usuario_id=usuario_id,
        )

        return jsonify(relatorio), 200

    except ValueError as erro:
        return jsonify({
            "erro": str(erro)
        }), 400

    except Exception as erro:
        print(f"[ERRO] Erro ao gerar relatório: {erro}")
        return jsonify({
            "erro": "Não foi possível gerar o relatório."
        }), 500


@app.route("/api/investimentos", methods=["GET"])
@login_obrigatorio
def api_listar_investimentos():
    try:
        status = request.args.get("status")
        usuario_id = session.get("usuario_id")

        investimentos = listar_investimentos(
            status=status,
            usuario_id=usuario_id,
        )

        return jsonify(investimentos), 200

    except ValueError as erro:
        return jsonify({
            "erro": str(erro)
        }), 400

    except Exception as erro:
        print(f"[ERRO] Erro ao listar investimentos: {erro}")
        return jsonify({
            "erro": "Não foi possível listar os investimentos."
        }), 500


@app.route(
    "/api/investimentos/<int:investimento_id>",
    methods=["GET"],
)
@login_obrigatorio
def api_buscar_investimento(investimento_id):
    try:
        usuario_id = session.get("usuario_id")
        investimento = buscar_investimento_por_id(
            investimento_id,
            usuario_id=usuario_id,
        )

        if not investimento:
            return jsonify({
                "erro": "Investimento não encontrado."
            }), 404

        return jsonify(investimento), 200

    except Exception as erro:
        print(f"[ERRO] Erro ao buscar investimento: {erro}")
        return jsonify({
            "erro": "Não foi possível buscar o investimento."
        }), 500


@app.route("/api/investimentos", methods=["POST"])
@login_obrigatorio
def api_criar_investimento():
    try:
        dados = request.get_json(silent=True)
        usuario_id = session.get("usuario_id")

        if not dados:
            return jsonify({
                "erro": "O corpo da requisição é obrigatório."
            }), 400

        investimento = criar_investimento(
            dados,
            usuario_id=usuario_id,
        )

        return jsonify({
            "mensagem": "Investimento criado com sucesso.",
            "investimento": investimento,
        }), 201

    except ValueError as erro:
        return jsonify({
            "erro": str(erro)
        }), 400

    except Exception as erro:
        print(f"[ERRO] Erro ao criar investimento: {erro}")
        return jsonify({
            "erro": "Não foi possível criar o investimento."
        }), 500


@app.route(
    "/api/investimentos/<int:investimento_id>",
    methods=["PUT"],
)
@login_obrigatorio
def api_atualizar_investimento(investimento_id):
    try:
        dados = request.get_json(silent=True)
        usuario_id = session.get("usuario_id")

        if not dados:
            return jsonify({
                "erro": "O corpo da requisição é obrigatório."
            }), 400

        investimento = atualizar_investimento(
            investimento_id,
            dados,
            usuario_id=usuario_id,
        )

        if not investimento:
            return jsonify({
                "erro": "Investimento não encontrado."
            }), 404

        return jsonify({
            "mensagem": "Investimento atualizado com sucesso.",
            "investimento": investimento,
        }), 200

    except ValueError as erro:
        return jsonify({
            "erro": str(erro)
        }), 400

    except Exception as erro:
        print(f"[ERRO] Erro ao atualizar investimento: {erro}")
        return jsonify({
            "erro": "Não foi possível atualizar o investimento."
        }), 500


@app.route(
    "/api/investimentos/<int:investimento_id>",
    methods=["DELETE"],
)
@login_obrigatorio
def api_excluir_investimento(investimento_id):
    try:
        usuario_id = session.get("usuario_id")
        investimento_excluido = excluir_investimento(
            investimento_id,
            usuario_id=usuario_id,
        )

        if not investimento_excluido:
            return jsonify({
                "erro": "Investimento não encontrado."
            }), 404

        return jsonify({
            "mensagem": "Investimento excluído com sucesso."
        }), 200

    except Exception as erro:
        print(f"[ERRO] Erro ao excluir investimento: {erro}")
        return jsonify({
            "erro": "Não foi possível excluir o investimento."
        }), 500


@app.route(
    "/api/investimentos/resumo",
    methods=["GET"],
)
@login_obrigatorio
def api_resumo_investimentos():
    try:
        usuario_id = session.get("usuario_id")
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        return jsonify(resumo), 200

    except Exception as erro:
        print(f"[ERRO] Erro ao gerar resumo de investimentos: {erro}")
        return jsonify({
            "erro": "Não foi possível gerar o resumo dos investimentos."
        }), 500

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=DEBUG,
    )
