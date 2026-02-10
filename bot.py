import discord
from discord import app_commands
from discord.ext import commands
import requests, csv
from io import StringIO
from PIL import Image, ImageDraw, ImageFont

# ============ CONFIG ============
TOKEN = "PASTE_BOT_TOKEN"


ADMIN_ROLE_ID = 1431219831322968074      # ADMIN ROLE ID
LEADERBOARD_CHANNEL_ID = 1431223777600999525  # CHANNEL ID

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1EpRPwqOB7q8O9V2cp2khb0cAijGiXid1ZXPKQnwzsG4/edit?usp=sharing"
TOP_LIMIT = 50
# ================================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def mask_username(name: str):
    if len(name) <= 4:
        return "xx**"
    return name[:3] + "*" * (len(name)-5) + name[-2:]

def read_sheet():
    r = requests.get(SHEET_CSV_URL, timeout=20)
    r.raise_for_status()
    rows = []
    for row in csv.DictReader(StringIO(r.text)):
        try:
            rows.append({
                "user": row["user_name"],
                "wager": float(row["wager"])
            })
        except:
            pass
    rows.sort(key=lambda x: x["wager"], reverse=True)
    return rows[:TOP_LIMIT]

def generate_image(data):
    h = 140 + len(data) * 34
    img = Image.new("RGB", (1000, h), "#0b1220")
    d = ImageDraw.Draw(img)

    try:
        title = ImageFont.truetype("arial.ttf", 36)
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        title = font = ImageFont.load_default()

    d.text((260, 30), "TOP 50 WAGER LEADERBOARD", fill="#facc15", font=title)

    y = 100
    for i, u in enumerate(data, 1):
        d.text((40, y), f"{i}.", fill="white", font=font)
        d.text((100, y), mask_username(u["user"]), fill="white", font=font)
        d.text((780, y), f"${int(u['wager'])}", fill="white", font=font)
        y += 34

    img.save("leaderboard.png")
    return "leaderboard.png"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ Slash commands synced")

@bot.tree.command(name="leaderboard", description="Post Top 50 leaderboard")
async def leaderboard(interaction: discord.Interaction):

    # channel check
    if interaction.channel_id != LEADERBOARD_CHANNEL_ID:
        await interaction.response.send_message(
            "❌ Wrong channel", ephemeral=True
        )
        return

    # role check
    if not any(r.id == ADMIN_ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(
            "❌ You are not allowed", ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)

    data = read_sheet()
    if not data:
        await interaction.followup.send("❌ No data found")
        return

    img = generate_image(data)
    await interaction.followup.send(file=discord.File(img))

bot.run(TOKEN)
