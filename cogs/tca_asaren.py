import os
import aiohttp
import random
import datetime
import discord
from discord.ext import commands, tasks


class MyCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        if "PROBLEMS_TOKEN" not in os.environ:
            raise ValueError("there is no atcoder_problems token")
        self.token = os.environ["PROBLEMS_TOKEN"]
        self.tugi_yasumi = False
        self.onoff = True
        self.create_bacha.start()

    def cog_unload(self):
        self.create_bacha.cancel()

    @commands.hybrid_command()
    @commands.is_owner()
    async def tugi_yasumi(self, ctx):
        self.tugi_yasumi = True
        await ctx.send("次回の朝練は休みになりました。")

    @commands.command()
    @commands.is_owner()
    async def asaren_onoff(self, ctx):
        self.onoff = not self.onoff
        await ctx.send(f"次回以降の朝練が{(self.onoff and 'オン') or 'オフ'}になりました。")

    @tasks.loop(time=datetime.time(21, 30, 0))
    async def create_bacha(self):
        if datetime.date.today().weekday() == 6:
            return
        if not self.onoff:
            return
        if self.tugi_yasumi:
            self.tugi_yasumi = False
            return
        contest_id = await self.create_contest()
        if isinstance(contest_id, discord.Message):
            return
        await self.bot.get_channel(1174529316902666341).send('今日の朝練: https://kenkoooo.com/atcoder/#/contest/show/' + contest_id)

    async def create_contest(
        self, start_time: datetime.time = datetime.time(7, 0),
        title: str = "TCA朝練#{date}", minutes: int = 70
    ):
        channel = self.bot.get_channel(1174529316902666341)
        if not isinstance(channel, discord.TextChannel):
            return
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            problem_json = await (await session.get("https://kenkoooo.com/atcoder/resources/problem-models.json")).json()

        # 問題の選定
        kouho = []
        kouho_green = []  # 緑diff*2
        kouho_blue = []  # 青diff*1
        for problem_id in problem_json.keys():
            if "abc" not in problem_id or 'difficulty' not in problem_json[problem_id]:
                continue
            if problem_json[problem_id]['is_experimental']:
                continue  # 試験管は除く。
            if 400 <= problem_json[problem_id]["difficulty"] < 800:
                kouho.append(problem_id)
            elif 800 <= problem_json[problem_id]["difficulty"] < 1200:
                kouho_green.append(problem_id)
            elif 1600 <= problem_json[problem_id]["difficulty"] < 2000:
                kouho_blue.append(problem_id)

        problems = []
        for _ in range(4):
            k = random.choice(kouho)
            kouho.remove(k)
            problems.append({'id': k, 'point': 100, 'order': 0})
        for _ in range(2):
            k = random.choice(kouho_green)
            kouho_green.remove(k)
            problems.append({'id': k, 'point': 200, 'order': 0})
        problems.append({
            'id': random.choice(kouho_blue),
            'point': 400, 'order': 0
        })
        start_dt = datetime.datetime.combine(datetime.date.today(), start_time)

        # コンテスト作成
        print("---------------\nCreating contest...\nproblems info:")
        for i in problems:
            print(f"- {i['id']} (diff: {problem_json[i['id']]['difficulty']})")
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'token=' + self.token
        }
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            r = await session.post('https://kenkoooo.com/atcoder/internal-api/contest/create', headers=headers, json={
                'title': title.format(date=start_dt.strftime(r"%m/%d")),
                'memo': "茶x4",
                'start_epoch_second': int(start_dt.timestamp()),
                'duration_second': minutes*60,
                'mode': None,
                'is_public': True,
                'penalty_second': 300,
            })
        if r.status != 200:
            return await channel.send("バチャの作成に失敗しました。")
        contest_id = (await r.json())['contest_id']

        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            r = await session.post('https://kenkoooo.com/atcoder/internal-api/contest/item/update', headers=headers, json={
                'contest_id': contest_id,
                'problems': problems
            })
        if r.status != 200:
            return await channel.send('バチャの問題設定に失敗しました。')
        return contest_id


async def setup(bot):
    await bot.add_cog(MyCog(bot))
