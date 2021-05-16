import asyncio
import random

import discord
import selenium.common
from selenium import webdriver

user_agent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 '
    'Safari/537.36 '
]


async def process_output(p, m, msg, ctx):
    for line in iter(p.stdout.readline, b''):
        msg += line.rstrip().decode("utf-8") + "\n"
        try:
            await m.edit(content=msg)
        except discord.errors.HTTPException:
            msg = msg.splitlines()[-1]
            m = await ctx.send(msg)
    return msg, m


async def usedname(name,channel):
    # Chrome のオプションを設定する
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--user-agent=" + random.choice(user_agent))

    # Selenium Server に接続する
    driver = webdriver.Remote(
        command_executor='http://dockerserver_chrome-selenium_1:4444/wd/hub',
        desired_capabilities=options.to_capabilities(),
        options=options,
    )

    await channel.send("少々お待ちください(のこり最大約3分)")
    # Selenium 経由でブラウザを操作する
    driver.get('https://ja.namemc.com/search?q=' + name)
    try:
        if driver.find_element_by_css_selector(
                "#status-bar > div > div > div.col-md-5.text-center.my-1 > div > div:nth-child(1) > div:nth-child(2)"
        ).text == "Unavailable":
            return True
        else:
            return False
    except selenium.common.exceptions.NoSuchElementException:
        await asyncio.sleep(60*3)
        await usedname(name, channel)
    finally:
        driver.quit()


async def issetup(guild,cursor,channel,logger,send=True):
    logger.info("LIB:issetup:checking guild "+str(guild.id))
    cursor.execute(f"SELECT * FROM clanbot.guild_data WHERE guild_id={guild.id}")
    rows = cursor.fetchall()
    if len(rows) == 0:
        if send:
            await channel.send("最初に初期セットアップを`,setup` で行ってください。")
        return False
    else:
        return True
