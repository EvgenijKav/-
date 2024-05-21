# -*- coding: utf-8 -*-
# Данная программа является музыкальным ботом для discord. Бот воспроизводит звук из любого видео на youtube. Используется официальная библиотека discord.
# Имеет базовые команды: "!help", "!play", "!leave", "!pause", "!resume", "!stop".

import time
#import asyncio
import os
import discord
import youtube_dl
from discord.ext import commands
from config import token #Берёт специальный токен конкретного боата, которого вы должныы создать на discord.dev. Файл с токеном вы тоже должны создать и хранить его рядом с основной программой.
                        #Ни в коем случае не делитесь токеном своего бота ни с кем!
bot = commands.Bot(command_prefix='!') #Чтобы командовать боту - используется префикс "!".
#songs = asyncio.Queue() #Эта и 15-ая строчка - попытка написать систему очереди. Так и не получилось(((.
#play_next_song = asyncio.Event()

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} #Настройки проигрывателя, который нужно установить отдельно. Любой, на ваш выбор.

@bot.event
async def on_ready():
    print('Bot online') #Каждый раз при включении бота - он подверждает свою готовность в консоли словами: "Bot online".

async def audio_player_task():
    while True:
        play_next_song.clear()
        current = await songs.get()
        current.start()
        await play_next_song.wait()

server, server_id, name_channel = None, None, None

domains = ['https://www.youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/'] #Поддерживаемые ботом ссылки.
async def check_domains(link): #Функция проверки ссылок.
    for x in domains:
        if link.startswith(x):
            return True
    return False

@bot.command(pass_context=True)
async def play(ctx, *, command = None): #Главная команда для воспроизведения музыки/звуков из видео.
    """Воспроизводит музыку"""
    global server, server_id, name_channel
    author = ctx.author
    if command == None:
        server = ctx.guild
        name_channel = author.voice.channel.name
        voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
    params = command.split(' ') #Команда проигрывания и ссылка в этой команде разделяются пробелом. Например: "!play https://www.youtube.com/...".
    if len(params) == 1:
        source = params [0]
        server = ctx.guild
        name_channel = author.voice.channel.name
        voice_channel = discord.utils.get(server.voice_channels, name=name_channel)
        print('param 1')
    elif len(params) == 3:
        server_id = params[0]
        voice_id = params[1]
        source = params[2]
        try:
            server_id = int(server_id)
            voice_id = int(voice_id)
        except:
            await ctx.chanell.send(f'{author.mention}, id сервера или голосового канала должно быть целочисленным.')
            return
        print('param 3')
        server = bot.get_guild(server_id)
        voice_channel = discord.utils.get(server.voice_channels, id=voice_id)
    else:
        await ctx.channnel.send(f'{author.mention}, Команда введена неправильно.')
        return

    voice = discord.utils.get(bot.voice_clients, guild = server)
    if voice is None:
        await voice_channel.connect()
        voice = discord.utils.get(bot.voice_clients, guild = server)
    if source == None:
        pass
    elif source.startswith('http'):
        if not check_domains(source):
            await ctx.channel.send(f'{author.mention}, Неподдерживаемая ссылка')
            return
        song_there = os.path.isfile('song.mp3') #Обращается к пустому файлу "song.mp3" который вы должны создать сами и указать к нему путь.
        try:
            if song_there:
                os.remove('song.mp3')
        except PermissionError:
            await ctx.channel.send('У тебя недостаточно прав на удаление.')
            return

        ydl_opts = {
            'format': 'bestaudio/best',
               'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
        } #Настройка для загрузчика mp3 файла (ну или любого другого файла звукого формата, какой вам угоден).

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([source])
        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                os.rename(file, 'song.mp3')
        voice.play(discord.FFmpegPCMAudio('song.mp3'))
    else:
        voice.play(discord.FFmpegPCMAudio(f'music/{source}')) #Указание пути к папке для скачеваемых файлов.

@bot.command()
async def leave(ctx):
    """Командует боту выйти из голосового канала"""
    global server, name_channel
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, Меня уже выгнали из голосового канала.')

@bot.command()
async def pause(ctx):
    """Ставит музыку на паузу"""
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, Вы остановили музыку. :raised_hand:')

@bot.command()
async def resume(ctx):
    """Включает, поставленную на паузу, музыку"""
    voice = discord.utils.get(bot.voice_clients, guild=server)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.channel.send(f'{ctx.author.mention}, Вы возобновили музыку. :arrow_forward:')

@bot.command()
async def stop(ctx):
    """Прекращает воспроизведение музыки"""
    voice = discord.utils.get(bot.voice_clients, guild=server)
    voice.stop()

def shutdown(offbot=19): #Автоматическое выключение бота после трёх минут бездействия.
    while time.gmtime().tm_hour < offbot:
        time.sleep(180)

# bot.loop.create_task(audio_player_task()) #Тоже часть попытки написать систему очереди. Пока что отключено.

bot.run(token)