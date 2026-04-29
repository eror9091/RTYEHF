import discord
from discord.ext import commands
import config
import asyncio

ADMIN_ROLE_IDS = [1498779701848707082, 1498780255954145371]
LOG_CHANNEL_ID = 1498792078748946572

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=["/", "!"], intents=intents)

PRIMARY_COLOR = 0x9B59B6
SECONDARY_COLOR = 0x3498DB
SUCCESS_COLOR = 0x2ECC71
ERROR_COLOR = 0xE74C3C

def is_admin(ctx):
    return any(role.id in ADMIN_ROLE_IDS for role in ctx.author.roles)

async def send_log(guild, title, description, color):
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен на сервере 𝒮𝑒𝓇𝓋𝑒𝓇 𝒩𝑒𝓌𝐿𝒾𝓋𝑒𝒮𝓉𝓊𝒹𝒾𝑜")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="за 𝒮𝑒𝓇𝓋𝑒𝓇 𝒩𝑒𝓌𝐿𝒾𝓋𝑒𝒮𝓉𝓊𝒹𝒾𝑜"
        ),
        status=discord.Status.dnd
    )

@bot.command(name="Сервер")
async def server_info(ctx):
    guild = ctx.guild
    members = guild.members
    online = len([m for m in members if m.status != discord.Status.offline])
    offline = len([m for m in members if m.status == discord.Status.offline])
    bots_count = len([m for m in members if m.bot])
    humans = guild.member_count - bots_count
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    roles = len(guild.roles)

    embed = discord.Embed(
        title=f"𝒮𝑒𝓇𝓋𝑒𝓇 𝒩𝑒𝓌𝐿𝒾𝓋𝑒𝒮𝓉𝓊𝒹𝒾𝑜",
        color=PRIMARY_COLOR,
        timestamp=ctx.message.created_at
    )

    embed.add_field(
        name="Основная информация",
        value=f"Название: {guild.name}\n"
              f"ID: {guild.id}\n"
              f"Владелец: {guild.owner}\n"
              f"Создан: {guild.created_at.strftime('%d.%m.%Y')}",
        inline=False
    )

    embed.add_field(
        name="Участники",
        value=f"Всего: {guild.member_count}\n"
              f"Людей: {humans}\n"
              f"Ботов: {bots_count}\n"
              f"Онлайн: {online}\n"
              f"Оффлайн: {offline}",
        inline=True
    )

    embed.add_field(
        name="Сервер",
        value=f"Категорий: {len(guild.categories)}\n"
              f"Текстовых: {text_channels}\n"
              f"Голосовых: {voice_channels}\n"
              f"Ролей: {roles}",
        inline=True
    )

    embed.add_field(
        name="Уровень проверки",
        value=str(guild.verification_level),
        inline=True
    )

    embed.add_field(
        name="Бусты",
        value=f"Бустов: {guild.premium_subscription_count}\n"
              f"Уровень: {guild.premium_tier}",
        inline=True
    )

    if guild.features:
        embed.add_field(
            name="Особенности",
            value="\n".join([f"• {f}" for f in guild.features]),
            inline=False
        )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.set_footer(
        text=f"Запросил: {ctx.author.name} | 𝒮𝑒𝓇𝓋𝑒𝓇 𝒩𝑒𝓌𝐿𝒾𝓋𝑒𝒮𝓉𝓊𝒹𝒾𝑜",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    await ctx.send(embed=embed)

@bot.command(name="Очистить")
@commands.check(is_admin)
async def clear(ctx, amount: int = 10):
    if amount < 1:
        embed = discord.Embed(
            title="Ошибка",
            description="Укажите число больше 0",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    if amount > 100:
        amount = 100

    deleted = await ctx.channel.purge(limit=amount + 1)

    embed = discord.Embed(
        title="Очистка",
        description=f"Удалено {len(deleted) - 1} сообщений",
        color=PRIMARY_COLOR
    )
    await ctx.send(embed=embed, delete_after=3)

    await send_log(
        ctx.guild,
        "Очистка сообщений",
        f"Админ: {ctx.author.mention}\nКанал: {ctx.channel.mention}\nКоличество: {len(deleted) - 1}",
        SECONDARY_COLOR
    )

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Нет доступа",
            description="У вас недостаточно прав для этой команды",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)

@bot.command(name="Мьют")
@commands.check(is_admin)
async def mute(ctx, member: discord.Member, time: int = 10, *, reason: str = "Не указана"):
    if time < 1:
        embed = discord.Embed(
            title="Ошибка",
            description="Время должно быть больше 0",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    await member.timeout(discord.utils.utcnow() + asyncio.timedelta(minutes=time), reason=reason)

    embed = discord.Embed(
        title="Мьют",
        description=f"{member.mention} замьючен на {time} мин.\nПричина: {reason}",
        color=SUCCESS_COLOR
    )
    await ctx.send(embed=embed)

    await send_log(
        ctx.guild,
        "Мьют",
        f"Админ: {ctx.author.mention}\nУчастник: {member.mention}\nВремя: {time} мин.\nПричина: {reason}",
        SUCCESS_COLOR
    )

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Нет доступа",
            description="У вас недостаточно прав для этой команды",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Ошибка",
            description="!Мьют @участник [время в минутах] [причина]",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name="Бан")
@commands.check(is_admin)
async def ban(ctx, member: discord.Member, *, reason: str = "Не указана"):
    await member.ban(reason=reason)

    embed = discord.Embed(
        title="Бан",
        description=f"{member.mention} забанен\nПричина: {reason}",
        color=ERROR_COLOR
    )
    await ctx.send(embed=embed)

    await send_log(
        ctx.guild,
        "Бан",
        f"Админ: {ctx.author.mention}\nУчастник: {member.mention}\nПричина: {reason}",
        ERROR_COLOR
    )

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Нет доступа",
            description="У вас недостаточно прав для этой команды",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Ошибка",
            description="!Бан @участник [причина]",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name="Кик")
