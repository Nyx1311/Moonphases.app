import streamlit as st
import math
import os
import base64
import re
from datetime import date
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Lunar Phases Astro Calendar", layout="wide")

# ---------------------------
# Session state defaults
# ---------------------------
if 'show_zodiac' not in st.session_state:
    st.session_state.show_zodiac = False
if 'show_sign_mover' not in st.session_state:
    st.session_state.show_sign_mover = False
if 'show_menstrual' not in st.session_state:
    st.session_state.show_menstrual = False
if 'show_myths' not in st.session_state:
    st.session_state.show_myths = False
if 'birth_date' not in st.session_state:
    st.session_state.birth_date = date.today()
if 'hindu_date' not in st.session_state:
    st.session_state.hindu_date = date.today()
if 'sign_index' not in st.session_state:
    st.session_state.sign_index = 0
if 'zodiac_date' not in st.session_state:
    st.session_state.zodiac_date = date.today()

# ---------------------------
# Constants / resources
# ---------------------------
GLB_FILENAME = "moon.glb"
IMAGE_FILES = {
    "new_moon": "new_moon.png",
    "waxing_crescent": "waxing_crescent.png",
    "first_quarter": "first_quater.png",
    "waxing_gibbous": "waxing_gibbous.png",
    "full_moon": "full_moon.png",
    "waning_gibbous": "waning_gibbous.png",
    "third_quarter": "third_quarter.png",
    "waning_crescent": "waning_crescent.png"
}
SYNODIC_MONTH = 29.53058867

