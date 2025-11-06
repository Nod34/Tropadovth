import discord
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Optional
from database import db
from utils import calculate_tickets

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Modal de inscrição
class InscricaoModal(Modal, title='Inscrição no Sorteio'):
    nome = TextInput(
        label='Primeiro Nome',
        placeholder='Digite seu primeiro nome',
        required=True,
        max_length=50,
        min_length=3
    )
    sobrenome = TextInput(
        label='Sobrenome',
        placeholder='Digite seu sobrenome',
        required=True,
        max_length=50,
        min_length=3
    )
    hashtag = TextInput(
        label='Hashtag do Sorteio',
        placeholder='Ex: #Sorteio2025',
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = str(interaction.user.id)
            nome = self.nome.value.strip()
            sobrenome = self.sobrenome.value.strip()
            hashtag = self.hashtag.value.strip()

            # Validações básicas
            if db.is_blacklisted(user_id):
                await interaction.response.send_message(
                    '🚫 Você está banido e não pode participar.',
                    ephemeral=True
                )
                return

            if db.is_registered(user_id):
                await interaction.response.send_message(
                    '⚠️ Você já está inscrito no sorteio.',
                    ephemeral=True
                )
                return
            
            # Validação da hashtag
            if not db.data['config']['hashtag']:
                await interaction.response.send_message(
                    '⚠️ Hashtag não configurada.',
                    ephemeral=True
                )
                return

            if hashtag.lower() != db.data['config']['hashtag'].lower():
                await interaction.response.send_message(
                    f'❌ Hashtag incorreta!\nCorreta: {db.data["config"]["hashtag"]}',
                    ephemeral=True
                )
                return

            # Processa a inscrição
            await interaction.response.defer(ephemeral=True)
            
            channel_id = db.get_inscricao_channel()
            if not channel_id:
                await interaction.followup.send('❌ Canal de inscrições não configurado.', ephemeral=True)
                return

            channel = interaction.guild.get_channel(int(channel_id))
            msg = await channel.send(
                f"{interaction.user.mention}\n{nome} {sobrenome}\n{hashtag}"
            )
            
            # Calcula fichas
            member = interaction.guild.get_member(int(user_id))
            tickets = calculate_tickets(
                member,
                db.data['config'].get('bonus_roles', {}),
                db.data['config'].get('tag_enabled', False),
                db.data['config'].get('server_tag', ''),
                db.data['config']['tag_quantity']
            )

            # Registra participante
            db.add_participant(
                user_id,
                nome,
                sobrenome,
                f"{nome} {sobrenome}",
                str(msg.id),
                tickets,
                datetime.now().isoformat()
            )

            await interaction.followup.send('✅ Inscrição realizada com sucesso!', ephemeral=True)

        except Exception as e:
            logging.error(f'Erro na inscrição: {e}')
            await interaction.followup.send('❌ Erro ao processar inscrição.', ephemeral=True)

# Classe do botão de inscrição
class InscreverButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Inscrever-se no Sorteio",
            style=discord.ButtonStyle.primary,
            custom_id="inscrever_button"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InscricaoModal())

# Remover o comando /inscrever e adicionar /setup_inscricao
@tree.command(
    name='setup_inscricao',
    description='[ADMIN] Configurar botão de inscrição e canal de inscritos'
)
@app_commands.describe(
    canal_botao='Canal onde o botão será criado',
    canal_inscricoes='Canal onde as inscrições aparecerão',
    mensagem='Mensagem personalizada (opcional)',
    midia='Foto ou vídeo para anexar (opcional)'
)
@app_commands.default_permissions(administrator=True)
async def setup_inscricao(
    interaction: discord.Interaction,
    canal_botao: discord.TextChannel,
    canal_inscricoes: discord.TextChannel,
    mensagem: Optional[str] = None,
    midia: Optional[discord.Attachment] = None
):
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Configura canal de inscrições
        db.data['config']['inscricao_channel'] = str(canal_inscricoes.id)
        db.save()

        # Cria view com botão
        view = discord.ui.View(timeout=None)
        view.add_item(InscreverButton())

        # Prepara mensagem
        content = mensagem or "🎉 **SORTEIO ABERTO!**\nClique no botão abaixo para participar."

        # Envia mensagem com mídia se fornecida
        if midia:
            file = await midia.to_file()
            message = await canal_botao.send(content, file=file, view=view)
        else:
            message = await canal_botao.send(content, view=view)

        # Registra view para persistência
        try:
            client.add_view(view)
        except Exception as e:
            logging.error(f'Erro ao registrar view: {e}')

        await interaction.followup.send(
            f"✅ Configuração concluída!\n\n"
            f"• Botão criado em: {canal_botao.mention}\n"
            f"• Inscrições aparecem em: {canal_inscricoes.mention}",
            ephemeral=True
        )

    except Exception as e:
        logging.error(f'Erro no setup_inscricao: {e}', exc_info=True)
        await interaction.followup.send(
            "❌ Erro ao configurar inscrição. Verifique os logs.",
            ephemeral=True
        )