@commands.check(is_admin)
async def kick(ctx, member: discord.Member, *, reason: str = "Не указана"):
    await member.kick(reason=reason)

    embed = discord.Embed(
        title="Кик",
        description=f"{member.mention} кикнут\nПричина: {reason}",
        color=ERROR_COLOR
    )
    await ctx.send(embed=embed)

    await send_log(
        ctx.guild,
        "Кик",
        f"Админ: {ctx.author.mention}\nУчастник: {member.mention}\nПричина: {reason}",
        ERROR_COLOR
    )

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Нет доступа",
            description="У вас недостаточно прав для этой команды",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Ошибка",
            description="!Кик @участник [причина]",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name="Тюрьма")
@commands.check(is_admin)
async def jail(ctx, member: discord.Member, time: int = 10, *, reason: str = "Не указана"):
    jail_role = discord.utils.get(ctx.guild.roles, name="Тюрьма")
    if not jail_role:
        jail_role = await ctx.guild.create_role(name="Тюрьма", color=discord.Color.dark_gray())
        for channel in ctx.guild.channels:
            await channel.set_permissions(jail_role, send_messages=False, speak=False)

    await member.add_roles(jail_role, reason=reason)

    embed = discord.Embed(
        title="Тюрьма",
        description=f"{member.mention} посажен в тюрьму на {time} мин.\nПричина: {reason}",
        color=SUCCESS_COLOR
    )
    await ctx.send(embed=embed)

    await send_log(
        ctx.guild,
        "Тюрьма",
        f"Админ: {ctx.author.mention}\nУчастник: {member.mention}\nВремя: {time} мин.\nПричина: {reason}",
        SUCCESS_COLOR
    )

    await asyncio.sleep(time * 60)
    await member.remove_roles(jail_role, reason="Время вышло")

    unjail_embed = discord.Embed(
        title="Освобождение",
        description=f"{member.mention} освобождён из тюрьмы",
        color=SECONDARY_COLOR
    )
    await ctx.send(embed=unjail_embed)

    await send_log(
        ctx.guild,
        "Освобождение из тюрьмы",
        f"Участник: {member.mention}\nАвтоматически после {time} мин.",
        SECONDARY_COLOR
    )

@jail.error
async def jail_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Нет доступа",
            description="У вас недостаточно прав для этой команды",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Ошибка",
            description="!Тюрьма @участник [время в минутах] [причина]",
            color=ERROR_COLOR
        )
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name="Помощь")
async def help_command(ctx):
    embed = discord.Embed(
        title="Команды бота",
        color=SECONDARY_COLOR
    )

    embed.add_field(
        name="/Сервер",
        value="Информация о сервере",
        inline=False
    )
    embed.add_field(
        name="/Помощь",
        value="Список всех команд",
        inline=False
    )

    if is_admin(ctx):
        embed.add_field(
            name="Админ команды",
            value="!Очистить [число] - удалить сообщения\n"
                  "!Мьют @участник [время] [причина] - замьютить\n"
                  "!Бан @участник [причина] - забанить\n"
                  "!Кик @участник [причина] - кикнуть\n"
                  "!Тюрьма @участник [время] [причина] - посадить в тюрьму",
            inline=False
        )

    embed.set_footer(text="𝒮𝑒𝓇𝓋𝑒𝓇 𝒩𝑒𝓌𝐿𝒾𝓋𝑒𝒮𝓉𝓊𝒹𝒾𝑜 • Префиксы: / и !")

    await ctx.send(embed=embed)

bot.run(config.TOKEN)