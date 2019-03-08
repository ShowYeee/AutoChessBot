import discord
import asyncio
import time
from bs4 import BeautifulSoup
import requests
from discord.ext import commands
import json
import pymysql
from time import gmtime, strftime
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.interpolate import interp1d
import os
from boto.s3.connection import S3Connection


bot = commands.Bot(command_prefix='')
bot.remove_command('help')
ranklist = ['迷之棋手','♙ 士兵一段','♙ 士兵二段','♙ 士兵三段','♙ 士兵四段','♙ 士兵五段','♙ 士兵六段','♙ 士兵七段','♙ 士兵八段','♙ 士兵九段',
                    '♘ 騎士一段','♘ 騎士二段','♘ 騎士三段','♘ 騎士四段','♘ 騎士五段','♘ 騎士六段','♘ 騎士七段','♘ 騎士八段','♘ 騎士九段',
                    '♗ 主教一段','♗ 主教二段','♗ 主教三段','♗ 主教四段','♗ 主教五段','♗ 主教六段','♗ 主教七段','♗ 主教八段','♗ 主教九段',
                    '♖ 堡壘一段','♖ 堡壘二段','♖ 堡壘三段','♖ 堡壘四段','♖ 堡壘五段','♖ 堡壘六段','♖ 堡壘七段','♖ 堡壘八段','♖ 堡壘九段',
                    '♕ 國王','♔ 皇後']


class Info:
    def __init__(self,steamID):
        #取得GET
        r = requests.post('http://www.autochess-stats.com/backend/api/dacprofiles/' + steamID + '/requestfetch/')
        res  = requests.get('http://www.autochess-stats.com/backend/api/dacprofiles/'+ steamID)
        
        ress = res.text

        #JSON
        jd = json.loads(ress)

        #顯示
        self.name = jd['personaName']
        self.rank = ranklist[jd['dacProfile']['rank']]
        self.matches = jd['dacProfile']['matchesPlayed']
        self.candy = jd['dacProfile']['candies']
        self.couriers = len(jd['dacProfile']['availableCouriers'])
        self.steamicon = jd['iconUrl']

    def chart(self , steamID):
        #取得GET
        hs = requests.get('http://www.autochess-stats.com/backend/api/dacprofiles/' + steamID + '/changes/1')
        hss = hs.text

        #JSON
        jr = json.loads(hss)       
        data = jr
        x = []
        y = []
        time = []
        i = 0
        for s in data:
            if(s['newMmrLevel'] != 0):
                y.append(s['newMmrLevel'])
                x.append(i)
                time.append(s['timeFetched'][5:16].replace('T','\n'))
                i += 1
        time.reverse() 
        y.reverse()
        xx = np.array(x)
        yy = np.array(y)
        plt.figure(figsize=(8,4))
        plt.yticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38],
        ['Noob','♙ Soldier1','♙ Soldier2','♙ Soldier3','♙ Soldier4','♙ Soldier5','♙ Soldier6','♙ Soldier7','♙ Soldier8','♙ Soldier9',
        '♘ Knight1','♘ Knight2','♘ Knight3','♘ Knight4','♘ Knight5','♘ Knight6','♘ Knight7','♘ Knight8','♘ Knight9',
        '♗ Bishop1','♗ Bishop2','♗ Bishop3','♗ Bishop4','♗ Bishop5','♗ Bishop6','♗ Bishop7','♗ Bishop8','♗ Bishop9',
        '♖ Fortress1','♖ Fortress2','♖ Fortress3','♖ Fortress4','♖ Fortress5','♖ Fortress6','♖ Fortress7','♖ Fortress8','♖ Fortress9',
        '♕ King','♔ Queen'])
        plt.xticks(xx,time)
        plt.plot(xx,yy, '-',xx, yy,'o')
        plt.xlim([xx.min(),xx.max()])  # x軸邊界
        plt.ylim([yy.min(),yy.max()])  # y軸邊界
        plt.yticks(fontsize=10)
        plt.xticks(fontsize=8)
        plt.grid(linestyle='-.') 
        plt.fill_between(xx, yy, interpolate=True, color='green', alpha=0.3)
        plt.savefig(steamID + '.png')
        
    

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activitys = discord.Game(name = "刀塔自走棋")
    await bot.change_presence(activity = activitys)

