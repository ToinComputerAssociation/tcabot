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
        self.create_bacha.start()

    def cog_unload(self):
        self.create_bacha.cancel()

    @tasks.loop(time=datetime.time(22, 30, 0))
    async def create_bacha(self):
        channel = self.bot.get_channel(1174529316902666341)
        if not isinstance(channel, discord.TextChannel):
            return
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            problem_json = await (await session.get("https://kenkoooo.com/atcoder/resources/problem-models.json")).json()

        # 問題の選定
        kouho = []
        for problem_id in problem_json.keys():
            if "abc" not in problem_id or 'difficulty' not in problem_json[problem_id]:
                continue
            if not 400 <= problem_json[problem_id]["difficulty"] < 800:
                continue  # 茶diffのみ選ぶ。
            if problem_json[problem_id]['is_experimental']:
                continue  # 試験管は除く。
            kouho.append(problem_id)

        problems = []
        for _ in range(4):
            problems.append({
                'id': random.choice(kouho),
                'point': 100, 'order': 0
            })
        start_dt = datetime.datetime.combine(datetime.date.today(), datetime.time(7, 45))

        # コンテスト作成
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'token=' + self.token
        }
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            r = await session.post('https://kenkoooo.com/atcoder/internal-api/contest/create', headers=headers, json={
                'title': "TCA朝練#"+start_dt.strftime(r"%m/%d"),
                'memo': "茶x4",
                'start_epoch_second': int(start_dt.timestamp()),
                'duration_second': 25*60,
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
        await channel.send('今日の朝練: https://kenkoooo.com/atcoder/#/contest/show/' + contest_id)


async def setup(bot):
    await bot.add_cog(MyCog(bot))
