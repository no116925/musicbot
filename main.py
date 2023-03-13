import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from discord.utils import get
from discord import FFmpegPCMAudio
import discord.gateway
import os
import chromedriver_autoinstaller as AutoChrome


chrome_ver = AutoChrome.get_chrome_version()
print(chrome_ver,"크롬버전입니다")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, timeout=None)
client = discord.Client(discord_prefix='!', intents=intents)
interaction = discord.interactions
message = discord.ext
user = []
musictitle = []
song_queue = []
musicnow = []

userF = []
userFlist = []
allplaylist = []
options = webdriver.ChromeOptions()
options.add_argument("headless")
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


def title(msg):
	global music

	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	options = webdriver.ChromeOptions()
	options.add_argument("headless")

	driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
	source = driver.page_source
	bs = bs4.BeautifulSoup(source, 'lxml')
	entire = bs.find_all('a', {'id': 'video-title'})
	entireNum = entire[0]
	music = entireNum.text.strip()
    
	musictitle.append(music)
	musicnow.append(music)
	test1 = entireNum.get('href')
	url = 'https://www.youtube.com'+test1
	with YoutubeDL(YDL_OPTIONS) as ydl:
		info = ydl.extract_info(url, download=False)
	URL = info['formats'][0]['url']

	driver.quit()

	return music, URL

def play(ctx):
	global vc
	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
	URL = song_queue[0]
	del user[0]
	del musictitle[0]
	del song_queue[0]
	vc = get(bot.voice_clients, guild=ctx.guild)
	if not vc.is_playing():
		vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 

def play_next(ctx):
	if len(musicnow) - len(user) >= 2:
		for i in range(len(musicnow) - len(user) - 1):
			del musicnow[0]
	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
	if len(user) >= 1:
		if not vc.is_playing():
			del musicnow[0]
			URL = song_queue[0]
			del user[0]
			del musictitle[0]
			del song_queue[0]
			vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

def load_chrome_driver():
      
	options = webdriver.ChromeOptions()

	options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

	options.add_argument('--headless')
	# options.add_argument('--disable-gpu')
	options.add_argument('--no-sandbox')

	return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), options=options)


