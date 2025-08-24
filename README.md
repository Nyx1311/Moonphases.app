 Moonphases.app 🌙

# 🌙 Moonphases.app  

An interactive **Streamlit** application to explore the **moon’s phases, zodiac signs, Hindu lunar calendar**, and the **mythological stories** that connect humanity to the cosmos.  

This project began as an experiment with **3D visualization in Streamlit** using a GLB model of the Moon, and grew into a cultural + astronomical exploration tool.  

---

## ✨ Features  

- 🌓 **Lunar Phase Finder**  
  - Select any date and view the **moon’s face**, illumination %, age in days, and phase angle.  
  - Includes lunar phase images + a **3D interactive Moon model** (`moon.glb`) that rotates based on the selected phase.  

- ♈ **Zodiac Signs**  
  - Choose a date and discover its corresponding **zodiac sign (Rashi)**.  
  - Displays ruling planet, element, Hindu/English name, symbol, and descriptive personality traits.  

- 📅 **Hindu Lunar Calendar**  
  - Calculate and display **Nakshatra**, **Rashi**, **Tithi**, **Paksha**, **Yoga**, **Karana**, **Vara (weekday)**, and **Season** for any chosen date.  

- 🌸 **Moon & Menstrual Cycle**  
  - Toggle to explore the connection between **lunar phases** and the **menstrual cycle**, blending cultural traditions and scientific insights.  

- 🕯️ **Lunar Myths & Legends**  
  - Discover stories of **Chandra** (Hindu moon god) and **Selene** (Greek moon goddess).  
  - Learn how moon deities, cycles, and myths connect across cultures.  

---

## ⚙️ How It Works  

1. **Streamlit UI** – Built with [Streamlit](https://streamlit.io/) for an interactive web app experience.  
2. **3D Moon Model** – Uses Google’s `<model-viewer>` web component to render a GLB 3D moon (`moon.glb`).  
3. **Astronomical Calculations** –  
   - Moon phase age, illumination, and angle are computed using astronomical formulas.  
   - Hindu calendar elements (Nakshatra, Tithi, Rashi, etc.) are calculated using approximations based on sidereal and lunar cycles.  
4. **Toggles** –  
   - `Zodiac Signs` → Show zodiac insights.  
   - `Moon & Menstrual Cycle` → Explore cultural and scientific links.  
   - `Lunar Myths` → Read about lunar deities and legends.  
   - `Hindu Lunar Calendar` → View detailed panchang elements.  

---

## 📸 Screenshots  

_Add images here once you push them (e.g., screenshots of the app interface, zodiac card, 3D moon)._  

---

## 🛠️ Requirements  

- Python 3.8+  
- Streamlit  
- BeautifulSoup4  

Install dependencies:  
```bash
pip install streamlit beautifulsoup4
