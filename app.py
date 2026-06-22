from flask import Flask, render_template, jsonify, request
from src.metrics import gerar_metricas_dashboard, buscar_ultimas_transacoes, gerar_insights
from src.transform import tratar_transacoes
from src.load import carregar_transacoes_mysql, limpar_transacoes_mysql
from src.transacoes import buscar_todas_transacoes, criar_transacao, editar_transacao, excluir_transacao
from src.metas import buscar_meta_ativa, criar_meta, atualizar_meta, excluir_meta
from src.categorias import buscar_todas_categorias, criar_categoria, atualizar_categoria, excluir_categoria, obter_estatisticas_categoria, inicializar_categorias_padrao, buscar_categoria_por_id

import os
import pandas as pd

app = Flask(__name__)
# Configura Flask para retornar JSON com acentos corretamente
app.config['JSON_AS_ASCII'] = False

# Rota principal - exibe a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota do dashboard - exibe a dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Rota de transações - exibe a página de transações
@app.route('/transacoes')
def transacoes():
    return render_template('transacoes.html')

# Rota de metas - exibe a página de metas
@app.route('/metas')
def metas():
    return render_template('metas.html')

# Rota de categorias - exibe a página de categorias
@app.route('/categorias')
def categorias():
    return render_template('categorias.html')

# Rota de API - retorna métricas financeiras em JSON
@app.route('/api/metricas')
def api_metricas():
    try:
        # Busca e calcula as métricas
        metricas = gerar_metricas_dashboard()
        
        # Gera insights dinâmicos
        insights = gerar_insights()
        
        # Adiciona insights às métricas
        metricas['insights'] = insights
        
        # Retorna as métricas em formato JSON
        return jsonify(metricas)
        
    except Exception as e:
        # Em caso de erro, retorna mensagem de falha
        return jsonify({'erro': 'Falha ao buscar métricas', 'detalhes': str(e)}), 500

@app.route("/api/transacoes")
def api_transacoes():
    try:
        transacoes = buscar_ultimas_transacoes()
        return jsonify(transacoes)
    except Exception as erro:
        return jsonify({
            "erro": "Não foi possível buscar as últimas transações.",
            "detalhe": str(erro)
        }), 500

# Rota de API - retorna todas as transações em JSON
@app.route('/api/transacoes/todas')
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
        df = buscar_todas_transacoes(filtros if filtros else None)
        
        # Converte DataFrame para lista de dicionários
        transacoes = df.to_dict('records')
        
        # Retorna as transações em formato JSON
        return jsonify(transacoes)
        
    except Exception as e:
        # Em caso de erro, retorna mensagem de falha
        return jsonify({'erro': 'Falha ao buscar transações', 'detalhes': str(e)}), 500

