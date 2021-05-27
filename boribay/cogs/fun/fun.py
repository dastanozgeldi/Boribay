import asyncio
import random
import textwrap
from io import BytesIO
from time import time
from typing import Optional

import discord
from boribay.core import Boribay, Cog, Context
from boribay.utils import Manip, color_exists, make_image_url
from discord.ext import commands, flags


class Fun(Cog):
    """The fun commands extension."""

    def __init__(self, bot: Boribay):
        self.icon = '🎉'
        self.bot = bot

    async def alex_image(self, url: str, fn: str = None) -> discord.File:
        """Quick-Alex-image making function.

        Args:
            url (str): The URL of an image.
            fn (str, optional): Filename to take. Defaults to None.

        Returns:
            discord.File: A done to send file.
        """
        alex = self.bot.config.api.alex
        r = await self.bot.session.get(f'{alex[0]}{url}',
                                       headers={'Authorization': alex[1]})

        fp = BytesIO(await r.read())
        return discord.File(fp, fn or 'alex.png')

    async def dagpi_image(self, url: str, fn: str = None) -> discord.File:
        """Quick-Dagpi-image making function.

        Args:
            url (str): The URL of an image.
            fn (str, optional): Filename to take. Defaults to None.

        Returns:
            discord.File: A done to send file.
        """
        dagpi = self.bot.config.api.dagpi
        r = await self.bot.session.get(f'{dagpi[0]}{url}',
                                       headers={'Authorization': dagpi[1]})

        fp = BytesIO(await r.read())
        return discord.File(fp, fn or 'dagpi.png')

    @commands.command(aliases=['ph'])
    async def pornhub(self, ctx: Context, text_1: str, text_2: str = 'Hub') -> None:
        """PornHub logo maker.

        Example:
            **{p}ph Dosek** - a logo "DosekHub".**
            **{p}ph Bori bay** - Bori and bay in the orange box.**

        Args:
            text_1 (str): Text for the left side
            text_2 (str, optional): Text to the right side. Defaults to 'Hub'.
        """
        text_1 = text_1.replace(' ', '%20')
        text_2 = text_2.replace(' ', '%20')

        file = await self.alex_image(f'pornhub?text={text_1}&text2={text_2}')
        await ctx.send(file=file)

    @commands.command(aliases=['dym'])
    async def didyoumean(self, ctx: Context, search: str, did_you_mean: str) -> None:
        """Google search "Did you mean" meme.

        Example:
            **{p}didyoumean "looping" "recursion"**

        Args:
            search (str): The "searched" query.
            did_you_mean (str): Query not found, the "did you mean" text.
        """
        file = await self.alex_image(f'didyoumean?top={search}&bottom={did_you_mean}')
        await ctx.send(file=file)

    @commands.command()
    async def achieve(self, ctx: Context, *, text: str) -> None:
        """Minecraft "Achievement Get!" meme maker.

        Example:
            **{p}achieve sleep more than 6 hours**

        Args:
            text (str): A text for the achievement.
        """
        text = text.replace(' ', '%20')
        icon = random.randint(1, 44)

        file = await self.alex_image(f'achievement?text={text}&icon={icon}')
        await ctx.send(file=file)

    @commands.command()
    async def challenge(self, ctx: Context, *, text: str) -> None:
        """Minecraft "Challenge Complete!" meme maker.

        Example:
            **{p}challenge slept more than 6 hours**

        Args:
            text (str): A text for the challenge.
        """
        text = text.replace(' ', '%20')
        icon = random.randint(1, 45)

        file = await self.alex_image(f'challenge?text={text}&icon={icon}')
        await ctx.send(file=file)

    @commands.command()
    async def triggered(self, ctx: Context, image: Optional[str]) -> None:
        """Make the "TrIgGeReD" meme.

        Example:
            **{p}triggered @Dosek** - triggers Dosek.

        Args:
            image (Optional[str]): An image you want to get "triggered".
        """
        image = await make_image_url(ctx, image)

        file = await self.dagpi_image(f'triggered?url={image}', 'triggered.gif')
        await ctx.send(file=file)

    @commands.command(name='ascii')
    async def ascii_command(self, ctx: Context, image: Optional[str]) -> None:
        """Get the ASCII version of an image.

        Example:
            **{p}ascii @Dosek** - sends ASCII version of Dosek's avatar.

        Args:
            image (Optional[str]): An image you want to ASCII'ize.
        """
        image = await make_image_url(ctx, image)

        file = await self.dagpi_image(f'ascii?url={image}', 'ascii.png')
        await ctx.send(file=file)

    @commands.command()
    async def coinflip(self, ctx: Context):
        """Play the simple coinflip game.

        Chances:
        --------
        **head → 49.5%**; **tail → 49.5%**; **side → 1%**
        """
        choice = random.choices(
            population=['head', 'tail', 'side'],
            weights=[0.49, 0.49, 0.02],
            k=1
        )[0]

        if choice == 'side':
            return await ctx.send('Coin was flipped **to the side**!')

        await ctx.send(f'Coin flipped to the `{choice}`, no reward.')

    @flags.add_flag('--timeout', type=float, default=60.0,
                    help='Set your own timeout! Defaults to 60 seconds.')
    @flags.command(aliases=['tr', 'typerace'])
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def typeracer(self, ctx: Context, **flags):
        """Typeracer game. Compete with others and find out the best typist.

        If you don't like the given quote, react with a wastebasket to close the game.

        Example:
            **{p}tr** - the default round for 60 seconds.
            **{p}typeracer --timeout 30** - makes a round for 30 seconds.**

        Raises:
            commands.BadArgument: If too big or too small timeout was set.

        Returns:
            The average WPM of the winner, spent time and the original text.
        """
        timeout = flags.pop('timeout')
        if not 10.0 < timeout < 120.0:
            raise commands.BadArgument('Timeout limit has been reached. Specify between 10 and 120.')

        async with ctx.loading:
            r = await (await self.bot.session.get(ctx.config.api.quote)).json()
            content = r['content']
            buffer = await Manip.typeracer('\n'.join(textwrap.wrap(content, 30)))

        embed = ctx.embed(
            title='Typeracer', description='see who is the fastest at typing.'
        ).set_image(url='attachment://typeracer.png')
        embed.set_footer(text=f'© {r["author"]}')

        race = await ctx.send(file=discord.File(buffer, 'typeracer.png'), embed=embed)
        await race.add_reaction('🗑')
        start = time()

        try:
            done, pending = await asyncio.wait([
                self.bot.wait_for(
                    'raw_reaction_add',
                    check=lambda p: str(p.emoji) == '🗑' and p.user_id == ctx.author.id and p.message_id == race.id
                ),
                self.bot.wait_for(
                    'message',
                    check=lambda m: m.content == content,
                    timeout=timeout
                )
            ], return_when=asyncio.FIRST_COMPLETED)

            stuff = done.pop().result()

            if isinstance(stuff, discord.RawReactionActionEvent):
                return await race.delete()

            final = round(time() - start, 2)
            embed = ctx.embed(
                title=f'{stuff.author} won!',
                description=f'**Done in**: {final}s\n'
                f'**Average WPM**: {r["length"] / 5 / (final / 60):.0f} words\n'
                f'**Original text:**```diff\n+ {content}```',
            )
            await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            await ctx.try_delete(race)

    @commands.command(aliases=['rps'])
    async def rockpaperscissors(self, ctx: Context) -> None:
        """The Rock-Paper-Scissors game.

        There are three different reactions:
        ------------------------------------
        🪨 - for rock; 📄 - for paper; ✂ - for scissors.
        """
        rps_dict = {
            '🪨': {'🪨': 'draw', '📄': 'lose', '✂': 'win'},
            '📄': {'🪨': 'win', '📄': 'draw', '✂': 'lose'},
            '✂': {'🪨': 'lose', '📄': 'win', '✂': 'draw'}
        }
        choice = random.choice([*rps_dict.keys()])
        embed = ctx.embed(description='**Choose one 👇**')
        msg = await ctx.send(embed=embed.set_footer(text='10 seconds left⏰'))

        for r in rps_dict.keys():
            await msg.add_reaction(r)

        try:
            r, u = await self.bot.wait_for(
                'reaction_add', timeout=10,
                check=lambda re, us: us == ctx.author and str(re) in rps_dict.keys() and re.message.id == msg.id
            )
            game = rps_dict.get(str(r.emoji))
            embed = ctx.embed(
                description=f'Result: **{game[choice].upper()}**\n'
                f'My choice: **{choice}**\n'
                f'Your choice: **{r.emoji}**'
            )
            await msg.edit(embed=embed)

        except asyncio.TimeoutError:
            await ctx.try_delete(msg)

    @commands.command()
    async def eject(
        self,
        ctx: Context,
        color: str.lower,
        *,
        name: Optional[str]
    ) -> None:
        """Among Us "ejected" meme maker.

        Example:
            **{p}eject blue yes Dosek** - sends an ejected meme of blue impostor with nick "Dosek"

        Args:
            color (str.lower): Color of an ejected guy.
            name (Optional[str]): The name of the impostor.

        Available colors:
            black • blue • brown • cyan • darkgreen • lime
            • orange • pink • purple • red • white • yellow
        """
        # This check is still bad since the API colors are limited
        # and ImageColor.getrgb supports more colors.
        if not color_exists(color):
            raise commands.BadArgument(f'Color {color} does not exist.')

        name = name or ctx.author.display_name
        url = f'https://vacefron.nl/api/ejected?name={name}&impostor=true&crewmate={color}'

        # Calling the API.
        r = await self.bot.session.get(url)
        # Bufferizing the fetched image.
        io = BytesIO(await r.read())

        # Sending to the contextual channel.
        await ctx.send(file=discord.File(fp=io, filename='ejected.png'))

    @commands.command(aliases=['pp', 'penis'])
    async def peepee(self, ctx, member: Optional[discord.Member]):
        """Get the random size of your PP.

        Example:
            **{p}pp @Dosek** - sends Dosek's pp size.

        Args:
            member (Optional[discord.Member]): A member whose pp size you'd like to check.
            Takes you as the member if no one was mentioned.
        """
        member = member or ctx.author
        sz = 100 if member.id in self.bot.owner_ids else random.randint(1, 10)
        await ctx.send('{}\'s pp size is:\n3{}D'.format(member, '=' * sz))