@bot.command()
async def info(ctx , steamID):
    try:
        await ctx.send("查詢中，請稍等數秒...")
        discordID = ctx.author.id
        theinfo = Info(steamID)
        x = '- '
        steamurl = 'http://steamcommunity.com/profiles/' + steamID
        mysteam = "["+ theinfo.name +"]("+steamurl+")"
        embed = discord.Embed(title = ctx.author.name + " 排位查詢", description = "Steam名稱: " + mysteam, color=0xff0000) 
        embed.set_author(name="刀塔自走棋資料速查", icon_url="http://i.imgur.com/rlx1Kb2.png")
        embed.set_thumbnail(url = theinfo.steamicon)
        embed.add_field(name= '⁕ 目前牌位',  value = x + theinfo.rank , inline=False)
        embed.add_field(name= '⁕ 遊玩場次',  value = x +  str(theinfo.matches), inline=False)
        embed.add_field(name= '⁕ 糖果數量',  value = x +  str(theinfo.candy), inline=False)
        embed.add_field(name= '⁕ 信使數量',  value = x +  str(theinfo.couriers), inline=False)
        await ctx.send(embed=embed)  
        theinfo.chart(steamID)
        file = discord.File(steamID + '.png', filename = steamID + '.png')
        print(file)
        await ctx.send("", file=file) 
        print("(",strftime("%Y-%m-%d %H:%M:%S", gmtime()),"):",ctx.author.name,"(",ctx.author.id,"),Success(",steamID,")")

    except Exception  as n:
        await ctx.send("查無此人，請確定SteamID64")
        print("(",strftime("%Y-%m-%d %H:%M:%S", gmtime()),"):",ctx.author.name,"(",ctx.author.id,"),Fail")

    

@bot.command()
async def rank(ctx):

    try:
        await ctx.send("查詢中，請稍等數秒...")      
        discordID = ctx.author.id
        db = pymysql.connect(host=os.environ['host'], port=3306, user=os.environ['user'], passwd=os.environ['password'], db=os.environ['db'], charset='utf8')
        cursor = db.cursor()
        sql = 'SELECT steamID FROM player WHERE discordID = "%s";'
        cursor.execute(sql,discordID)  
        rows = [item[0] for item in cursor.fetchall()]
        steamID = rows[0]
        db.commit()
        db.close()
        theinfo = Info(steamID)
        x = '- '
        steamurl = 'http://steamcommunity.com/profiles/' + steamID
        mysteam = "["+ theinfo.name +"]("+steamurl+")"
        embed = discord.Embed(title = ctx.author.name + " 排位查詢", description = "Steam名稱: " + mysteam, color=0xff0000) 
        embed.set_author(name="刀塔自走棋資料速查", icon_url="http://i.imgur.com/rlx1Kb2.png")
        embed.set_thumbnail(url = theinfo.steamicon)
        embed.add_field(name= '⁕ 目前牌位',  value = x + theinfo.rank , inline=False)
        embed.add_field(name= '⁕ 遊玩場次',  value = x +  str(theinfo.matches), inline=False)
        embed.add_field(name= '⁕ 糖果數量',  value = x +  str(theinfo.candy), inline=False)
        embed.add_field(name= '⁕ 信使數量',  value = x +  str(theinfo.couriers), inline=False)
        await ctx.send(embed=embed)
        theinfo.chart(steamID)
        file = discord.File(steamID + '.png', filename = steamID + '.png')
        print(file)
        await ctx.send("", file=file)
        print("(",strftime("%Y-%m-%d %H:%M:%S", gmtime()),"):",ctx.author.name,"(",ctx.author.id,"),Success(",steamID,")")   
    except IndexError as n:
        await ctx.send("查詢錯誤，請確定有綁定SteamID64(-d.help)")
        print("(",strftime("%Y-%m-%d %H:%M:%S", gmtime()),"):",ctx.author.name,"(",ctx.author.id,"),Fail")
        

    
@bot.command()
async def bind(ctx , steamIDs):

    if(len(steamIDs) == 17): 
        db = pymysql.connect(host=os.environ['host'], port=3306, user=os.environ['user'], passwd=os.environ['password'], db=os.environ['db'], charset='utf8')
        cursor = db.cursor()

        discordID = ctx.author.id
        steamID = int(steamIDs)
        print(steamID)

        sqlStuff1 = 'DELETE FROM player WHERE discordID = "%s";'
        sqlStuff2 = 'INSERT INTO player (discordID, steamID) ''VALUES ("%s", "%s");'
        add = [(discordID), (discordID,steamID)]
        cursor.execute(sqlStuff1, add[0])
        cursor.execute(sqlStuff2, add[1])
        db.commit()
        db.close()

        await ctx.send(ctx.author.name + "綁定完成")
        print("(",strftime("%Y-%m-%d %H:%M:%S", gmtime()),"):",ctx.author.name,"(",ctx.author.id,"),Bind Success(",steamID,")")
    else:
        await ctx.send("綁定錯誤，請確定SteamID是否為17個數英組合(查詢ID: https://steamid.io/lookup)")



@bot.command()
async def Help(ctx):
    embed = discord.Embed(title="指令大全", color=0xeee657)
    embed.add_field(name="d.info <steamID64>", value="直接查詢玩家", inline=False)
    embed.add_field(name="d.bind <steamID64>", value="綁定自己SteamID64 (查詢ID: https://steamid.io/lookup)", inline=False)
    embed.add_field(name="d.myinfo <steamID64>", value="查詢自己牌位(請先用bind綁定)", inline=False)

    await ctx.send(embed=embed)

bot.run(os.environ['bot_token'])