# Rota de API - cria uma nova transação
@app.route('/api/transacoes', methods=['POST'])
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
        resultado = criar_transacao(
            data_transacao=dados['data'],
            descricao=dados['descricao'],
            categoria=dados['categoria'],
            tipo=dados['tipo'],
            valor=valor,
            conta=dados.get('conta', ''),
            instituicao=dados.get('instituicao', ''),
            status=dados['status']
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 201
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao criar transação', 'detalhes': str(e)}), 500

# Rota de API - edita uma transação existente
@app.route('/api/transacoes/<int:id>', methods=['PUT'])
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
        resultado = editar_transacao(
            id_transacao=id,
            data_transacao=dados['data'],
            descricao=dados['descricao'],
            categoria=dados['categoria'],
            tipo=dados['tipo'],
            valor=valor,
            conta=dados.get('conta', ''),
            instituicao=dados.get('instituicao', ''),
            status=dados['status']
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao editar transação', 'detalhes': str(e)}), 500

# Rota de API - exclui uma transação
@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def api_excluir_transacao(id):
    try:
        # Exclui transação
        resultado = excluir_transacao(id)
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao excluir transação', 'detalhes': str(e)}), 500
        
@app.route("/api/upload", methods=["POST"])
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
        resultado_carga = carregar_transacoes_mysql(df_tratado)

        return {
            "mensagem": "Planilha processada com sucesso.",
            "recebidos": resultado_carga["recebidos"],
            "importados": resultado_carga["importados"],
            "ignorados": resultado_carga["ignorados"],
            "categorizadas_automaticamente": contador_categorizadas
        }

    except Exception as erro:
        return jsonify({
            "erro": "Não foi possível importar a planilha.",
            "detalhe": str(erro)
        }), 500


@app.route("/api/transacoes/limpar", methods=["DELETE"])
def api_limpar_transacoes():
    try:
        limpar_transacoes_mysql()

        return jsonify({
            "mensagem": "Todos os dados foram removidos com sucesso."
        })

    except Exception as erro:
        return jsonify({
            "erro": "Não foi possível limpar os dados.",
            "detalhe": str(erro)
        }), 500

# Rota de API - retorna a meta ativa
@app.route('/api/meta')
def api_meta():
    try:
        meta = buscar_meta_ativa()
        
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
        return jsonify({'erro': 'Falha ao buscar meta', 'detalhes': str(e)}), 500

# Rota de API - cria uma nova meta
@app.route('/api/meta', methods=['POST'])
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
        id_meta = criar_meta(
            titulo=dados['titulo'],
            valor_meta=valor_meta,
            valor_atual=valor_atual,
            data_limite=dados.get('data_limite'),
            status=status
        )
        
        return jsonify({'mensagem': 'Meta criada com sucesso', 'id': id_meta}), 201
        
    except Exception as e:
        return jsonify({'erro': 'Falha ao criar meta', 'detalhes': str(e)}), 500

# Rota de API - atualiza uma meta existente
@app.route('/api/meta/<int:id>', methods=['PUT'])
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
        sucesso = atualizar_meta(
            id_meta=id,
            titulo=dados.get('titulo'),
            valor_meta=dados.get('valor_meta'),
            valor_atual=dados.get('valor_atual'),
            data_limite=dados.get('data_limite'),
            status=dados.get('status')
        )
        
        if sucesso:
            return jsonify({'mensagem': 'Meta atualizada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Meta não encontrada'}), 404
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao atualizar meta', 'detalhes': str(e)}), 500

# Rota de API - exclui uma meta
@app.route('/api/meta/<int:id>', methods=['DELETE'])
def api_excluir_meta(id):
    try:
        sucesso = excluir_meta(id)
        
        if sucesso:
            return jsonify({'mensagem': 'Meta excluída com sucesso'}), 200
        else:
            return jsonify({'erro': 'Meta não encontrada'}), 404
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao excluir meta', 'detalhes': str(e)}), 500

# Rota de API - retorna todas as categorias
@app.route('/api/categorias')
def api_categorias():
    try:
        # Inicializa categorias padrão se necessário
        inicializar_categorias_padrao()
        
        categorias = buscar_todas_categorias()
        
        # Adiciona estatísticas para cada categoria
        for categoria in categorias:
            estatisticas = obter_estatisticas_categoria(categoria['nome'])
            categoria['quantidade_transacoes'] = estatisticas['quantidade']
            categoria['valor_total'] = estatisticas['valor_total']
        
        return jsonify(categorias)
        
    except Exception as e:
        return jsonify({'erro': 'Falha ao buscar categorias', 'detalhes': str(e)}), 500

# Rota de API - cria uma nova categoria
@app.route('/api/categorias', methods=['POST'])
def api_criar_categoria():
    try:
        dados = request.get_json()
        
        # Valida campos obrigatórios
        if not dados.get('nome'):
            return jsonify({'erro': 'Nome da categoria é obrigatório'}), 400
        
        # Cria categoria
        resultado = criar_categoria(
            nome=dados['nome'],
            palavras_chave=dados.get('palavras_chave', []),
            cor=dados.get('cor')
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 201
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao criar categoria', 'detalhes': str(e)}), 500

# Rota de API - atualiza uma categoria
@app.route('/api/categorias/<nome>', methods=['PUT'])
def api_atualizar_categoria(nome):
    try:
        dados = request.get_json()
        
        # Atualiza categoria
        resultado = atualizar_categoria(
            nome_atual=nome,
            novo_nome=dados.get('nome'),
            palavras_chave=dados.get('palavras_chave'),
            cor=dados.get('cor')
        )
        
        if resultado['sucesso']:
            return jsonify({'mensagem': resultado['mensagem']}), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao atualizar categoria', 'detalhes': str(e)}), 500

# Rota de API - exclui uma categoria
@app.route('/api/categorias/<int:id>', methods=['DELETE'])
def api_excluir_categoria(id):
    try:
        resultado = excluir_categoria(id)
        
        if resultado['sucesso']:
            return jsonify({
                'mensagem': resultado['mensagem'],
                'quantidade_transacoes_atualizadas': resultado.get('quantidade_transacoes_atualizadas', 0)
            }), 200
        elif 'não encontrada' in resultado['erro']:
            return jsonify({'erro': resultado['erro']}), 404
        else:
            return jsonify({'erro': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'erro': 'Falha ao excluir categoria', 'detalhes': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)

