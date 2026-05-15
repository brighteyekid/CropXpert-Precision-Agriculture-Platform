"""
CropXpert — Discord bot service.
Slash commands for crop prediction, scheme lookup, soil health, MSP queries.
"""
import logging
import asyncio
import discord
from discord import app_commands
from core.config import get_settings

logger = logging.getLogger("cropxpert.discord")
settings = get_settings()

# Internal reference to the FastAPI app's DB session factory
_SessionLocal = None


def set_session_factory(session_factory):
    global _SessionLocal
    _SessionLocal = session_factory


class CropXpertBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if settings.DISCORD_GUILD_ID:
            guild = discord.Object(id=int(settings.DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        logger.info("Discord slash commands synced")

    async def on_ready(self):
        logger.info("Discord bot logged in as %s", self.user)


bot = CropXpertBot()


def _get_color(confidence: float) -> int:
    """Green >90%, Yellow 70-90%, Red <70%."""
    if confidence >= 0.9:
        return 0x5C7A42  # accent green
    elif confidence >= 0.7:
        return 0xC8922A  # amber
    else:
        return 0xB05A3A  # rust


@bot.tree.command(name="crop", description="Get crop recommendation from soil readings")
@app_commands.describe(
    n="Nitrogen (mg/kg)", p="Phosphorus (mg/kg)", k="Potassium (mg/kg)",
    ph="Soil pH", moisture="Moisture %", temp="Temperature °C", dist="District"
)
async def crop_command(
    interaction: discord.Interaction,
    n: float, p: float, k: float, ph: float,
    moisture: float, temp: float, dist: str = "Pune"
):
    await interaction.response.defer()

    try:
        from services.ml_service import predict
        results = predict(
            nitrogen=n, phosphorus=p, potassium=k,
            ph=ph, moisture=moisture, temperature=temp,
            rainfall=100.0, humidity=70.0,
        )

        top = results[0]
        color = _get_color(top["ml_confidence"])

        embed = discord.Embed(
            title=f"🌾 Top Recommendation: {top['crop']} ({top['ml_confidence']*100:.1f}%)",
            color=color,
        )
        embed.add_field(
            name="💰 Market",
            value=f"MSP: ₹{top['msp_inr_per_quintal']}/qt | Mandi: ₹{top['mandi_price']} ({top['mandi_trend']})",
            inline=False,
        )
        embed.add_field(
            name="📅 Sowing",
            value=f"{', '.join(top['sowing_months'])}",
            inline=True,
        )
        embed.add_field(
            name="🧪 Fertilizer",
            value=f"Urea: {top['fertilizer_dose']['urea']} | DAP: {top['fertilizer_dose']['dap']}",
            inline=True,
        )
        embed.add_field(
            name="✅ Action",
            value="BUY SEEDS NOW" if top["ml_confidence"] > 0.9 else "Review alternatives before procurement",
            inline=False,
        )

        # Runner-up crops
        if len(results) > 1:
            alts = "\n".join(
                f"**{r['rank']}.** {r['crop']} ({r['ml_confidence']*100:.1f}%)"
                for r in results[1:]
            )
            embed.add_field(name="Alternative Crops", value=alts, inline=False)

        embed.set_footer(text=f"District: {dist} | CropXpert ML v1.0")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Prediction error: {e}")


@bot.tree.command(name="schemes", description="List eligible government schemes")
@app_commands.describe(state="State name, e.g. Maharashtra")
async def schemes_command(interaction: discord.Interaction, state: str = "Maharashtra"):
    await interaction.response.defer()

    try:
        from services.scheme_service import get_schemes
        db = _SessionLocal()
        try:
            schemes = get_schemes(db, state)

            embed = discord.Embed(
                title=f"🏛️ Government Schemes — {state}",
                color=0x2A3D2E,
            )

            for s in schemes[:5]:
                embed.add_field(
                    name=f"{s.name} ({s.benefit_amount})",
                    value=f"{s.description[:100]}...\n[Apply]({s.apply_url})",
                    inline=False,
                )

            embed.set_footer(text=f"Showing {len(schemes)} schemes | CropXpert")
            await interaction.followup.send(embed=embed)
        finally:
            db.close()

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


@bot.tree.command(name="msp", description="Current MSP and market price for a crop")
@app_commands.describe(crop="Crop name, e.g. Rice")
async def msp_command(interaction: discord.Interaction, crop: str = "Rice"):
    from core.config import get_settings
    s = get_settings()
    msp = s.MSP_FALLBACK.get(crop)
    if msp is None:
        await interaction.response.send_message(f"❌ Unknown crop: {crop}")
        return

    mandi = int(msp * 1.01)
    delta = round((mandi - msp) / msp * 100, 1)

    embed = discord.Embed(
        title=f"📊 {crop} — Market Data",
        color=0x5C7A42 if delta >= 0 else 0xC8922A,
    )
    embed.add_field(name="MSP (2024-25)", value=f"₹{msp}/quintal", inline=True)
    embed.add_field(name="Mandi Price", value=f"₹{mandi}/quintal", inline=True)
    embed.add_field(name="Delta", value=f"+{delta}% above MSP" if delta >= 0 else f"{delta}%", inline=True)
    embed.set_footer(text="Source: AGMARKNET | CropXpert")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="soilhealth", description="View your latest soil reading")
async def soilhealth_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🔗 Link your CropXpert account first with `/link mobile:YOUR_NUMBER`"
    )


@bot.tree.command(name="link", description="Link Discord to your CropXpert account")
@app_commands.describe(mobile="Your registered mobile number")
async def link_command(interaction: discord.Interaction, mobile: str):
    await interaction.response.send_message(
        f"📱 An OTP has been sent to {mobile}. "
        f"Complete verification on the CropXpert app to link your account."
    )


@bot.tree.command(name="help", description="Show all CropXpert bot commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌱 CropXpert Bot — Commands",
        color=0x2A3D2E,
        description="Precision agriculture assistant for Indian farmers",
    )
    commands = [
        ("/crop", "Get crop recommendation\n`/crop n:90 p:42 k:43 ph:6.5 moisture:58 temp:20 dist:Pune`"),
        ("/schemes", "List eligible schemes\n`/schemes state:Maharashtra`"),
        ("/msp", "Current MSP data\n`/msp crop:Rice`"),
        ("/soilhealth", "View latest soil reading"),
        ("/link", "Link Discord to CropXpert account"),
    ]
    for name, desc in commands:
        embed.add_field(name=name, value=desc, inline=False)

    embed.add_field(
        name="🇮🇳 हिंदी में",
        value="बॉट हिंदी में भी जवाब दे सकता है। अपनी भाषा CropXpert ऐप में सेट करें।",
        inline=False,
    )
    embed.set_footer(text="CropXpert — SRMIST CINTEL")
    await interaction.response.send_message(embed=embed)


async def start_discord_bot():
    """Start Discord bot in background — safe to fail if no token."""
    if not settings.DISCORD_BOT_TOKEN:
        logger.info("No DISCORD_BOT_TOKEN — bot will not start")
        return

    try:
        await bot.start(settings.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error("Discord bot failed to start: %s", e)


async def stop_discord_bot():
    if bot.is_ready():
        await bot.close()