# ---------------------------
# CSS styling
# ---------------------------
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #0a0a0a;
        color: #e8d5ff;
        background-image: url('https://www.transparenttextures.com/patterns/stardust.png');
        background-attachment: fixed;
    }
    .title {
        font-style: italic;
        font-weight: bold;
        font-size: 3.5rem;
        text-align: center;
        color: white;
        text-shadow: 0 0 10px white, 0 0 20px white;
        margin: 20px 0;
        position: relative;
        font-family: 'Lucida Calligraphy', cursive;
    }
    .stars {
        position: relative;
        height: 30px;
        margin: -20px 0 20px;
    }
    .star {
        position: absolute;
        color: #ffd700;
        font-size: 1.5rem;
        animation: twinkle 2s infinite alternate;
    }
    @keyframes twinkle {
        0% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    .glass {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(6px);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 14px;
        margin: 12px 0;
    }
    .section-header {
        font-size: 1.6rem;
        font-weight: bold;
        color: #ff6ec7;
        margin-bottom: 10px;
        text-align: center;
        font-family: 'Lucida Calligraphy', cursive;
        font-style: italic;
    }
    .zodiac-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(6px);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 15px;
        margin: 10px;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .zodiac-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(255, 110, 199, 0.2);
    }
    .zodiac-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #ff6ec7;
        margin-bottom: 10px;
        text-align: center;
        font-family: 'Lucida Calligraphy', cursive;
        font-style: italic;
    }
    .zodiac-description {
        font-size: 0.9rem;
        line-height: 1.4;
        text-align: justify;
        margin-top: 10px;
    }
    .calendar-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 15px 0;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: rgba(0, 0, 0, 0.8);
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.9rem;
    }
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    .read-more {
        color: #ff6ec7;
        font-style: italic;
        text-decoration: underline;
    }
    .full-width {
        width: 100%;
    }
    .no-border {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Decorative stars helper
# ---------------------------
def render_stars():
    stars_html = """
    <div class="stars">
        <span class="star" style="left: 10%;">⭐</span>
        <span class="star" style="left: 35%; animation-delay: 0.4s;">⭐</span>
        <span class="star" style="left: 60%; animation-delay: 0.8s;">⭐</span>
        <span class="star" style="left: 85%; animation-delay: 1.2s;">⭐</span>
    </div>
    """
    st.markdown(stars_html, unsafe_allow_html=True)

# ---------------------------
# HTML content
# ---------------------------
MYTHS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lunar Deities: Chandra and Selene</title>
<style>
body {
background-color: #1a1a2e;
color: #e6e6fa;
font-family: 'Arial', sans-serif;
margin: 0;
padding: 20px;
background-image: url('https://www.transparenttextures.com/patterns/stardust.png');
background-attachment: fixed;
}
.container {
max-width: 1200px;
margin: 0 auto;
text-align: center;
}
h1 {
font-size: 2.8em;
font-style: italic;
color: #c0c0ff;
margin-bottom: 30px;
}
h2 {
font-size: 2em;
font-style: italic;
color: #b0b0ff;
margin-top: 50px;
}
h3 {
font-size: 1.5em;
font-style: italic;
color: #a0a0ff;
margin-top: 30px;
}
.myth-section {
margin: 40px 0;
padding: 20px;
background-color: rgba(0, 0, 0, 0.5);
border-radius: 10px;
box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}
img {
max-width: 100%;
height: auto;
border: 2px solid #c0c0ff;
border-radius: 8px;
margin: 15px 0;
}
p {
line-height: 1.6;
font-size: 1.1em;
margin: 10px 20px;
text-align: justify;
}
@media (max-width: 768px) {
h1 { font-size: 2.2em; }
h2 { font-size: 1.6em; }
h3 { font-size: 1.3em; }
img { max-width: 90%; }
p { margin: 10px; }
}
</style>
</head>
<body>
<div class="container">
<h1>The Celestial Dance of Lunar Deities</h1>
<div class="myth-section">
<h2>Chandra: The Moon God of Hindu Mythology</h2>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/3.jpg" alt="Chandra in his chariot">
<p>In the vast tapestry of Hindu mythology, Chandra emerges as the radiant lunar deity, born during the cosmic *Samudra Manthan*—the churning of the ocean of milk. As the waves frothed and sparkled, Chandra rose alongside divine treasures like nectar and celestial beings, his silvery light destined to soothe the world. He rides a majestic chariot across the night sky, pulled by ten white horses, their hooves silent against the starry expanse. Chandra governs the tides, the mind, and the heart, embodying emotions and fertility. Poets and sages revere him, for his glow inspires dreams and marks the rhythm of life itself.</p>
<h3>The 27 Nakshatras and Rohini's Allure</h3>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/1.jpg" alt="Chandra and Rohini">
<p>Chandra's heart belongs to the 27 daughters of Daksha, the Nakshatras—celestial maidens representing the lunar mansions that guide astrologers and navigators. Among them, Rohini, the "red one," captures his deepest affection. When Chandra lingers in her constellation, the moon glows with a warm, rosy brilliance, casting enchantment over the earth. The other Nakshatras, envious of Rohini's favor, appealed to Daksha, who cursed Chandra to wane, explaining the moon's cyclical phases. Through penance, Chandra regained his light, forever waxing and waning in a dance of cosmic balance.</p>
</div>
<div class="myth-section">
<h2>Selene: The Moon Goddess of Greek Mythology</h2>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/3.jpg" alt="Selene in her chariot">
<p>In the luminous myths of ancient Greece, Selene reigns as the goddess of the moon, her silver chariot drawn by two winged horses trailing stardust across the heavens. As the sister of Helios, the sun god, and Eos, the dawn, Selene is the night's radiant queen, her ethereal beauty a beacon in the darkness. Her light commands the tides and stirs the dreams of mortals, her presence a quiet symphony of celestial grace.</p>
<h3>Endymion's Eternal Sleep and the Lunar Phases</h3>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/2.jpg" alt="Selene and Endymion">
<p>Selene's heart was captured by Endymion, a mortal shepherd of divine beauty. Unable to bear his mortality, she beseeched Zeus to grant him eternal life. Zeus placed Endymion in an eternal sleep in a cave on Mount Latmos, preserving his youthful perfection. Night after night, Selene descends to bathe him in her silvery light, their love a poignant blend of longing and eternity. The Greeks wove the moon's phases into her tale: pursued by her brother Helios, Selene flees across the sky, her light waning to a crescent before vanishing, only to be reborn in a cycle of renewal.</p>
</div>
</div>
</body>
</html>
"""

MENSTRUAL_HTML = """ 
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lunar Phases and the Menstrual Cycle</title>
<style>
body {
background-color: #1a1a2e;
background-image: url('file:///C:/Users/neelu/OneDrive/Desktop/luna/women.jpg');
background-size: cover;
background-attachment: fixed;
background-position: center;
color: #e6e6fa;
font-family: 'Arial', sans-serif;
margin: 0;
padding: 20px;
}
.container {
max-width: 1200px;
margin: 0 auto;
text-align: center;
background-color: rgba(0, 0, 0, 0.6);
border-radius: 10px;
padding: 20px;
}
h1 {
font-size: 2.8em;
font-style: italic;
color: #c0c0ff;
margin-bottom: 30px;
}
h2 {
font-size: 2em;
font-style: italic;
color: #b0b0ff;
margin-top: 50px;
}
.section {
margin: 40px 0;
padding: 20px;
background-color: rgba(0, 0, 0, 0.5);
border-radius: 10px;
box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}
img {
max-width: 100%;
height: auto;
border: 2px solid #c0c0ff;
border-radius: 8px;
margin: 15px 0;
}
p {
line-height: 1.6;
font-size: 1.1em;
margin: 10px 20px;
text-align: justify;
}
@media (max-width: 768px) {
h1 { font-size: 2.2em; }
h2 { font-size: 1.6em; }
img { max-width: 90%; }
p { margin: 10px; }
.container { padding: 10px; }
}
</style>
</head>
<body>
<div class="container">
<h1>The Cosmic Rhythm: Lunar Phases and the Menstrual Cycle</h1>
<div class="section">
<h2>Historical and Cultural Connections</h2>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/LM.jpg" alt="Lunar Goddess and Menstrual Cycle">
<p>Across ancient civilizations, the moon's rhythm has been a mirror to the cycles of life, none more profound than the menstrual cycle. Spanning roughly 28 days, the menstrual cycle aligns closely with the lunar cycle of 29.5 days, a harmony that inspired myths and rituals. Lunar goddesses like Selene in Greek mythology and Chandra's consorts, the Nakshatras, in Hindu tradition were revered as embodiments of fertility and renewal. In ancient cultures, menstruation was seen as a sacred connection to the moon, with full moon rituals celebrating fertility and creation. These beliefs wove the lunar phases into the fabric of human experience, from lunar calendars guiding agricultural and reproductive cycles to ceremonies honoring the divine feminine under the moon's glow.</p>
</div>
<div class="section">
<h2>Scientific Perspective</h2>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/LL.jpg" alt="Lunar Phases and Science">
<p>Modern science explores the lunar-menstrual connection with cautious curiosity. While definitive evidence remains elusive, studies suggest intriguing links. Moonlight may influence melatonin levels, a hormone regulating sleep and reproductive cycles, potentially affecting ovulation. Some research indicates that a subset of women may synchronize their menstrual cycles with lunar phases, with ovulation rates peaking around the full moon. These findings echo ancient observations, though scientists emphasize that individual cycles vary widely due to genetics, environment, and lifestyle. The moon's gravitational pull, while subtle compared to its effect on tides, may exert a faint influence on biological rhythms, a hypothesis that continues to spark research and debate.</p>
</div>
<div class="section">
<h2>Cultural Beliefs and Practices</h2>
<img src="file:///C:/Users/neelu/OneDrive/Desktop/luna/LLI.jpg" alt="Lunar Rituals">
<p>In many traditions, the moon's phases guide life's rhythms. Ancient societies associated menstruation with lunar goddesses, viewing it as a sacred cycle of renewal. Some cultures aligned activities with lunar phases—planting seeds or performing rituals during the waxing moon for growth, and resting or reflecting during the waning moon. Full moon ceremonies, from fertility dances in ancient Greece to meditative gatherings in indigenous traditions, celebrate the moon's peak as a time of creation and abundance. Even today, some communities honor these cycles, using lunar calendars to time rituals or personal practices, connecting the body's rhythms to the cosmos.</p>
</div>
</div>
</body>
</html>
"""

# ---------------------------
# HTML helpers
# ---------------------------
def process_html_content(html_content: str) -> str:
    """Extract body content and convert local file:/// image paths to data URIs."""
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.find('body')
    if body:
        body_content = ''.join(str(child) for child in body.children)
    else:
        body_content = html_content
    # Find file:/// references and replace with base64 data URIs if files exist
    pattern = r'src="file:///(.*?)"'
    matches = re.findall(pattern, body_content)
    for match in matches:
        # Convert match into OS path
        file_path = match.replace('/', '\\') if os.name == 'nt' else match
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()
            ext = os.path.splitext(file_path)[1][1:].lower()
            if ext == 'jpg':
                ext = 'jpeg'
            data_uri = f"data:image/{ext};base64,{encoded}"
            body_content = body_content.replace(f'src="file:///{match}"', f'src="{data_uri}"')
    return body_content

# ---------------------------
# Moon phase calculation
# ---------------------------
def moon_phase(date_obj: date):
    year, month, day = date_obj.year, date_obj.month, date_obj.day
    y = year
    m = month
    d = day
    if m < 3:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5
    days_since_new = jd - 2451550.1
    new_moons = days_since_new / SYNODIC_MONTH
    fraction = new_moons - int(new_moons)
    age = fraction * SYNODIC_MONTH
    if age < 0:
        age += SYNODIC_MONTH
    illumination = (1 - math.cos(2 * math.pi * age / SYNODIC_MONTH)) / 2 * 100
    phase_angle = (age / SYNODIC_MONTH) * 360.0
    return {
        "age": round(age, 2),
        "illumination": round(illumination, 1),
        "phase_angle": round(phase_angle, 2)
    }

def get_phase_image_filename(age_days):
    if age_days < 1:
        key = "new_moon"
    elif age_days < 7.4:
        key = "waxing_crescent"
    elif age_days < 8.9:
        key = "first_quarter"
    elif age_days < 14.8:
        key = "waxing_gibbous"
    elif age_days < 15.8:
        key = "full_moon"
    elif age_days < 21.1:
        key = "waning_gibbous"
    elif age_days < 22.1:
        key = "third_quarter"
    elif age_days < 28.0:
        key = "waning_crescent"
    else:
        key = "new_moon"
    return IMAGE_FILES.get(key)

# ---------------------------
# Load GLB as base64
# ---------------------------
def load_glb_as_base64(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"GLB file not found: {file_path}")
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ---------------------------
# Hindu Calendar Data
# ---------------------------
nakshatras = [
    {"name": "Ashwini", "ruler": "Ketu", "element": "Earth", "symbol": "Horse's Head"},
    {"name": "Bharani", "ruler": "Venus", "element": "Earth", "symbol": "Yoni"},
    {"name": "Krittika", "ruler": "Sun", "element": "Fire", "symbol": "Razor"},
    {"name": "Rohini", "ruler": "Moon", "element": "Earth", "symbol": "Bull's Cart"},
    {"name": "Mrigashira", "ruler": "Mars", "element": "Earth", "symbol": "Deer's Head"},
    {"name": "Ardra", "ruler": "Rahu", "element": "Water", "symbol": "Teardrop"},
    {"name": "Punarvasu", "ruler": "Jupiter", "element": "Water", "symbol": "Quiver of Arrows"},
    {"name": "Pushya", "ruler": "Saturn", "element": "Water", "symbol": "Flower"},
    {"name": "Ashlesha", "ruler": "Mercury", "element": "Water", "symbol": "Serpent"},
    {"name": "Magha", "ruler": "Ketu", "element": "Water", "symbol": "Throne"},
    {"name": "Purva Phalguni", "ruler": "Venus", "element": "Water", "symbol": "Front Legs of Bed"},
    {"name": "Uttara Phalguni", "ruler": "Sun", "element": "Fire", "symbol": "Back Legs of Bed"},
    {"name": "Hasta", "ruler": "Moon", "element": "Earth", "symbol": "Hand"},
    {"name": "Chitra", "ruler": "Mars", "element": "Fire", "symbol": "Pearl"},
    {"name": "Swati", "ruler": "Rahu", "element": "Fire", "symbol": "Young Shoot of Plant"},
    {"name": "Vishakha", "ruler": "Jupiter", "element": "Fire", "symbol": "Triumphal Gateway"},
    {"name": "Anuradha", "ruler": "Saturn", "element": "Fire", "symbol": "Lotus"},
    {"name": "Jyeshtha", "ruler": "Mercury", "element": "Air", "symbol": "Circular Amulet"},
    {"name": "Mula", "ruler": "Ketu", "element": "Air", "symbol": "Bunch of Roots"},
    {"name": "Purva Ashadha", "ruler": "Venus", "element": "Air", "symbol": "Winnowing Basket"},
    {"name": "Uttara Ashadha", "ruler": "Sun", "element": "Air", "symbol": "Elephant's Tusk"},
    {"name": "Shravana", "ruler": "Moon", "element": "Air", "symbol": "Ear"},
    {"name": "Dhanishtha", "ruler": "Mars", "element": "Ether", "symbol": "Musical Drum"},
    {"name": "Shatabhisha", "ruler": "Rahu", "element": "Ether", "symbol": "Empty Circle"},
    {"name": "Purva Bhadrapada", "ruler": "Jupiter", "element": "Ether", "symbol": "Swords"},
    {"name": "Uttara Bhadrapada", "ruler": "Saturn", "element": "Ether", "symbol": "Twin"},
    {"name": "Revati", "ruler": "Mercury", "element": "Ether", "symbol": "Fish"}
]

rashis = [
    {"name": "Mesha", "english": "Aries", "ruler": "Mars", "element": "Fire", "symbol": "♈", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\Aries.jpg"},
    {"name": "Vrishabha", "english": "Taurus", "ruler": "Venus", "element": "Earth", "symbol": "♉", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\taurus.png"},
    {"name": "Mithuna", "english": "Gemini", "ruler": "Mercury", "element": "Air", "symbol": "♊", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\Gemini.jpg"},
    {"name": "Karka", "english": "Cancer", "ruler": "Moon", "element": "Water", "symbol": "♋", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\Cancer.png"},
    {"name": "Simha", "english": "Leo", "ruler": "Sun", "element": "Fire", "symbol": "♌", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\Leo.png"},
    {"name": "Kanya", "english": "Virgo", "ruler": "Mercury", "element": "Earth", "symbol": "♍", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\virgo.png"},
    {"name": "Tula", "english": "Libra", "ruler": "Venus", "element": "Air", "symbol": "♎", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\libra.png"},
    {"name": "Vrishchika", "english": "Scorpio", "ruler": "Mars", "element": "Water", "symbol": "♏", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\scorpio.jpg"},
    {"name": "Dhanus", "english": "Sagittarius", "ruler": "Jupiter", "element": "Fire", "symbol": "♐", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\sagittarius.jpg"},
    {"name": "Makara", "english": "Capricorn", "ruler": "Saturn", "element": "Earth", "symbol": "♑", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\capricon.png"},
    {"name": "Kumbha", "english": "Aquarius", "ruler": "Saturn", "element": "Air", "symbol": "♒", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\Aqairus.jpg"},
    {"name": "Meena", "english": "Pisces", "ruler": "Jupiter", "element": "Water", "symbol": "♓", "image": "C:\\Users\\neelu\\OneDrive\\Desktop\\luna\\Pieces.jpg"}
]

tithi_names = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

# Zodiac descriptions
zodiac_descriptions = {
    "Aries": "Aries bursts onto the cosmic stage like a comet tearing through the void, its crimson trail igniting the night. A warrior born of fire, Aries embodies raw courage and unyielding ambition, their heart a furnace that fuels daring quests. They charge into life's battles with fearless abandon, their spirit untamed, their eyes alight with the thrill of conquest. Impulsive and bold, they are the spark of creation, the first breath of spring, forging paths where none dare tread. Yet, their fiery temper can flare like a supernova. Aries is the leader who carves destiny with a blade of passion, forever chasing the horizon of endless possibility.",
    "Taurus": "Taurus stands as an ancient oak rooted deep in the earth's core, its branches cradling the stars. Steadfast and sensual, they are the guardians of stability, their presence a sanctuary amidst the cosmos's chaos. Taurus delights in life's pleasures—velvet petals, rich feasts, and the soft glow of moonlight—savoring each moment like a sacred ritual. Their stubborn resolve is a mountain unmoved, yet their loyalty flows like a river, eternal and unwavering for those they hold dear. With quiet determination, Taurus builds empires of enduring beauty, their soul a tapestry of patience and strength, grounded in the heartbeat of the earth.",
    "Gemini": "Gemini flits through the heavens like a mischievous breeze, their words weaving tales that dance among the constellations. Quick-witted and versatile, they are the zodiac's communicators, their mind a kaleidoscope of ideas that shimmer like fireflies in a midnight sky. Gemini's duality is their magic—a twin spirit that shifts between light and shadow, curiosity and charm. They are the eternal seekers, chasing knowledge with restless grace, their laughter echoing through the cosmos. Yet, their fleeting nature can scatter their focus like stardust. Gemini is the storyteller who spins life's narrative, connecting the universe with threads of wit and wonder.",
    "Cancer": "Cancer emerges from the moon's silvery embrace, a guardian cloaked in the tides of emotion. Their heart is an ocean, deep and intuitive, reflecting the lunar phases that guide their soul. Nurturing and protective, they weave a cocoon of love for their chosen ones, their empathy a beacon in the night. Cancer's sensitivity is their strength, feeling the world's joys and sorrows as if they were their own. Yet, like the moon, they can retreat into their shell, guarding their tender core. They are the keepers of memory, their home a sacred haven where the heart finds solace under the celestial glow.",
    "Leo": "Leo strides across the heavens like a lion bathed in sunlight, their mane ablaze with regal fire. Charismatic and bold, they are the zodiac's kings and queens, commanding attention with a radiant presence that outshines the stars. Leo's heart burns with passion and creativity, their confidence a crown forged in the furnace of self-belief. They thrive in the spotlight, weaving drama and warmth into every moment, yet their pride can roar like a tempest. Generous and loyal, Leo rules with a heart of gold, inspiring others to bask in their light, a sovereign whose kingdom is built on love and courage.",
    "Virgo": "Virgo moves through the cosmos with the precision of a master craftsman, their hands shaping order from chaos. Analytical and meticulous, they are the zodiac's artisans, their mind a constellation of details aligned in perfect harmony. Virgo's devotion to service is their art, tending to the world with quiet grace and unwavering diligence. Their pursuit of perfection is a pilgrimage, yet their self-criticism can cast shadows on their brilliance. Practical and nurturing, Virgo is the healer who mends the universe's fractures, their soul a garden where wisdom and kindness bloom under starlight.",
    "Libra": "Libra glides through the heavens like a celestial dancer, their steps weaving balance into the cosmic waltz. Charmed by beauty and diplomacy, they are the zodiac's peacemakers, their heart a scale that seeks harmony in every encounter. Libra's elegance is their magic, turning conflict into art with a smile that rivals the dawn. They crave connection, their soul alight with the pursuit of love and justice, yet indecision can sway their delicate balance. Refined and gracious, Libra is the muse who paints the universe with colors of fairness, their presence a symphony of grace under the stars.",
    "Scorpio": "Scorpio slinks through the cosmos like a phantom, their eyes piercing the veil of the universe's secrets. Intense and enigmatic, they are the zodiac's alchemists, transforming pain into power with a will as unyielding as obsidian. Scorpio's passion burns like a hidden flame, their loyalty fierce and their intuition a compass through the shadows. They embrace life's depths, unafraid of its mysteries, yet their secrecy can cloak their heart in darkness. With magnetic allure, Scorpio is the sorcerer who reshapes destiny, their soul a crucible where transformation ignites under the moon's gaze.",
    "Sagittarius": "Sagittarius gallops across the heavens like an archer astride a comet, their arrow aimed at the farthest stars. Adventurous and free-spirited, they are the zodiac's explorers, their heart a map of uncharted horizons. Sagittarius seeks truth with a philosopher's zeal, their optimism a flame that lights even the darkest paths. Their restless spirit chases freedom, yet their bluntness can sting like an arrow's tip. With boundless curiosity, Sagittarius is the wanderer who roams the cosmos, their laughter a beacon that inspires others to dream beyond the constellations.",
    "Capricorn": "Capricorn climbs the celestial peaks like a goat scaling the cliffs of eternity, their gaze fixed on the summit of ambition. Disciplined and resolute, they are the zodiac's architects, building legacies with the patience of stone. Capricorn's pragmatism is their crown, their work ethic a foundation that withstands time's tides. They carry the weight of responsibility with stoic grace, yet their guarded heart can feel the chill of isolation. With unwavering determination, Capricorn is the sovereign who carves empires from the cosmos, their soul a monument to enduring strength.",
    "Aquarius": "Aquarius soars through the heavens like a starship, their mind a galaxy of revolutionary ideas. Eccentric and altruistic, they are the zodiac's visionaries, their heart pulsing with dreams of a better world. Aquarius wields intellect like a lightning bolt, their independence a rebellion against the mundane. They champion humanity with unwavering ideals, yet their detachment can cast them adrift in the cosmos. With a spirit that defies convention, Aquarius is the innovator who reshapes the stars, their vision a constellation of hope and progress.",
    "Pisces": "Pisces drifts through the cosmos like a shimmering tide, their soul an ocean of dreams and intuition. Compassionate and ethereal, they are the zodiac's mystics, their heart attuned to the universe's unspoken melodies. Pisces weaves empathy into every connection, their imagination a canvas where reality and fantasy blur. They feel the world's currents deeply, yet their sensitivity can pull them into the depths. With boundless creativity, Pisces is the dreamer who sails the celestial seas, their spirit a lighthouse guiding lost souls through the cosmic mist."
}

# ------------------------
# Hindu Calendar Calculations
# ------------------------
def calculate_nakshatra(date_obj):
    epoch_start = date(1900, 1, 1)
    days_since_epoch = (date_obj - epoch_start).days
    moon_cycle = 27.321661
    nakshatra_position = (days_since_epoch % moon_cycle) / moon_cycle * 27
    return int(nakshatra_position) % 27

def calculate_rashi(date_obj):
    year = date_obj.year
    day_of_year = (date_obj - date(year, 1, 1)).days
    ayanamsa = 24.1  # degrees, approximate for current epoch
    tropical_longitude = (day_of_year / 365.25) * 360
    sidereal_longitude = (tropical_longitude - ayanamsa + 360) % 360
    return int(sidereal_longitude / 30) % 12

def calculate_tithi(date_obj):
    new_moon = date(2000, 1, 6)  # Reference new moon
    days_since_new_moon = (date_obj - new_moon).days
    lunar_month = 29.530588853
    tithi_position = (days_since_new_moon % lunar_month) / lunar_month * 30
    return int(tithi_position) % 30

def get_vara(date_obj):
    days = ["Ravivaar", "Somvaar", "Mangalvaar", "Budhvaar", "Guruvaar", "Shukravaar", "Shanivaar"]
    return days[date_obj.weekday()]

def calculate_yoga(date_obj):
    yogas = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarman", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva",
        "Vyaghata", "Harshana", "Vajra", "Siddha", "Vyatipata", "Variyan",
        "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
        "Brahma", "Indra", "Vaidhriti"
    ]
    day_of_year = (date_obj - date(date_obj.year, 1, 1)).days
    return yogas[day_of_year % 27]

def calculate_karana(tithi):
    karanas = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanij", "Vishti"]
    return karanas[int(tithi / 2) % 7]

def get_season(date_obj):
    month = date_obj.month
    if 3 <= month <= 6:
        return "Vasant (Spring)"
    elif 7 <= month <= 10:
        return "Grishma (Summer)"
    else:
        return "Shishir (Winter)"

# ------------------------
# Load resources
# ------------------------
glb_exists = os.path.exists(GLB_FILENAME)
moon_model_data = load_glb_as_base64(GLB_FILENAME) if glb_exists else None

# ------------------------
# Main App
# ---------------------------
def main():
    # Title and decorative elements
    st.markdown('<div class="title">Lunar Phases Astro Calendar</div>', unsafe_allow_html=True)
    render_stars()
    
    # Always visible sections - Lunar Phase Finder and 3D Model
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Lunar Phase Finder (always visible)
        with st.container():
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">Lunar Phase Finder</h2>', unsafe_allow_html=True)
            
            selected_date = st.date_input(
                "Select a date",
                value=date.today(),
                min_value=date(1900, 1, 1),
                max_value=date(2100, 12, 31)
            )
            
            moon_data = moon_phase(selected_date)
            
            # Display moon phase information
            st.markdown("### *Lunar Phase Information*")
            st.markdown(f"*Date:* {selected_date}")
            st.markdown(f"*Moon age:* {moon_data['age']} days")
            st.markdown(f"*Illumination:* {moon_data['illumination']}%")
            st.markdown(f"*Phase angle:* {moon_data['phase_angle']}°")
            
            # Display moon phase image
            phase_filename = get_phase_image_filename(moon_data["age"])
            if phase_filename and os.path.exists(phase_filename):
                st.image(phase_filename, caption=f"*Phase: {phase_filename.replace('_', ' ').replace('.png', '').title()}*", width=300)
            else:
                st.error(f"Phase image not found: {phase_filename}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 3D Moon Model (always visible)
        with st.container():
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            
            if not glb_exists:
                st.error(f"3D model file not found: {GLB_FILENAME}")
            else:
                phase_angle = moon_data["phase_angle"]
                sun_x = math.cos(math.radians(phase_angle)) * 2.0
                sun_z = math.sin(math.radians(phase_angle)) * 2.0
                model_html = f"""
                <div style="width:100%; height:70vh; display:flex; align-items:center; justify-content:center; background-color:transparent;">
                <model-viewer 
                    src="data:model/gltf-binary;base64,{moon_model_data}"
                    alt="3D Moon"
                    style="width:100%; height:100%; background-color:transparent;"
                    shadow-intensity="1"
                    camera-controls
                    environment-image="neutral"
                    exposure="1.4"
                    auto-rotate="false"
                    rotation="0deg {phase_angle}deg 0deg"
                    scale="4 4 4">
                    <directional-light slot="scene" intensity="2" color="#ffffff" position="{sun_x} 0 {sun_z}"></directional-light>
                </model-viewer>
                </div>
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                """
                components.html(model_html, height=600)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Toggle sections
    st.markdown('<div class="section-header">Explore Lunar Knowledge</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        show_zodiac = st.checkbox("Zodiac Signs", st.session_state.show_zodiac)
        st.session_state.show_zodiac = show_zodiac
        
        show_menstrual = st.checkbox("Moon & Menstrual Cycle", st.session_state.show_menstrual)
        st.session_state.show_menstrual = show_menstrual
    
    with col2:
        show_myths = st.checkbox("Lunar Myths", st.session_state.show_myths)
        st.session_state.show_myths = show_myths
        
        show_sign_mover = st.checkbox("Hindu Lunar Calendar", st.session_state.show_sign_mover)
        st.session_state.show_sign_mover = show_sign_mover
    
    # Display sections based on toggles
    if st.session_state.show_zodiac:
        st.markdown('<div class="section-header">Zodiac Signs</div>', unsafe_allow_html=True)
        
        # Date selection for zodiac
        zodiac_date = st.date_input("Select date for Zodiac Sign", st.session_state.zodiac_date)
        st.session_state.zodiac_date = zodiac_date
        
        # Calculate zodiac sign based on date
        rashi_idx = calculate_rashi(zodiac_date)
        zodiac_data = rashis[rashi_idx]
        
        # Display zodiac information
        st.markdown(f'<div class="zodiac-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="zodiac-title">{zodiac_data["english"]} {zodiac_data["symbol"]}</div>', unsafe_allow_html=True)
        st.markdown(f"**Hindu Name:** {zodiac_data['name']}")
        st.markdown(f"**Ruler:** {zodiac_data['ruler']}")
        st.markdown(f"**Element:** {zodiac_data['element']}")
        if os.path.exists(zodiac_data['image']):
            st.image(zodiac_data['image'], width=300)
        st.markdown(f'<div class="zodiac-description">{zodiac_descriptions.get(zodiac_data["english"], "")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.show_menstrual:
        st.markdown('<div class="section-header">Moon & Menstrual Cycle</div>', unsafe_allow_html=True)
        processed_html = process_html_content(MENSTRUAL_HTML)
        st.markdown(processed_html, unsafe_allow_html=True)
    
    if st.session_state.show_myths:
        st.markdown('<div class="section-header">Lunar Myths</div>', unsafe_allow_html=True)
        processed_html = process_html_content(MYTHS_HTML)
        st.markdown(processed_html, unsafe_allow_html=True)
    
    if st.session_state.show_sign_mover:
        st.markdown('<div class="section-header">Hindu Lunar Calendar</div>', unsafe_allow_html=True)
        
        # Hindu Calendar section
        with st.container():
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">Hindu Lunar Calendar 🌙</h2>', unsafe_allow_html=True)
            st.markdown('<div class="tooltip">', unsafe_allow_html=True)
            st.markdown('<span class="read-more">read more</span>', unsafe_allow_html=True)
            st.markdown('<span class="tooltip-text"><strong>Nakshatra:</strong> 27 lunar mansions or star constellations in Vedic astronomy<br>Each Nakshatra spans 13°20\' and represents specific stellar influences on Earth</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Hindu Calendar controls
            st.markdown('<div class="calendar-controls">', unsafe_allow_html=True)
            hindu_date = st.date_input(
                "Select date",
                value=st.session_state.hindu_date,
                min_value=date(1900, 1, 1),
                max_value=date(2100, 12, 31),
                key="hinduDateInput"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Calendar", key="updateHinduBtn"):
                    st.session_state.hindu_date = hindu_date
            with col2:
                if st.button("Today", key="hinduTodayBtn"):
                    st.session_state.hindu_date = date.today()
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Calculate Hindu calendar data
            nakshatra_idx = calculate_nakshatra(st.session_state.hindu_date)
            rashi_idx = calculate_rashi(st.session_state.hindu_date)
            tithi_val = calculate_tithi(st.session_state.hindu_date)
            
            nakshatra_data = nakshatras[nakshatra_idx]
            rashi_data = rashis[rashi_idx]
            
            # Display Nakshatra information
            st.markdown("### *Nakshatra (Star Alignment) ⭐*")
            st.markdown(f"*Current Nakshatra:* <span id='hinduNakshatra'>{nakshatra_data['name']}</span>", unsafe_allow_html=True)
            st.markdown(f"*Ruling Planet:* <span id='hinduNakshatraRuler'>{nakshatra_data['ruler']}</span>", unsafe_allow_html=True)
            st.markdown(f"*Element:* <span id='hinduNakshatraElement'>{nakshatra_data['element']}</span>", unsafe_allow_html=True)
            st.markdown(f"*Symbol:* <span id='hinduNakshatraSymbol'>{nakshatra_data['symbol']}</span>", unsafe_allow_html=True)
            
            # Display Rashi information
            st.markdown("### *Rashi (Zodiac Sign) ♌*")
            st.markdown(f"*Current Rashi:* {rashi_data['name']} ({rashi_data['english']})")
            st.markdown(f"*Element:* {rashi_data['element']}")
            st.markdown(f"*Ruling Planet:* {rashi_data['ruler']}")
            
            # Display Tithi information
            st.markdown("### *Tithi (Lunar Day) 🌕*")
            tithi_day = (tithi_val % 15) + 1
            paksha = "Shukla Paksha" if tithi_val < 15 else "Krishna Paksha"
            tithi_name = tithi_names[min(tithi_day - 1, 14)]
            
            st.markdown(f"*Tithi:* {tithi_name}")
            st.markdown(f"*Paksha:* {paksha}")
            st.markdown(f"*Day:* {tithi_day}")
            
            # Display additional Hindu calendar information
            st.markdown("### *Additional Information*")
            st.markdown(f"*Vara (Day of Week):* {get_vara(st.session_state.hindu_date)}")
            st.markdown(f"*Yoga:* {calculate_yoga(st.session_state.hindu_date)}")
            st.markdown(f"*Karana:* {calculate_karana(tithi_val)}")
            st.markdown(f"*Season:* {get_season(st.session_state.hindu_date)}")
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()