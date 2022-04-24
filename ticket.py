import discord
from discord.ext import commands
import json

with open('config.json') as f:
    data = json.load(f)
    token = data["token"]

bot = commands.Bot(command_prefix="!", case_insensitive=True, help_command=None)
client = discord.Client

# discord_slash is the library I use for Button components
from discord_slash import SlashCommand
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (
    ComponentContext,
    create_actionrow,
    create_button,
)

bot = commands.Bot(command_prefix="!", case_insensitive=True, help_command=None)
# yes it says slash, but slash commands are not used and this is required for buttons.
slash = SlashCommand(bot)

# Remember to edit these!
TICKET_MOD_ROLE_ID = 964147640117899334
MANAGEMENT_ROLE_ID = 964147640117899334
GUILD_ID = 964146280290988113

TICKET_CATEGORY_NAME = "Active Tickets"

# Ignore these
ticket_category = None
ticket_mod_role = None
management_role = None
guild = None


@bot.event
async def on_ready():
    global guild, ticket_category, ticket_mod_role, management_role  # one of the annoying things about Python...

    # get the guild
    guild = bot.get_guild(GUILD_ID)

    # replace Active Tickets the exact name of your category (case sensitive)
    ticket_category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)

    ticket_mod_role = guild.get_role(
        role_id=TICKET_MOD_ROLE_ID
    )  # ticket moderator role
    management_role = guild.get_role(role_id=MANAGEMENT_ROLE_ID)  # management role


# called whenever a button is pressed
@bot.event
async def on_component(ctx: ComponentContext):
    await ctx.defer(
        ignore=True
    )  # ignore, i.e. don't do anything *with the button* when it's pressed.

    ticket_created_embed = discord.Embed(
        title="Demande reçue",
        description=f"""Hey {ctx.author.name}! Merci d'avoir choisi nos services pour ton bot discord.""",
    )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True),
        guild.me: discord.PermissionOverwrite(view_channel=True),
        ticket_mod_role: discord.PermissionOverwrite(view_channel=True),
    }

    ticket = await guild.create_text_channel(
        f"{ctx.author.name}-{ctx.author.discriminator}", overwrites=overwrites,
        category=ticket_category
    )

    await ticket.send(
        ctx.author.mention, embed=ticket_created_embed
    )  # ping the user who pressed the button, and send the embed


@bot.command()
async def sendticket(ctx):
    embed = discord.Embed(
        title="Créer votre bot",
        description="Appuyez sur le bouton ci - dessous pour créer le ticket.",
    )

    actionrow = create_actionrow(
        *[
            create_button(
                label="Ouvrir le ticket", custom_id="ticket", style=ButtonStyle.primary
            ),
        ]
    )

    await ctx.send(embed=embed, components=[actionrow])


@bot.command(aliases=["approve"])
@commands.has_role(TICKET_MOD_ROLE_ID)
async def up(ctx):
    overwrites = {
        ctx.guild.me: discord.PermissionOverwrite(view_channel=True),
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ticket_mod_role: discord.PermissionOverwrite(view_channel=None),
        management_role: discord.PermissionOverwrite(view_channel=True),
    }
    await ctx.channel.edit(overwrites=overwrites)

    await ctx.channel.send(
        "Votre ticket a été fermé ! Votre script vous sera envoyé bientôt comme indiqué dans la discussion."
    )


@bot.command()
@commands.has_role(TICKET_MOD_ROLE_ID)
async def close(ctx):
    try:
        if int(ctx.channel.name[-4:]) > 0:
            await ctx.channel.delete()
        else:
            await ctx.send("❌ This does not seem like a ticket channel.")
    except:
        await ctx.send("❌ This does not seem like a ticket channel.")

bot.run(token)