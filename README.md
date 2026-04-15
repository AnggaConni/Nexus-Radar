# 🎯 Nexus Radar
> **Catch the whispers before the storm.** 
> An autonomous AI-powered OSINT engine detecting latent environmental and societal anomalies before they escalate into global crises.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)]()
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Google%20Gemini-orange.svg)]()

![Nexus Radar Dashboard Preview](https://via.placeholder.com/1000x500.png?text=Nexus+Radar+Dashboard+Preview) *(Note: Replace with your actual screenshot)*

## 📖 The Vision: Why Weak Signals Matter
Traditional disaster management operates on a **reactive paradigm**—mobilizing resources only *after* a catastrophe strikes. However, crises are rarely sudden; they are preceded by subtle, creeping anomalies known as **Latent Signals** (e.g., a localized mass coral bleaching, a sudden drop in well water pressure, or isolated 'test burns' in a forest).

**Nexus Radar** defeats human cognitive biases (like Normalcy and Survivorship Bias) by autonomously scanning the web for these early indicators across 6 scientific domains:
🌊 **Ocean** | ☁️ **Climate** | 🌋 **DRR** | 💧 **Water** | 🌱 **Biodiversity** | 👥 **Social/Behavioral**

---

## ✨ Key Features
*   🤖 **Autonomous 5-Layer AI Pipeline:** Powered by Google Gemini, the engine automatically validates signals, extracts data, assesses catastrophe risks, and maps root causes.
*   🌍 **Geospatial Dashboard (`radar.html`):** An interactive UI built with TailwindCSS, Leaflet.js, and ECharts to visualize global threats and structural root causes.
*   🧠 **Automated Intelligence Synthesis:** Periodically generates a highly structured "Intelligence Resume" containing strategic recommendations and critical intervention targets.
*   ⚡ **Zero-Maintenance Automation:** Runs entirely on GitHub Actions via Cron Jobs. No dedicated backend server required.
*   📚 **Interactive Educational Hub (`info.html`):** A built-in SVG network diagram explaining the science and psychology behind ecological tipping points.

---

## 📂 Repository Structure
*   `scraper.py`: The Python core engine that performs web scraping and AI inference.
*   `.github/workflows/main.yml`: The GitHub Actions automation script.
*   `index.html`: The SEO-friendly SaaS Landing Page.
*   `radar.html`: The main Signal Inventory & Intelligence Dashboard.
*   `info.html`: The interactive Domain Analytics visualizer.
*   `data.json`: Append-only database storing all extracted latent signals.
*   `resume.json`: Periodic AI-generated synthesis reports.

---

## 🚀 How to Deploy (Free via GitHub)

You can run your own instance of Nexus Radar entirely for free using GitHub Actions and GitHub Pages.

### 1. Fork & Clone
Fork this repository to your own GitHub account.

### 2. Get API Key
Get a free API key from [Google AI Studio (Gemini)](https://aistudio.google.com/).

### 3. Set Up GitHub Secrets
1. Go to your repository **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name: `GEMINI_API_KEY`
4. Secret: *(Paste your Google Gemini API Key here)*

### 4. Enable GitHub Pages
1. Go to **Settings** > **Pages**.
2. Under "Build and deployment", set the source to **Deploy from a branch**.
3. Select the `main` branch and `/ (root)` folder, then save.
4. Your dashboard will be live at `https://[your-username].github.io/[repo-name]/`.

### 5. Trigger the First Run
1. Go to the **Actions** tab in your repository.
2. Select **Latent Signal Auto-Crawler** on the left.
3. Click **Run workflow**, choose `force_both` to generate your first batch of data and resume immediately.
4. From now on, the script will run automatically every day at midnight (UTC).

---

## ⚙️ Configuration (Environment Variables)
You can tweak the engine's behavior by modifying the variables in `.github/workflows/main.yml`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATA_INTERVAL_DAYS` | `1` | How often the engine searches for new signals (in days). |
| `RESUME_INTERVAL_DAYS` | `90` | How often the AI generates a new Quarterly Synthesis Report. |
| `MAX_ITEMS_PER_RUN` | `2` | Maximum number of new signals to append to the database per run. |
| `GEMINI_MODEL` | `gemini-3-flash-preview` | The specific Gemini LLM model to use. |

---

## ⚠️ Disclaimer
This tool utilizes Large Language Models (LLMs) to synthesize data from Open-Source Intelligence (OSINT). While the engine is instructed to seek verified sources, AI outputs can occasionally produce hallucinations or misinterpret data. **This tool is for research, educational, and early-warning screening purposes only** and should not replace professional ground-truth scientific assessments.

---

## ⚖️ License (AGPL v3.0)
This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

You are free to use, modify, and distribute this software. However, if you modify the code and provide it as a service over a network (like a web dashboard), you **must** make the modified source code available to your users under the same AGPL license.

See the [LICENSE](LICENSE) file for more details.

---
*Built to map the invisible. Designed for the future of our planet.* 🌍