@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(bot.user.name)
    print('connection was succesful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("우스 일"))
    
@bot.command()
async def 대기열추가(ctx, *, msg):
	user.append(msg)
	result, URLTEST = title(msg)
	song_queue.append(URLTEST)
	await ctx.send(result + "를 재생목록에 추가했어요!")

@bot.command()
async def 대기열삭제(ctx, *, number):
	try:
		ex = len(musicnow) - len(user)
		del user[int(number) - 1]
		del musictitle[int(number) - 1]
		del song_queue[int(number)-1]
		del musicnow[int(number)-1+ex]
            
		await ctx.send("대기열이 정상적으로 삭제되었습니다.")
	except:
		if len(list) == 0:
			await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
		else:
			if len(list) < int(number):
				await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
			else:
				await ctx.send("숫자를 입력해주세요!")

@bot.command()
async def 목록(ctx):
	if len(musictitle) == 0:
		await ctx.send("아직 아무노래도 등록하지 않았어요.")
	else:
		global Text
		Text = ""
		for i in range(len(musictitle)):
			Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
		await ctx.send(embed = discord.Embed(title= "노래목록", description = Text.strip(), color = 0x00ff00))

@bot.command()
async def 목록초기화(ctx):
	try:
		ex = len(musicnow) - len(user)
		del user[:]
		del musictitle[:]
		del song_queue[:]
		while True:
			try:
				del musicnow[ex]
			except:
				break
		await ctx.send(embed = discord.Embed(title= "목록초기화", description = """목록이 정상적으로 초기화되었습니다. 이제 노래를 등록해볼까요?""", color = 0x00ff00))
	except:
		await ctx.send("아직 아무노래도 등록하지 않았어요.")

@bot.command()
async def 목록재생(ctx):

	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
	if len(user) == 0:
		await ctx.send("아직 아무노래도 등록하지 않았어요.")
	else:
		if len(musicnow) - len(user) >= 1:
			for i in range(len(musicnow) - len(user)):
				del musicnow[0]
		if not vc.is_playing():
			play(ctx)
		else:
			await ctx.send("우뚜가 이미 부르고 있어요!")

@bot.command()
async def 들어와(ctx):
	try:
		global vc
		vc = await ctx.message.author.voice.channel.connect()
	except:
		try:
			await vc.move.to(ctx.message.author.voice.channel)
		except:
			await ctx.send("채널부터 들어가시죠?")
@bot.command()
async def 나가(ctx):
	try:
		await vc.disconnect()
	except:
		await ctx.send("애초에 부르기나 하시죠?")

@bot.command()
async def URL(ctx, *, url):
	YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	if not vc.is_playing():
		with YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(url, download=False)
		URL = info['formats'][0]['url']
		vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
		await ctx.send(embed = discord.Embed(title= "우뚜 노래 중", description = "현재 " + url + "을(를) 부르고 있습니다.", color = 0x00ff00))
	else:
		await ctx.send("노래가 이미 재생되고 있습니다!")

@bot.command()
async def 재생(ctx, *, msg):
	try:
		global vc
		vc = await ctx.message.author.voice.channel.connect()
	except:
		try:
			await vc.move.to(ctx.message.author.voice.channel)
		except:
			await ctx.send("채널부터 들어가시죠?")
	if not vc.is_playing():

		options = webdriver.ChromeOptions()
		options.add_argument("headless")

		global entireText
		YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
		FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


		driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
		source = driver.page_source
		bs = bs4.BeautifulSoup(source, 'lxml')
		entire = bs.find_all('a', {'id': 'video-title'})
		entireNum = entire[0]
		entireText = entireNum.text.strip()
		musicurl = entireNum.get('href')
		url = 'https://www.youtube.com'+musicurl

		driver.quit()

		musicnow.insert(0, entireText)
		with YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(url, download=False)
		URL = info['formats'][0]['url']
		await ctx.send(embed = discord.Embed(title= "우뚜 노래 중", description = "현재 " + musicnow[0] + "을(를) 부르고 있습니다.", color = 0x00ff00))
		vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
	else:
		user.append(msg)
		result,URLTEST = title(msg)
		song_queue.append(URLTEST)
		global Text
		Text = ""
		for i in range(len(musictitle)):
			Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
		await ctx.send(embed = discord.Embed(title= "우뚜 부를 목록", description = Text.strip(), color = 0x00ff00))

@bot.command()
async def 일시정지(ctx):
	if vc.is_playing():
		vc.pause()
		await ctx.send(embed = discord.Embed(title= "우뚜 노래 멈춤", description = musicnow[0] + "을(를) 멈췄습니다.", color = 0x00ff00))
	else:
		await ctx.send("예약부터 하시죠?")

@bot.command()
async def 다시재생(ctx):
	try:
		vc.resume()
	except:
		await ctx.send("예약부터 하시죠?")
	else:
		await ctx.send(embed = discord.Embed(title= "우뚜 노래 다시 시작", description = musicnow[0]  + "을(를) 다시 부르기 시작했습니다.", color = 0x00ff00))

@bot.command()
async def 다음곡(ctx):
	if vc.is_playing():
		vc.stop()
		await ctx.send(embed = discord.Embed(title= "우뚜 노래 스킵", description = musicnow[0]  + "을(를) 건너뛰었습니다.", color = 0x00ff00))
	else:
		await ctx.send("예약부터 하시죠?")

@bot.command()
async def 지금노래(ctx):
    if not vc.is_playing():
        await ctx.send("예약부터 하시죠?")
    else:
        await ctx.send(embed = discord.Embed(title = "우뚜 노래 중", description = "현재 " + musicnow[0] + "을(를) 부르고 있습니다.", color = 0x00ff00))

@bot.command()
async def 멜론차트(ctx):
	if not vc.is_playing():
        
		options = webdriver.ChromeOptions()
		options.add_argument("headless")

		global entireText
		YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
		FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
		
		driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
		driver.get("https://www.youtube.com/results?search_query=멜론차트")
		source = driver.page_source
		bs = bs4.BeautifulSoup(source, 'lxml')
		entire = bs.find_all('a', {'id': 'video-title'})
		entireNum = entire[0]
		entireText = entireNum.text.strip()
		musicurl = entireNum.get('href')
		url = 'https://www.youtube.com'+musicurl 

		driver.quit()
	
		with YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(url, download=False)
		URL = info['formats'][0]['url']
		await ctx.send(embed = discord.Embed(title= "우뚜 노래 시작", description = "현재 " + entireText + "을(를) 부르고 있습니다.", color = 0x00ff00))
		vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
	else:
		await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없어요!")
	
@bot.command()
async def 즐겨찾기(ctx):
	global Ftext
	Ftext = ""
	correct = 0
	global Flist
	for i in range(len(userF)):
		if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
			correct = 1 #있으면 넘김
	if correct == 0:
		userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
		userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듬.
		userFlist[len(userFlist)-1].append(str(ctx.message.author.name))
        
	for i in range(len(userFlist)):
		if userFlist[i][0] == str(ctx.message.author.name):
			if len(userFlist[i]) >= 2: # 노래가 있다면
				for j in range(1, len(userFlist[i])):
					Ftext = Ftext + "\n" + str(j) + ". " + str(userFlist[i][j])
				titlename = str(ctx.message.author.name) + "님의 즐겨찾기"
				embed = discord.Embed(title = titlename, description = Ftext.strip(), color = 0x00ff00)
				embed.add_field(name = "목록에 추가\U0001F4E5", value = "즐겨찾기에 모든 곡들을 목록에 추가합니다.", inline = False)
				embed.add_field(name = "플레이리스트로 추가\U0001F4DD", value = "즐겨찾기에 모든 곡들을 새로운 플레이리스트로 저장합니다.", inline = False)
				Flist = await ctx.send(embed = embed)
				await Flist.add_reaction("\U0001F4E5")
				await Flist.add_reaction("\U0001F4DD")
			else:
				await ctx.send("아직 등록하신 즐겨찾기가 없어요.")



@bot.command()
async def 즐겨찾기추가(ctx, *, msg):
	correct = 0
	for i in range(len(userF)):
		if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
			correct = 1 #있으면 넘김
	if correct == 0:
		userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
		userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
		userFlist[len(userFlist)-1].append(str(ctx.message.author.name))

	for i in range(len(userFlist)):
		if userFlist[i][0] == str(ctx.message.author.name):
            
			options = webdriver.ChromeOptions()
			options.add_argument("headless")

			driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
			driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
			source = driver.page_source
			bs = bs4.BeautifulSoup(source, 'lxml')
			entire = bs.find_all('a', {'id': 'video-title'})
			entireNum = entire[0]
			music = entireNum.text.strip()

			driver.quit()

			userFlist[i].append(music)
			await ctx.send(music + "(이)가 정상적으로 등록되었어요!")



@bot.command()
async def 즐겨찾기삭제(ctx, *, number):
	correct = 0
	for i in range(len(userF)):
		if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
			correct = 1 #있으면 넘김
	if correct == 0:
		userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
		userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
		userFlist[len(userFlist)-1].append(str(ctx.message.author.name))

	for i in range(len(userFlist)):
		if userFlist[i][0] == str(ctx.message.author.name):
			if len(userFlist[i]) >= 2: # 노래가 있다면
				try:
					del userFlist[i][int(number)]
					await ctx.send("정상적으로 삭제되었습니다.")
				except:
					await ctx.send("입력한 숫자가 잘못되었거나 즐겨찾기의 범위를 초과하였습니다.")
			else:
				await ctx.send("즐겨찾기에 노래가 없어서 지울 수 없어요!")
		
@bot.command()
async def 즐겨찾기재생(ctx):
	try:
		global vc
		vc = await ctx.message.author.voice.channel.connect()
	except:
		try:
			await vc.move.to(ctx.message.author.voice.channel)
		except:
			await ctx.send("즐겨찾기 불러오는 중")
	global Ftext
	Ftext = ""
	correct = 0
	global Flist
	for i in range(len(userF)):
		if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
			correct = 1 #있으면 넘김
			print(userFlist)
		if correct == 0:
			userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
			userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듬.
			userFlist[len(userFlist)-1].append(str(ctx.message.author.name))
        
		for i in range(len(userFlist)):
			for j in range(1, len(userFlist[i])):
				if not vc.is_playing():
					options = webdriver.ChromeOptions()
					options.add_argument("headless")

					global entireText
					YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
					driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
					driver.get("https://www.youtube.com/results?search_query="+str(userFlist[i][j])+"+lyrics")
					source = driver.page_source
					bs = bs4.BeautifulSoup(source, 'lxml')
					entire = bs.find_all('a', {'id': 'video-title'})
					entireNum = entire[0]
					entireText = entireNum.text.strip()
					musicurl = entireNum.get('href')
					url = 'https://www.youtube.com'+musicurl

					driver.quit()

					musicnow.insert(0, entireText)
					with YoutubeDL(YDL_OPTIONS) as ydl:
						info = ydl.extract_info(url, download=False)
					URL = info['formats'][0]['url']
					vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
				else:
					user.append(userFlist[i][j])
					result,URLTEST = title(userFlist[i][j])
					song_queue.append(URLTEST)
					global Text
					Text = ""
					for k in range(len(musictitle)):
							Text = Text + "\n" + str(k + 1) + ". " + str(musictitle[k])
					await ctx.send(embed = discord.Embed(title= "우뚜 부를 목록", description = Text.strip(), color = 0x00ff00))



bot.run('MTA4MjUxODY2NDA5MzM4ODkxMA.GZ6k1o.Zbab8zpQkZSm2Ko5HaY_HOfYX0xza6X2-X75Po')