@client.event
async def on_ready():
    try:
        await tree.sync()
        logging.info(f'Bot {client.user.name} online!')
    except Exception as e:
        logging.error(f'Erro ao sincronizar comandos: {e}')

# Comando de sincronização forçada
@tree.command(name='sync', description='[ADMIN] Forçar sincronização de comandos')
@app_commands.default_permissions(administrator=True)
async def sync_commands(interaction: discord.Interaction, guild_id: Optional[str] = None):
    try:
        if guild_id:
            guild_obj = discord.Object(id=int(guild_id))
            synced = await tree.sync(guild=guild_obj)
            await interaction.response.send_message(f'✅ Sincronizado {len(synced)} comandos no guild {guild_id}', ephemeral=True)
        else:
            synced = await tree.sync()
            await interaction.response.send_message(f'✅ Sincronizado {len(synced)} comandos globais', ephemeral=True)
    except Exception as e:
        logging.error(f'Erro ao sincronizar comandos: {e}')
        await interaction.response.send_message(f'❌ Erro: {e}', ephemeral=True)

# Comandos Administrativos
@tree.command(name='hashtag', description='[ADMIN] Definir a hashtag oficial do sorteio')
@app_commands.default_permissions(administrator=True)
async def hashtag(interaction: discord.Interaction, hashtag: str):
    try:
        db.set_hashtag(hashtag)
        await interaction.response.send_message(f'✅ Hashtag definida: {hashtag}', ephemeral=True)
    except Exception as e:
        logging.error(f'Erro ao definir hashtag: {e}')
        await interaction.response.send_message('❌ Erro ao definir hashtag.', ephemeral=True)

@tree.command(name='tag', description='[ADMIN] Configurar verificação de tag do servidor')
@app_commands.default_permissions(administrator=True)
async def tag(interaction: discord.Interaction, tag: str, quantidade: int = 1):
    try:
        db.set_tag_enabled(True, tag, quantidade)
        await interaction.response.send_message(
            f'✅ Tag configurada:\nTag: {tag}\nFichas: {quantidade}', 
            ephemeral=True
        )
    except Exception as e:
        logging.error(f'Erro ao configurar tag: {e}')
        await interaction.response.send_message('❌ Erro ao configurar tag.', ephemeral=True)

@tree.command(name='fichas', description='[ADMIN] Adicionar fichas extras para cargos')
@app_commands.default_permissions(administrator=True)
async def fichas(interaction: discord.Interaction, cargo: discord.Role, quantidade: int, abreviacao: str):
    try:
        db.add_bonus_role(str(cargo.id), cargo.name, quantidade, abreviacao)
        await interaction.response.send_message(
            f'✅ Bônus configurado:\nCargo: {cargo.mention}\nFichas: {quantidade}\nAbreviação: {abreviacao}',
            ephemeral=True
        )
    except Exception as e:
        logging.error(f'Erro ao adicionar fichas: {e}')
        await interaction.response.send_message('❌ Erro ao adicionar fichas.', ephemeral=True)

@tree.command(name='tirar', description='[ADMIN] Remover fichas extras de cargos')
@app_commands.default_permissions(administrator=True)
async def tirar(interaction: discord.Interaction, cargo: discord.Role):
    try:
        db.remove_bonus_role(str(cargo.id))
        await interaction.response.send_message(
            f'✅ Bônus removido do cargo {cargo.mention}',
            ephemeral=True
        )
    except Exception as e:
        logging.error(f'Erro ao remover fichas: {e}')
        await interaction.response.send_message('❌ Erro ao remover fichas.', ephemeral=True)

