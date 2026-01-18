import discord
from discord.ext import commands
import os

# ================= CONFIGURAÇÕES =================
TOKEN = os.getenv("DISCORD_TOKEN")  # Token vem do Render
ADM_ROLE_NAME = "Admin"             # Nome do cargo de admin
CATEGORY_NAME = "Partidas"          # Categoria onde os canais serão criados
# =================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

fila = []

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

@bot.command()
async def entrar(ctx):
    user = ctx.author

    if user in fila:
        await ctx.send("❌ Você já está na fila.")
        return

    fila.append(user)
    await ctx.send(f"✅ {user.mention} entrou na fila. Posição: {len(fila)}")

    # Quando tiver 2 players, cria o canal
    if len(fila) >= 2:
        p1 = fila.pop(0)
        p2 = fila.pop(0)
        await criar_canal(ctx.guild, p1, p2)

async def criar_canal(guild, p1, p2):
    # Categoria
    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
    if category is None:
        category = await guild.create_category(CATEGORY_NAME)

    # Cargo admin
    admin_role = discord.utils.get(guild.roles, name=ADM_ROLE_NAME)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        p1: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        p2: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    if admin_role:
        overwrites[admin_role] = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True
        )

    channel = await guild.create_text_channel(
        name=f"partida-{p1.name}-{p2.name}",
        category=category,
        overwrites=overwrites
    )

    await channel.send(
        f"🎮 **Partida criada!**\n"
        f"{p1.mention} vs {p2.mention}\n"
        f"👮 ADM autorizado no canal."
    )

@bot.command(name="fila")
async def mostrar_fila(ctx):
    if not fila:
        await ctx.send("📭 Fila vazia.")
        return

    texto = "📋 **Fila atual:**\n"
    for i, user in enumerate(fila, start=1):
        texto += f"{i}. {user.mention}\n"

    await ctx.send(texto)

@bot.command()
@commands.has_permissions(administrator=True)
async def limpar(ctx):
    fila.clear()
    await ctx.send("🧹 Fila limpa.")

bot.run(TOKEN)
