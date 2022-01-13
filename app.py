import discord
import yt
import vtx as libvtx
import html
import configparser
import logging
from discord.ext import commands


config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger(__name__)
handler = logging.FileHandler('botwell.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

TOKEN = config['discord']['token']
PUCK_SNOWFLAKE = 532623452784558110
SZ_SNOWFLAKE = 121932280074600448
EMBED_COLOR = 0xa700d6

bot = commands.Bot(command_prefix='!')


def make_yt_embed(query, message, page_num=1, result_num=None):
    try:
        video_results = yt.youtube_search(query, page_num, result_num)
    except Exception as e:
        video_results = None
        logger.error(
            'error getting video results: %s',
            e
        )

    puck = message.guild.get_member(PUCK_SNOWFLAKE)

    logger.info(
        'make_yt_embed: %s',
        query
    )

    try:
        if video_results:
            if result_num:
                description_string = None
            else:
                description_string = """Want more results? Respond `!more`
                To show a specific result, respond `!result 2`
                Please report any issues or feature suggestions to <@!%s>\n""" % PUCK_SNOWFLAKE

            em = discord.Embed(
                description=description_string,
                colour=EMBED_COLOR,
            )
            em.set_thumbnail(url=video_results[0]["snippet"]["thumbnails"]["default"]["url"])
            #em.set_footer(text="Thank you for using Botwell", icon_url=puck.avatar_url)
            em.set_footer(text="Thank you for using Botwell")

            for index, result in enumerate(video_results):
                if result_num:
                    result_name = 'Result %d' % result_num
                else:
                    result_name = 'Result %d' % (int(index) + 1)

                em.add_field(
                    name=result_name,
                    value='[%s](https://youtube.com/watch?v=%s)' % (html.unescape(result["snippet"]["title"]), result["id"]["videoId"])
                )
        else:
            em = discord.Embed(
                title='No Results',
                description='Try something a little less specific.',
                colour=EMBED_COLOR,
            )
    except Exception as e:
        em = None
        logger.error(
            'error making discord embed: %s',
            e
        )

    if result_num:
        return em, 'Result %s https://youtube.com/watch?v=%s' % (result_num, video_results[0]["id"]["videoId"])
    else:
        return em


def make_vtx_embed(ctx, protocol, channels, powers):
    protocol_filtered, channels_filtered, powers_filtered = libvtx.filter_params(protocol, channels, powers)

    if protocol_filtered and channels_filtered and powers_filtered:
        filename = libvtx.generate_vtx_table(protocol_filtered, channels_filtered, powers_filtered, ctx.author)

        fi = discord.File(
            fp=filename,
            filename='vtx_table.json'
        )

        em = discord.Embed(
            title='VTX Table',
            description='from <@!%s> & <@!%s>' % (PUCK_SNOWFLAKE, SZ_SNOWFLAKE),
            colour=EMBED_COLOR,
        )

        em.add_field(
            name='protocol',
            value=protocol_filtered,
            inline=False
        )

        em.add_field(
            name='channels',
            value=', '.join(channels_filtered),
            inline=False
        )

        em.add_field(
            name='power levels',
            value=', '.join(powers_filtered),
            inline=False
        )

        puck = ctx.guild.get_member(PUCK_SNOWFLAKE)
        em.set_footer(text='Thank you for using Botwell\n', icon_url=puck.avatar_url)

        return fi, em

    else:
        return None, make_vtx_help_embed()


def make_vtx_help_embed():
    em = discord.Embed(
        title='Error Creating VTX Table',
        description='Invalid VTX table options provided.',
        colour=EMBED_COLOR,
    )

    em.add_field(
        name='protocol',
        value='[irc|sa2]',
        inline=False
    )

    em.add_field(
        name='channels',
        value='[a (BOSCAM_A) | b (BOSCAM_B) | e (BOSCAM_E) | f (FATSHARK) | r (RACEBAND) | i (IMD6)]',
        inline=False
    )

    em.add_field(
        name='power levels',
        value='[0|25|50|100|200|250|300|400|600|800|1000]',
        inline=False
    )

    em.add_field(
        name='example',
        value='!vtx sa2 f,r 25,100,800',
        inline=False
    )

    return em


@bot.command()
async def botwell(ctx, *args):
    arg_string = ' '.join(args)

    logger.info(
        '!botwell command: %s',
        arg_string
    )

    await ctx.channel.send(embed=make_yt_embed(query=arg_string, message=ctx))


@bot.command()
async def more(ctx, *args):
    arg_string = ' '.join(args)

    logger.info(
        '!more command: %s',
        arg_string
    )

    counter = 0
    async for message in ctx.channel.history(limit=100):
        if message.author != bot.user:
            if message.content.startswith('!botwell'):
                previous_message = message.content
                break
            if message.content.startswith('!more'):
                counter += 1

    query = previous_message.replace('!botwell', '').lstrip()
    await ctx.channel.send(embed=make_yt_embed(query=query, message=ctx, page_num=(counter + 1)))


@bot.command()
async def result(ctx, *args):
    arg_string = ' '.join(args)
    result_num = int(args[0])

    logger.info(
        '!result command: %s',
        arg_string
    )

    async for message in ctx.channel.history(limit=100):
        if message.author != bot.user:
            if message.content.startswith('!botwell'):
                previous_message = message.content
                break

    query = previous_message.replace('!botwell', '').lstrip()
    embed, message = make_yt_embed(query=query, message=ctx, result_num=result_num)
    await ctx.channel.send(content=message)


@bot.command()
async def map(ctx, *args):
    arg_string = ' '.join(args)

    logger.info(
        '!map command: %s',
        arg_string
    )

    em = discord.Embed(
        title='JB Discord Users Map',
        url='https://jbmap.puck.sh/results',
        colour=EMBED_COLOR,
    )

    await ctx.channel.send(embed=em)


@bot.command()
async def vtx(ctx, protocol, channels, powers):
    logger.info(
        '!vtx command: protocol=%s, channels=%s, power=%s',
        protocol, channels, powers
    )

    fi, em = make_vtx_embed(ctx, protocol, channels, powers)

    await ctx.send(file=fi, embed=em)


@vtx.error
async def vtx_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=make_vtx_help_embed())


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)
