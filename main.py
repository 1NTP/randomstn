import discord
from discord.ext import commands
from discord import Option
import os
import random

staffs = [421964224118652939]

nameToPath = {}

guildTeam1Select = {}
guildTeam2Select = {}

guildTeam1Count = {}
guildTeam2Count = {}

guildDupeStn = {}

PREFIX = '!'
TOKEN = ''

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
intents.typing = True
intents.guilds = True
intents.presences = False
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
client = discord.Client()

async def disableAllButtons(ctx: discord.Interaction):
    for component in ctx.message.components:
        if isinstance(component, discord.ui.Button):
            component.disabled = True

            await ctx.message.edit(components=ctx.message.components)

class CompleteMission(discord.ui.View):
    @discord.ui.button(label="미션 완료", style=discord.ButtonStyle.primary, emoji="✅")
    async def button_callback(self, button, ctx: discord.Interaction):
        teamStr = await getRoleName("stnTeam:", ctx.user)
        team = ctx.message.content.split('\n')[0].split(": ", 1)[1]   
        if teamStr == team:
            await ctx.response.send_message(f"미션을 완료했습니다.", ephemeral=True)
            await disableAllButtons(ctx)
            if teamStr == "stnTeam: Line1":
                guildTeam1Select.pop(ctx.guild.id)
            else:
                guildTeam2Select.pop(ctx.guild.id)
        

class TwoImages(discord.ui.View):
    @discord.ui.button(label="선택: 1", style=discord.ButtonStyle.primary, emoji="1️⃣")
    async def button_callback1(self, button, ctx: discord.Interaction):
        teamStr = await getRoleName("stnTeam:", ctx.user)
        team = ctx.message.content.split('\n')[0].split(": ", 1)[1]   
        if teamStr == team:
            stn = ctx.message.content.split('\n')[-1].split(" vs ")[0]
            if teamStr == "stnTeam: Line1":
                guildTeam1Select[ctx.guild.id] = stn
            else:
                guildTeam2Select[ctx.guild.id] = stn
        
            
            await ctx.response.send_message(f"{stn}을 선택하셨습니다.")
            await disableAllButtons(ctx)
        else:
            ctx.response.send_message("당신의 팀이 아닙니다.", ephemeral=True)
    @discord.ui.button(label="선택: 2", style=discord.ButtonStyle.primary, emoji="2️⃣")
    async def button_callback2(self, button, ctx: discord.Interaction):
        teamStr = await getRoleName("stnTeam:", ctx.user)
        team = ctx.message.content.split('\n')[0].split(": ", 1)[1]
        
        if teamStr == team:
            stn = ctx.message.content.split('\n')[-1].split(" vs ")[1]
            
            if teamStr == "stnTeam: Line1":
                guildTeam1Select[ctx.guild.id] = stn
            else:
                guildTeam2Select[ctx.guild.id] = stn
            
            await ctx.response.send_message(f"{stn}을 선택하셨습니다.")
            await disableAllButtons(ctx)
        else:
            ctx.response.send_message("당신의 팀이 아닙니다.", ephemeral=True)
        
        

async def removeTeamRole(str: str, user: discord.Member):
    for role in user.roles:
        if role.name.__contains__(str):
            await user.remove_roles(role)
             
async def addNamedRole(roleName: str, user: discord.Member):
    rolesStr = []
    for role in user.guild.roles:
        rolesStr.append(role.name)
    
    if not rolesStr.__contains__(roleName):
        await user.guild.create_role(name=roleName)
    for role in user.guild.roles:
        if role.name == roleName:
            await user.add_roles(role)

async def getRoleName(str: str, user: discord.Member):
    for role in user.roles:
        if role.name.__contains__(str):
            return role.name
    return None

def addDupeImage(guild: discord.guild, str: str):
    if not guild in guildDupeStn:
        guildDupeStn[guild] = []
        
    guildDupeStn[guild].append(str)

def dupeList(guild: discord.guild):
    if not guild in guildDupeStn:
        guildDupeStn[guild] = []
    return guildDupeStn[guild]

def getRandomSubfolder(base_folder):
    subfolders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

    if not subfolders:
        return None

    selected_subfolder = random.choice(subfolders)
    return f"{base_folder}\\{selected_subfolder}"

def pathToStnName(path: str):
    nameWithDot = path.split("\\")[-1]
    name = nameWithDot.split(".")[0].split("_")[-1]
    return name

async def sendRandomImage(ctx: discord.Interaction, folder_path):
    if folder_path == None:
        return await ctx.send("오류: 폴더 경로를 찾을 수 없습니다.")
    if not os.path.exists(folder_path):
        return await ctx.send("오류: 폴더를 찾을 수 없습니다.")

    image_files = [f for f in os.listdir(folder_path) if f.endswith(('png', 'jpg', 'jpeg', 'gif')) and not dupeList(ctx.guild).__contains__(f)]
    
    if len(image_files) < 1:
        return await ctx.send("남은 역이 없습니다!")

    if not image_files:
        return await ctx.send("오류: 폴더에 이미지가 없습니다.") 
    
    selected_image = random.choice(image_files)
    addDupeImage(ctx.guild, selected_image)   
    image_path = os.path.join(folder_path, selected_image)


    with open(image_path, 'rb') as image_file:
        teamStr = await getRoleName("stnTeam:", ctx.user)
        image = discord.File(image_file)
        nameToPath[pathToStnName(image_path)] = image_path
        await ctx.response.send_message(f"팀: {teamStr}\n역을 뽑았습니다!\n{pathToStnName(image_path)}", file=image)
                
   
