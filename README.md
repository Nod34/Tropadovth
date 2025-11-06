
# 🎉 Bot de Sorteio Discord - Python

Bot completo para gerenciamento de sorteios no Discord com sistema de fichas personalizável.

## ✨ Funcionalidades

- 📝 **Modal de inscrição** interativo
- 🎫 **Sistema de fichas** totalmente configurável
- 👥 **Validação de nomes** reais
- 🔖 **Sistema de hashtag** com verificação
- 🏆 **Cargos com fichas extras** e siglas personalizadas
- 🏷️ **TAG do servidor** com fichas extras
- 📊 **Estatísticas completas**
- 🚫 **Blacklist** com motivo
- 📤 **Exportação** de listas
- 🔒 **Bloqueio de chat** para não-admins
- 📢 **Sistema de anúncios** com embeds

## 🚀 Deploy no Render

### 1. Preparar Repositório

1. Crie um repositório no GitHub
2. Faça upload dos arquivos:
   - `bot.py`
   - `database.py`
   - `utils.py`
   - `requirements.txt`
   - `.gitignore`

### 2. Criar Web Service no Render

1. Acesse [https://render.com](https://render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python bot.py
```

### 3. Configurar Variáveis de Ambiente

No painel do Render, vá em **Environment** e adicione:

- **BOT_TOKEN**: Seu token do Discord bot
- **PORT**: 5000 (opcional, já está configurado)

### 4. Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o deploy finalizar (5-10 minutos)
3. Seu bot estará online 24/7! 🎉

### 5. Manter o Bot Online (Opcional)

O Render pode desligar serviços gratuitos após inatividade. Para manter online:

1. Use **[UptimeRobot](https://uptimerobot.com)** (grátis)
2. Adicione um monitor HTTP com a URL do seu Render
3. Configure para pingar a cada 5 minutos

**URL do seu bot:** `https://seu-app.onrender.com`

## 🔧 Configuração do Bot Discord

### Permissões Necessárias

No [Discord Developer Portal](https://discord.com/developers/applications):

1. Vá em **"Bot"**
2. Ative os **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
3. Em **"OAuth2" → "URL Generator"**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Administrator` (ou ajuste conforme necessário)

## 📋 Comandos

### 👥 Comandos Públicos

- `/inscrever` - Inscrever-se no sorteio
- `/verificar` - Ver status de inscrição
- `/ajuda` - Listar comandos

### 🛡️ Comandos Admin

- `/hashtag` - Definir hashtag oficial
- `/tag` - Configurar verificação de TAG
- `/fichas` - Adicionar fichas extras para cargos
- `/tirar` - Remover fichas de cargos
- `/lista` - Listar participantes
- `/exportar` - Exportar listas
- `/atualizar` - Recalcular fichas
- `/estatisticas` - Ver estatísticas
- `/blacklist` - Gerenciar banimentos
- `/chat` - Bloquear/desbloquear canal
- `/anunciar` - Enviar anúncios
- `/limpar` - Limpar inscrições

## 📦 Estrutura do Projeto

```
├── bot.py              # Código principal do bot
├── database.py         # Sistema de database JSON
├── utils.py            # Funções utilitárias
├── requirements.txt    # Dependências
├── .gitignore         # Arquivos ignorados pelo Git
└── database.json      # Dados (criado automaticamente)
```

## 🔒 Segurança

- **NUNCA** commite o arquivo `.env` ou `database.json`
- Use variáveis de ambiente para tokens
- O `.gitignore` já está configurado

## 📝 Formato das Listas

### Lista Simples
```
Rafael Felipe
Matheus Carlos
```

### Lista Detalhada (com fichas)
```
Rafael Fe.
Rafael Fe. S.B
Rafael Fe. M.C
Matheus Ca.
Matheus Ca. M.C
```

As siglas são geradas automaticamente dos cargos.

## 🛠️ Tecnologias

- **Python 3.11+**
- **discord.py 2.3.2**
- **Flask 3.0.0** (servidor HTTP)
- **JSON** (database)

## ❓ Problemas Comuns

### Bot não fica online
- Verifique se `BOT_TOKEN` está configurado corretamente
- Confira os logs no Render
- Certifique-se que os Intents estão ativados

### Comandos não aparecem
- Aguarde até 1 hora para sincronizar
- Use `/` no Discord para ver comandos
- Verifique se o bot tem permissões de admin

### Render desliga o bot
- Use UptimeRobot para pingar o bot
- Considere upgrade para plano pago do Render

## 📞 Suporte

- Discord: [Seu servidor]
- Issues: [GitHub Issues]

---

**Desenvolvido com ❤️ para comunidades Discord**
