
import discord
from discord.ext import commands
from discord.ui import View, Select
from PIL import Image
import pytesseract
import re
import io

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

TIME_SLOTS = [
    "13:00–15:00",
    "15:00–17:00",
    "20:00–21:30",
    "21:40–23:00"
]

teams = [
    {
        "name": f"TEAM {i}",
        "logo": "🏆",
        "matches": 0,
        "booyah": 0,
        "kills": 0,
        "points": 0
    }
    for i in range(1, 13)
]

class TimeSelect(Select):
    def __init__(self, player_id):
        self.player_id = player_id
        super().__init__(
            placeholder="Chọn khung giờ",
            options=[
                discord.SelectOption(label=t, value=t)
                for t in TIME_SLOTS
            ]
        )

    async def callback(self, interaction):
        await interaction.response.send_message(
            f"ID: {self.player_id}\n"
            f"Khung giờ: {self.values[0]}",
            ephemeral=True
        )

class TimeView(View):
    def __init__(self, player_id):
        super().__init__(timeout=300)
        self.add_item(TimeSelect(player_id))

@bot.command()
async def td(ctx, player_id=None):
    if not player_id:
        await ctx.send("Dùng: .td ID người chơi")
        return

    await ctx.send(
        f"🎮 CUSTOM TC - ID {player_id}",
        view=TimeView(player_id)
    )

def make_table():
    ranked = sorted(
        teams,
        key=lambda t: t["points"],
        reverse=True
    )

    lines = [
        "HẠNG | LOGO | TÊN TEAM | SỐ TRẬN | BOOYAH | HẠ GỤC | ĐIỂM",
        "-" * 75
    ]

    for rank, team in enumerate(ranked, 1):
        lines.append(
            f"{rank} | {team['logo']} | {team['name']} | "
            f"{team['matches']} | {team['booyah']} | "
            f"{team['kills']} | {team['points']}"
        )

    return "\n".join(lines)

@bot.command()
async def bang(ctx):
    await ctx.send(
        "🏆 **CUSTOM TC - BẢNG TỔNG**\n"
        f"```text\n{make_table()}\n```"
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def doiten(ctx, so_doi: int, *, ten_moi: str):
    if not 1 <= so_doi <= 12:
        await ctx.send("Chỉ có đội từ 1 đến 12.")
        return

    teams[so_doi - 1]["name"] = ten_moi
    await ctx.send(f"Đã đổi tên đội {so_doi}: {ten_moi}")

@bot.command()
async def docanh(ctx):
    if not ctx.message.attachments:
        await ctx.send("Hãy gửi ảnh bảng tổng Garena kèm lệnh .docanh")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.content_type or not attachment.content_type.startswith("image/"):
        await ctx.send("Tệp gửi lên phải là hình ảnh.")
        return

    image_bytes = await attachment.read()
    image = Image.open(io.BytesIO(image_bytes))

    text = pytesseract.image_to_string(image, lang="eng")

    await ctx.send(
        "🔎 Nội dung OCR đọc được:\n"
        f"```text\n{text[:1500]}\n```\n"
        "Hãy kiểm tra dữ liệu trước khi nhập điểm."
    )

@bot.event
async def on_ready():
    print(f"CUSTOM TC online: {bot.user}")

bot.run("DAN_TOKEN_BOT_VAO_DAY")