async def sendTwoImages(ctx: discord.Interaction, folder_path: str):
    if folder_path == None:
        return await ctx.send("오류: 폴더 경로를 찾을 수 없습니다.")
    
    if not os.path.exists(folder_path):
        return await ctx.send("오류: 폴더를 찾을 수 없습니다.")

    image_pathes = []

    #여기부터 반복
    for i in range(2):
        while (randomPath := getRandomSubfolder(folder_path)) is None:
            pass
        
        image_files = [f for f in os.listdir(randomPath) if f.endswith(('png', 'jpg', 'jpeg', 'gif')) and not dupeList(ctx.guild).__contains__(f)]
        
        if len(image_files) < 1:
            return await ctx.send("남은 역이 없습니다!")
        
        if not image_files:
            return await ctx.send("오류: 폴더에 이미지가 없습니다.")

        selected_image = random.choice(image_files)
        image_path = os.path.join(randomPath, selected_image)
        addDupeImage(ctx.guild, selected_image)
        
        image_pathes.append(image_path)
        
        
    with open(image_pathes[0], 'rb') as image_file1, open(image_pathes[1], 'rb') as image_file2:
        teamStr = await getRoleName("stnTeam:", ctx.user)
        nameToPath[pathToStnName(image_pathes[0])] = image_pathes[0]
        nameToPath[pathToStnName(image_pathes[1])] = image_pathes[1]
        await ctx.response.send_message(f"팀: {teamStr}\n역을 뽑았습니다!\n{pathToStnName(image_pathes[0])} vs {pathToStnName(image_pathes[1])}", files=[discord.File(image_file1), discord.File(image_file2)], view=TwoImages())
        
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}.')
    
    
@bot.event
async def on_message(message):
    if message.author == client.user:
        return

@bot.slash_command(description = '랜덤 지하철')
async def stn(ctx: discord.Interaction, arg: Option(str, "명령어를 선택하세요.", choices = ["draw", "current station", "join line1", "join line2", "leave team", "author"])):
    if arg == "author":
        await ctx.response.send_message("제작자: uwuaden (디스코드: 1ntp)", ephemeral=True)
    if arg == "join line1":
        await removeTeamRole("stnTeam:", ctx.user)
        await addNamedRole("stnTeam: Line1", ctx.user)
        await ctx.response.send_message("Line1 팀에 추가되었습니다.", ephemeral=True)
    if arg == "join line2":
        await removeTeamRole("stnTeam:", ctx.user)
        await addNamedRole("stnTeam: Line2", ctx.user)
        await ctx.response.send_message("Line2 팀에 추가되었습니다.", ephemeral=True)
    if arg == "leave team":
        await removeTeamRole("stnTeam:", ctx.user)
        await ctx.response.send_message("팀을 나갔습니다.", ephemeral=True)
    if arg == "draw":
        teamStr = await getRoleName("stnTeam:", ctx.user)
        if teamStr == None:
            await ctx.response.send_message("팀에 포함되어 있지 않습니다.", ephemeral=True)
            return
        
        if not ctx.guild_id in guildTeam1Count:
            guildTeam1Count[ctx.guild_id] = 0
        if not ctx.guild_id in guildTeam2Count:
            guildTeam2Count[ctx.guild_id] = 0
        
        if teamStr == "stnTeam: Line1":
            if guildTeam1Select.__contains__(ctx.guild.id):
                await ctx.response.send_message("이미 역이 선택되어 있습니다.", ephemeral=True)
                return
            if guildTeam1Count[ctx.guild_id] >= 1:
                await sendTwoImages(ctx, "stn")
            else:
                await sendRandomImage(ctx, "stn\\1호선")
            guildTeam1Count[ctx.guild_id] = guildTeam1Count[ctx.guild_id] + 1
        else:
            if guildTeam2Select.__contains__(ctx.guild.id):
                await ctx.response.send_message("이미 역이 선택되어 있습니다.", ephemeral=True)
                return
            if guildTeam2Count[ctx.guild_id] >= 1:
                await sendTwoImages(ctx, "stn")
            else:
                await sendRandomImage(ctx, "stn\\2호선")
            guildTeam2Count[ctx.guild_id] = guildTeam2Count[ctx.guild_id] + 1
            
    if arg == "current station":
        teamStr = await getRoleName("stnTeam:", ctx.user)
        if teamStr == None:
            await ctx.response.send_message("팀에 포함되어 있지 않습니다.", ephemeral=True)
            return
        
        
        if teamStr == "stnTeam: Line1":
            if not guildTeam1Select.__contains__(ctx.guild_id):
                await ctx.response.send_message(f"선택된 역이 없습니다.", ephemeral=True)
                return
            
            path = nameToPath[guildTeam1Select[ctx.guild.id]]
            if path != None:
                with open(path, 'rb') as image_file:
                    image = discord.File(image_file)
                    await ctx.response.send_message(f"팀: {teamStr}\n현재 선택된 역: {guildTeam1Select[ctx.guild.id]}", file=image, view=CompleteMission())
            else:
                await ctx.response.send_message(f"선택된 역이 없습니다.", ephemeral=True)
        else:
            if not guildTeam2Select.__contains__(ctx.guild_id):
                await ctx.response.send_message(f"선택된 역이 없습니다.", ephemeral=True)
                return
            path = nameToPath[guildTeam2Select[ctx.guild.id]]
            if path != None:
                with open(path, 'rb') as image_file:
                    image = discord.File(image_file)
                    await ctx.response.send_message(f"팀: {teamStr}\n현재 선택된 역: {guildTeam2Select[ctx.guild.id]}", file=image, view=CompleteMission())
            else:
                await ctx.response.send_message(f"선택된 역이 없습니다.", ephemeral=True)
    
try:
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")
