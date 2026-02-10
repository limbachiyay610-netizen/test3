import discord
from discord import app_commands
from discord.ext import commands
import requests, csv
from io import StringIO
from PIL import Image, ImageDraw, ImageFont

# ================= CONFIG =================

TOKEN = "MTQ3MDMzNTI5NTUxMjY0MTU1OQ.Gxuh14.cB_fSZnGcCudyKdESDDZ609BaBrylSJTSMpiQ4"

ADMIN_ROLE_ID = 1431219831322968074      # ADMIN ROLE ID
LEADERBOARD_CHANNEL_ID = 1431223777600999525  # CHANNEL ID

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1EpRPwqOB7q8O9V2cp2khb0cAijGiXid1ZXPKQnwzsG4/export?format=csv"

TOP_LIMIT = 50

# =========================================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- UTIL FUNCTIONS ----------

def mask_username(name: str) -> str:
    name = str(name)
    if len(name) <= 4:
        return "xx**"
    return name[:3] + "*" * (len(name) - 5) + name[-2:]

def read_sheet():
    r = requests.get(SHEET_CSV_URL, timeout=20)
    r.raise_for_status()

    reader = csv.DictReader(StringIO(r.text))
    data = []

    for row in reader:
        username = (
            row.get("user_name") or
            row.get("USERNAME") or
            row.get("username")
        )

        wager = (
            row.get("wager") or
            row.get("WAGER")
        )

        if not username or not wager:
            continue

        try:
            data.append({
                "user": username.strip(),
                "wager": float(str(wager).replace(",", ""))
            })
        except:
            pass

    data.sort(key=lambda x: x["wager"], reverse=True)
    return data[:TOP_LIMIT]

def generate_image(data):
    height = 140 + len(data) * 34
    img = Image.new("RGB", (1000, height), "#0b1220")
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        title_font = font = ImageFont.load_default()

    draw.text((260, 30), "TOP 50 WAGER LEADERBOARD", fill="#facc15", font=title_font)

    y = 100
    for i, row in enumerate(data, start=1):
        draw.text((40, y), f"{i}.", fill="white", font=font)
        draw.text((100, y), mask_username(row["user"]), fill="white", font=font)
        draw.text((780, y), f"${int(row['wager'])}", fill="white", font=font)
        y += 34

    img.save("leaderboard.png")
    return "leaderboard.png"

# ---------- EVENTS ----------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ Bot online & slash commands synced")

# ---------- SLASH COMMAND ----------

@bot.tree.command(name="leaderboard", description="Post Top 50 wager leaderboard")
async def leaderboard(interaction: discord.Interaction):

    # Channel check
    if interaction.channel_id != LEADERBOARD_CHANNEL_ID:
        await interaction.response.send_message(
            "❌ Wrong channel", ephemeral=True
        )
        return

    # Role check
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message(
            "❌ You are not allowed", ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)

    data = read_sheet()
    if not data:
        await interaction.followup.send("❌ No data found in sheet")
        return

    img_path = generate_image(data)
    await interaction.followup.send(file=discord.File(img_path))

# ---------- RUN ----------

bot.run(TOKEN)
