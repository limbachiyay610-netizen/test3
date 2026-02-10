import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
import io

# ================== CONFIG ==================
TOKEN = "MTQ3MDMzNTI5NTUxMjY0MTU1OQ.Gxuh14.cB_fSZnGcCudyKdESDDZ609BaBrylSJTSMpiQ4"


ADMIN_ROLE_ID = 1431219831322968074
LEADERBOARD_CHANNEL_ID = 1431223777600999525

GOOGLE_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1EpRPwqOB7q8O9V2cp2khb0cAijGiXid1ZXPKQnwzsG4"
    "/export?format=csv"
)

BACKGROUND_IMAGE = "background.png"   # TU APNI IMAGE DEGA
FONT_PATH = "font.ttf"                # TU APNA FONT DEGA

TITLE_TEXT = "STAKE X ADEFT"
SUBTITLE_TEXT = "WAGER LEADERBOARD"
# ============================================


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


def fetch_sheet_data():
    r = requests.get(GOOGLE_SHEET_CSV)
    lines = r.text.splitlines()[1:]
    data = []

    for line in lines:
        row = line.split(",")
        if len(row) >= 2:
            username = row[0].strip()
            wager = row[1].strip()
            if username and wager:
                data.append((username, wager))

    return data[:50]


def generate_leaderboard(data):
    bg = Image.open(BACKGROUND_IMAGE).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    W, H = bg.size

    # 🔥 FONT SIZE BADHA DIYA (MAIN FIX)
    title_font = ImageFont.truetype(FONT_PATH, 90)
    header_font = ImageFont.truetype(FONT_PATH, 56)
    row_font = ImageFont.truetype(FONT_PATH, 48)

    # ---------- TITLE ----------
    draw.text((W//2 - 350, 40), TITLE_TEXT, fill="yellow", font=title_font)
    draw.text((W//2 - 360, 150), SUBTITLE_TEXT, fill="white", font=header_font)

    # ---------- HEADERS ----------
    start_y = 260
    draw.text((140, start_y), "RANK", fill="cyan", font=header_font)
    draw.text((320, start_y), "USERNAME", fill="cyan", font=header_font)
    draw.text((850, start_y), "WAGER", fill="cyan", font=header_font)

    y = start_y + 80   # 👈 spacing badhayi

    for i, (user, wager) in enumerate(data, start=1):
        draw.text((150, y), str(i), fill="white", font=row_font)
        draw.text((320, y), user, fill="white", font=row_font)
        draw.text((850, y), wager, fill="white", font=row_font)
        y += 60          # 👈 line gap badhaya

    out = io.BytesIO()
    bg.save(out, format="PNG")
    out.seek(0)
    return out


@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")


@bot.command()
async def leaderboard(ctx):
    if ctx.channel.id != LEADERBOARD_CHANNEL_ID:
        return

    if ADMIN_ROLE_ID not in [r.id for r in ctx.author.roles]:
        await ctx.send("❌ Admin only command")
        return

    data = fetch_sheet_data()
    if not data:
        await ctx.send("❌ No data found")
        return

    img = generate_leaderboard(data)
    await ctx.send(file=discord.File(img, "leaderboard.png"))


bot.run(TOKEN)
