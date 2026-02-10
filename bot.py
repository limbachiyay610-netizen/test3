import discord
from discord.ext import commands
from discord import app_commands
import requests, csv
from io import StringIO
from PIL import Image, ImageDraw, ImageFont

# ========== CONFIG ==========
TOKEN = "MTQ3MDMzNTI5NTUxMjY0MTU1OQ.Gxuh14.cB_fSZnGcCudyKdESDDZ609BaBrylSJTSMpiQ4"

ADMIN_ROLE_ID = 1431219831322968074      # ADMIN ROLE ID
LEADERBOARD_CHANNEL_ID = 1431223777600999525  # CHANNEL ID

CSV_URL = "https://docs.google.com/spreadsheets/d/1EpRPwqOB7q8O9V2cp2khb0cAijGiXid1ZXPKQnwzsG4/export?format=csv"
TOP_LIMIT = 50
# ============================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- HELPERS ----------

def mask_username(name):
    name = str(name)
    if len(name) <= 4:
        return "xx**"
    return name[:3] + "*" * (len(name) - 5) + name[-2:]


def read_sheet():
    r = requests.get(CSV_URL, timeout=20)
    r.raise_for_status()

    reader = csv.DictReader(StringIO(r.text))
    data = []

    for row in reader:
        row = {k.strip().lower(): v for k, v in row.items() if k}
        user = row.get("username")
        wager = row.get("wager")

        if not user or not wager:
            continue

        try:
            wager = float(str(wager).replace(",", "").replace("$", ""))
            data.append({"user": user, "wager": wager})
        except:
            pass

    data.sort(key=lambda x: x["wager"], reverse=True)
    return data[:TOP_LIMIT]


def generate_image(data):
    bg = Image.open("background.jpg").convert("RGB")
    W, H = bg.size
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 60)
        sub_font = ImageFont.truetype("arialbd.ttf", 34)
        head_font = ImageFont.truetype("arialbd.ttf", 30)
        row_font = ImageFont.truetype("arialbd.ttf", 32)
        small_font = ImageFont.truetype("arialbd.ttf", 26)
    except:
        title_font = sub_font = head_font = row_font = small_font = ImageFont.load_default()

    # ---------- TITLE ----------
    draw.text((W//2 - 260, 40), "STAKE x ADFET", fill="white", font=title_font)
    draw.text((W//2 - 260, 115), "WAGER LEADERBOARD", fill="#00bfff", font=sub_font)

    # ---------- HEADERS ----------
    y = 190
    draw.text((90, y), "RANK", fill="white", font=head_font)
    draw.text((250, y), "USERNAME", fill="white", font=head_font)
    draw.text((W - 350, y), "WAGER", fill="white", font=head_font)

    draw.line((80, y + 40, W - 80, y + 40), fill="#00bfff", width=2)

    # ---------- ROWS ----------
    y += 65
    for i, row in enumerate(data, start=1):
        draw.text((90, y), f"{i:02}", fill="white", font=row_font)
        draw.text((250, y), mask_username(row["user"]), fill="white", font=row_font)
        draw.text((W - 350, y), f"${int(row['wager'])}", fill="white", font=row_font)
        y += 45

    # ---------- FOOTER ----------
    draw.line((200, H - 130, W - 200, H - 130), fill="white", width=1)
    draw.text((W//2 - 140, H - 95), "USE CODE ADFET", fill="white", font=small_font)

    img.save("leaderboard.png")
    return "leaderboard.png"

# ---------- EVENTS ----------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ Bot online")

# ---------- COMMAND ----------

@bot.tree.command(name="leaderboard", description="Show wager leaderboard")
async def leaderboard(interaction: discord.Interaction):

    if interaction.channel_id != CHANNEL_ID:
        await interaction.response.send_message("❌ Wrong channel", ephemeral=True)
        return

    if not any(r.id == ADMIN_ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    data = read_sheet()
    if not data:
        await interaction.followup.send("❌ No data found")
        return

    img = generate_image(data)
    await interaction.followup.send(file=discord.File(img))

# ---------- RUN ----------
bot.run(TOKEN)
