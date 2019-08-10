import discord
import yt
import html
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['discord']['token']
PUCK_SNOWFLAKE = '532623452784558110'
EMBED_COLOR = 0xa700d6

client = discord.Client()

def make_embed(query, message, page_num=1):
    video_results = yt.youtube_search(query, page_num)
    puck = message.server.get_member(PUCK_SNOWFLAKE)

    if video_results:
        em = discord.Embed(
            description='Want more results? Respond !more\n Please report any issues or feature suggestions to <@!%s>\n' % PUCK_SNOWFLAKE,
            colour=EMBED_COLOR,
        )
        em.set_thumbnail(url=video_results[0]["snippet"]["thumbnails"]["default"]["url"])
        em.set_footer(text="Thank you for using Botwell", icon_url=puck.avatar_url)

        for index, result in enumerate(video_results):
            em.add_field(
                name='Result %d' % (int(index) + 1),
                value='[%s](https://youtube.com/watch?v=%s)' % (html.unescape(result["snippet"]["title"]), result["id"]["videoId"])
            )
    else:
        em = discord.Embed(
            title='No Results',
            description='Try something a little less specific.',
            colour=EMBED_COLOR,
        )

    return em

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!botwell'):
        query = message.content.replace('!botwell', '')
        await client.send_message(message.channel, embed=make_embed(query=query, message=message))

    if message.content.startswith('!more'):
        counter = 0
        async for message in client.logs_from(message.channel, limit=100):
            if message.author != client.user:
                if message.content.startswith('!botwell'):
                    previous_message = message.content
                    break
                if message.content.startswith('!more'):
                    counter += 1

        query = previous_message.replace('!botwell', '')
        await client.send_message(message.channel, embed=make_embed(query=query, message=message, page_num=(counter + 1)))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)