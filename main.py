import nextcord
from nextcord.ext import commands
import json
import os
import config
# กำหนด Intents
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(intents=intents)

DB_FILE = "keywords.json"

# โหลดหรือสร้างฐานข้อมูล
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        keywords = json.load(f)
else:
    keywords = {}

def save_keywords():
    """บันทึกฐานข้อมูลไปยังไฟล์ JSON"""
    with open(DB_FILE, "w") as f:
        json.dump(keywords, f, indent=4)

def is_admin(interaction: nextcord.Interaction):
    """ตรวจสอบว่าผู้ใช้เป็นแอดมินหรือไม่"""
    return interaction.user.guild_permissions.administrator


@bot.event
async def on_ready():
    print(f"Bot is on ready {bot.user}")

@bot.slash_command(name="addkeyword", description="เพิ่มคำสำคัญในห้อง (เฉพาะแอดมิน)")
async def add_keyword(interaction: nextcord.Interaction, channel: nextcord.TextChannel, keyword: str):
    if not is_admin(interaction):
        await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้!", ephemeral=True)
        return

    if str(channel.id) not in keywords:
        keywords[str(channel.id)] = []

    if keyword not in keywords[str(channel.id)]:
        keywords[str(channel.id)].append(keyword)
        save_keywords()
        await interaction.response.send_message(f"เพิ่มคำสำคัญ `{keyword}` ให้กับห้อง {channel.mention} แล้ว!", ephemeral=True)
    else:
        await interaction.response.send_message(f"คำสำคัญ `{keyword}` มีอยู่แล้วในห้อง {channel.mention}!", ephemeral=True)

@bot.slash_command(name="delkeyword", description="ลบคำสำคัญในห้อง (เฉพาะแอดมิน)")
async def del_keyword(interaction: nextcord.Interaction, channel: nextcord.TextChannel, keyword: str):
    if not is_admin(interaction):
        await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้!", ephemeral=True)
        return

    if str(channel.id) in keywords and keyword in keywords[str(channel.id)]:
        keywords[str(channel.id)].remove(keyword)
        if not keywords[str(channel.id)]:
            del keywords[str(channel.id)]  
        save_keywords()
        await interaction.response.send_message(f"ลบคำสำคัญ `{keyword}` จากห้อง {channel.mention} แล้ว!", ephemeral=True)
    else:
        await interaction.response.send_message(f"ไม่พบคำสำคัญ `{keyword}` ในห้อง {channel.mention}!", ephemeral=True)


@bot.slash_command(name="editkeyword", description="แก้ไขคำสำคัญในห้อง (เฉพาะแอดมิน)")
async def edit_keyword(interaction: nextcord.Interaction, channel: nextcord.TextChannel, old_keyword: str, new_keyword: str):
    if not is_admin(interaction):
        await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้!", ephemeral=True)
        return

    if str(channel.id) in keywords and old_keyword in keywords[str(channel.id)]:
        keywords[str(channel.id)].remove(old_keyword)
        keywords[str(channel.id)].append(new_keyword)
        save_keywords()
        await interaction.response.send_message(f"แก้ไขคำสำคัญ `{old_keyword}` เป็น `{new_keyword}` ในห้อง {channel.mention} แล้ว!", ephemeral=True)
    else:
        await interaction.response.send_message(f"ไม่พบคำสำคัญ `{old_keyword}` ในห้อง {channel.mention}!", ephemeral=True)

@bot.slash_command(name="listkeywords", description="แสดงคำสำคัญในห้อง (เฉพาะแอดมิน)")
async def list_keywords(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    if not is_admin(interaction):
        await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้!", ephemeral=True)
        return

    if str(channel.id) in keywords and keywords[str(channel.id)]:
        keyword_list = "\n".join(keywords[str(channel.id)])
        await interaction.response.send_message(f"คำสำคัญในห้อง {channel.mention}:\n```{keyword_list}```", ephemeral=True)
    else:
        await interaction.response.send_message(f"ห้อง {channel.mention} ยังไม่มีคำสำคัญ!", ephemeral=True)

@bot.event
async def on_message(message: nextcord.Message):
    if message.author.bot:
        return

    channel_id = str(message.channel.id)
    if channel_id in keywords:
        valid_keywords = keywords[channel_id]
        if not any(keyword in message.content for keyword in valid_keywords):
            await message.delete()  
        else:
            print(f"ข้อความที่ตรงกับคำสำคัญจาก {message.author}: {message.content}")

    await bot.process_commands(message)

bot.run(config.token)