@tree.command(name='atualizar', description='[ADMIN] Atualizar fichas dos participantes')
@app_commands.default_permissions(administrator=True)
async def atualizar(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        count = 0
        for user_id, participant in db.get_all_participants().items():
            member = interaction.guild.get_member(int(user_id))
            if member:
                new_tickets = calculate_tickets(
                    member,
                    db.data['config'].get('bonus_roles', {}),
                    db.data['config'].get('tag_enabled', False),
                    db.data['config'].get('server_tag', ''),
                    db.data['config'].get('tag_quantity', 0)
                )
                db.update_tickets(user_id, new_tickets)
                count += 1
        
        await interaction.followup.send(f'✅ Atualizadas fichas de {count} participantes.', ephemeral=True)
    except Exception as e:
        logging.error(f'Erro ao atualizar fichas: {e}')
        await interaction.followup.send('❌ Erro ao atualizar fichas.', ephemeral=True)

@tree.command(name='estatisticas', description='Ver estatísticas do sorteio')
async def estatisticas(interaction: discord.Interaction):
    try:
        stats = db.get_statistics()
        text = (
            f'📊 **Estatísticas do Sorteio**\n'
            f'• Total de participantes: {stats["total_participants"]}\n'
            f'• Total de fichas: {stats["total_tickets"]}\n\n'
            f'**Fichas por cargo:**\n'
        )
        
        for role_name, count in stats['tickets_by_role'].items():
            text += f'• {role_name}: {count}\n'
            
        if stats['tickets_by_tag'] > 0:
            text += f'\n**Com tag do servidor:** {stats["tickets_by_tag"]}'
            
        await interaction.response.send_message(text, ephemeral=True)
    except Exception as e:
        logging.error(f'Erro ao mostrar estatísticas: {e}')
        await interaction.response.send_message('❌ Erro ao carregar estatísticas.', ephemeral=True)

@tree.command(name='blacklist', description='[ADMIN] Gerenciar lista de bloqueios')
@app_commands.default_permissions(administrator=True)
async def blacklist(
    interaction: discord.Interaction, 
    acao: str,
    usuario: discord.Member,
    motivo: str = "Sem motivo especificado"
):
    try:
        if acao.lower() == "add":
            db.add_to_blacklist(str(usuario.id), usuario.name, motivo)
            await interaction.response.send_message(
                f'✅ {usuario.mention} foi banido do sorteio.\nMotivo: {motivo}',
                ephemeral=True
            )
        elif acao.lower() == "remove":
            db.remove_from_blacklist(str(usuario.id))
            await interaction.response.send_message(
                f'✅ {usuario.mention} foi desbanido do sorteio.',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                '❌ Ação inválida. Use "add" ou "remove".',
                ephemeral=True
            )
    except Exception as e:
        logging.error(f'Erro no blacklist: {e}')
        await interaction.response.send_message('❌ Erro ao gerenciar blacklist.', ephemeral=True)

@tree.command(name='chat', description='[ADMIN] Controlar quem pode escrever no canal (mensagem de inscrição via botão)')
@app_commands.default_permissions(administrator=True)
async def chat(interaction: discord.Interaction, canal: discord.TextChannel, estado: bool):
    try:
        db.set_chat_lock(estado, str(canal.id))
        await interaction.response.send_message(
            f'✅ Chat {canal.mention} {"bloqueado" if estado else "desbloqueado"} (inscrições via botão).',
            ephemeral=True
        )
    except Exception as e:
        logging.error(f'Erro em /chat: {e}', exc_info=True)
        await interaction.response.send_message('❌ Erro ao controlar chat.', ephemeral=True)

# Público: verificar inscrição
@tree.command(name='verificar', description='Verificar seu status de inscrição')
async def verificar(interaction: discord.Interaction):
    try:
        user_id = str(interaction.user.id)
        if not db.is_registered(user_id):
            await interaction.response.send_message('❌ Você não está inscrito no sorteio.', ephemeral=True)
            return
        p = db.get_participant(user_id)
        await interaction.response.send_message(
            f'✅ Inscrição encontrada:\nNome: {p.get("full_name")}\nFichas: {p.get("tickets")}',
            ephemeral=True
        )
    except Exception as e:
        logging.error(f'Erro em /verificar: {e}', exc_info=True)
        await interaction.response.send_message('❌ Erro ao verificar inscrição.', ephemeral=True)

# /ajuda - mostra lista de comandos
@tree.command(name='ajuda', description='Mostrar comandos disponíveis')
async def ajuda(interaction: discord.Interaction):
    text = (
        "**Comandos Públicos:**\n"
        "/verificar - Verificar seu status de inscrição\n\n"
        "**Comandos Administrativos:**\n"
        "/ajuda - Mostrar esta mensagem\n"
        "/setup_inscricao - Configurar botão e gerar lista\n"
        "/hashtag - Definir a hashtag oficial do sorteio\n"
        "/tag - Configurar verificação de tag do servidor\n"
        "/fichas - Adicionar fichas extras para cargos\n"
        "/tirar - Remover fichas extras de cargos\n"
        "/lista - Listar todos os participantes\n"
        "/exportar - Exportar lista de participantes\n"
        "/atualizar - Atualizar fichas dos participantes\n"
        "/estatisticas - Ver estatísticas do sorteio\n"
        "/limpar - Limpar inscrições e mensagens\n"
        "/blacklist - Gerenciar lista de bloqueios\n"
        "/chat - Controlar quem pode escrever no canal\n"
        "/anunciar - Enviar anúncio (mensagem/foto/video/embed/titulo)\n"
    )
    await interaction.response.send_message(text, ephemeral=True)

# /lista - listar participantes (admin)
@tree.command(name='lista', description='[ADMIN] Listar todos os participantes')
@app_commands.describe(tipo='Tipo de lista')
@app_commands.choices(tipo=[
    app_commands.Choice(name='Sem fichas', value='simples'),
    app_commands.Choice(name='Com fichas', value='detalhada')
])
@app_commands.default_permissions(administrator=True)
async def lista(interaction: discord.Interaction, tipo: str = 'simples'):
    participants = db.get_all_participants()
    
    if not participants:
        await interaction.response.send_message('Nenhum participante inscrito ainda.', ephemeral=True)
        return
    
    participants = sorted(participants.values(), key=lambda p: p['full_name'])
    
    response = ''
    
    if tipo == 'detalhada':
        for p in participants:
            # Nome base com primeira ficha (participação)
            first_name = p['first_name']
            last_name_abbrev = p['last_name'][:2] + '.'
            base_name = f"{first_name} {last_name_abbrev}"
            response += f"{base_name}\n"
            
            # Fichas por cargos (usando abreviações)
            for role_name, role_data in p['tickets'].get('roles', {}).items():
                for _ in range(role_data['quantity']):
                    response += f"{base_name} {role_data['abbreviation']}\n"
            
            # Fichas por tag (usando 'TAG')
            if p['tickets'].get('tag'):
                for _ in range(p['tickets']['tag']):
                    response += f"{base_name} TAG\n"
            
            response += "\n"  # Linha extra entre participantes
    else:
        # Lista simples só com nomes completos
        for p in participants:
            response += f"{p['full_name']}\n"
    
    if len(response) > 2000:
        chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
        await interaction.response.send_message(chunks[0], ephemeral=True)
        for chunk in chunks[1:]:
            await interaction.followup.send(chunk, ephemeral=True)
    else:
        await interaction.response.send_message(response or 'Lista vazia', ephemeral=True)

# /exportar - exporta CSV com participantes (admin)
@tree.command(name='exportar', description='[ADMIN] Exportar lista de participantes (CSV)')
@app_commands.default_permissions(administrator=True)
async def exportar(interaction: discord.Interaction):
    try:
        parts = db.get_all_participants()
        if not parts:
            await interaction.response.send_message('Nenhum participante para exportar.', ephemeral=True)
            return
        bio = io.StringIO()
        writer = csv.writer(bio)
        writer.writerow(['user_id', 'first_name', 'last_name', 'full_name', 'tickets', 'registered_at'])
        for p in parts.values():
            writer.writerow([p.get('user_id'), p.get('first_name'), p.get('last_name'), p.get('full_name'), p.get('tickets'), p.get('registered_at')])
        bio.seek(0)
        await interaction.response.send_message(file=File(fp=bio, filename='participantes.csv'), ephemeral=True)
    except Exception as e:
        logging.error(f'Erro em /exportar: {e}', exc_info=True)
        await interaction.response.send_message('❌ Erro ao exportar participantes.', ephemeral=True)

# /limpar - limpa DB e opcionalmente mensagens do canal de inscrições
@tree.command(name='limpar', description='[ADMIN] Limpar inscrições e mensagens')
@app_commands.default_permissions(administrator=True)
async def limpar(interaction: discord.Interaction, canal_limpar: Optional[discord.TextChannel] = None):
    try:
        await interaction.response.defer(ephemeral=True)
        db.clear_participants()
        deleted = 0
        if canal_limpar:
            # deleta mensagens do bot no canal (limite 500)
            deleted = await canal_limpar.purge(limit=500, check=lambda m: m.author == client.user)
        await interaction.followup.send(f'✅ Inscrições limpas. Mensagens deletadas: {deleted}', ephemeral=True)
    except Exception as e:
        logging.error(f'Erro em /limpar: {e}', exc_info=True)
        await interaction.followup.send('❌ Erro ao limpar inscrições.', ephemeral=True)

# /exportar e /atualizar já implementados anteriormente; aqui está /atualizar concretizado
@tree.command(name='atualizar', description='[ADMIN] Atualizar fichas dos participantes')
@app_commands.default_permissions(administrator=True)
async def atualizar(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        count = 0
        for user_id, participant in db.get_all_participants().items():
            member = interaction.guild.get_member(int(user_id))
            if member:
                new_tickets = calculate_tickets(
                    member,
                    db.data['config'].get('bonus_roles', {}),
                    db.data['config'].get('tag_enabled', False),
                    db.data['config'].get('server_tag', ''),
                    db.data['config'].get('tag_quantity', 0)
                )
                db.update_tickets(user_id, new_tickets)
                count += 1
        await interaction.followup.send(f'✅ Atualizadas fichas de {count} participantes.', ephemeral=True)
    except Exception as e:
        logging.error(f'Erro em /atualizar: {e}', exc_info=True)
        await interaction.followup.send('❌ Erro ao atualizar fichas.', ephemeral=True)

# /anunciar - enviar anúncio com texto, título, embed e/ou mídia (admin)
@tree.command(name='anunciar', description='[ADMIN] Enviar anúncio (mensagem/foto/video/embed/titulo)')
@app_commands.default_permissions(administrator=True)
async def anunciar(
    interaction: discord.Interaction,
    canal: discord.TextChannel,
    titulo: Optional[str] = None,
    mensagem: Optional[str] = None,
    anexar: Optional[discord.Attachment] = None,
    usar_embed: Optional[bool] = False
):
    try:
        await interaction.response.defer(ephemeral=True)
        if usar_embed:
            embed = discord.Embed(title=titulo or discord.Embed.Empty, description=mensagem or discord.Embed.Empty)
            if anexar:
                file = await anexar.to_file()
                await canal.send(embed=embed, file=file)
            else:
                await canal.send(embed=embed)
        else:
            if anexar:
                file = await anexar.to_file()
                content = (f"**{titulo}**\n\n{mensagem}") if titulo or mensagem else None
                await canal.send(content or None, file=file)
            else:
                content = (f"**{titulo}**\n\n{mensagem}") if titulo or mensagem else ""
                await canal.send(content)
        await interaction.followup.send('✅ Anúncio enviado.', ephemeral=True)
    except Exception as e:
        logging.error(f'Erro em /anunciar: {e}', exc_info=True)
        await interaction.followup.send('❌ Erro ao enviar anúncio.', ephemeral=True)

# Inicia um HTTP server mínimo para atender healthchecks em Render (opcional,
# apenas se você NÃO puder usar Background Worker)
import asyncio
import os
from aiohttp import web

async def _health(request):
    return web.Response(text="ok")

async def _start_web():
    app = web.Application()
    app.router.add_get("/", _health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"HTTP server running on port {port}")

# Inicializa web server em background e roda o bot
async def _main():
    # start web server
    asyncio.create_task(_start_web())
    # run discord client (blocking)
    client_task = asyncio.get_event_loop().run_in_executor(None, client.run, os.getenv("BOT_TOKEN"))
    await client_task

if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
