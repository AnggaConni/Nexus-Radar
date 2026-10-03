"""
=======================================================================
  LATENT SIGNAL RADAR v2.2 — Global Early Warning Engine
  AI Engine : Google Gemini 2.5 Flash (Free Tier Optimized)
  Crawler   : DuckDuckGo Search (100% Free Python Wrapper)
  Mode      : Multi-Schedule Tracker (Data = 1 Day, Resume = 3 Months)
  Feature   : Pre-crisis Detection, Environmental & Societal Systems
=======================================================================
"""

import os
import json
import logging
import random
import hashlib
import time
import unicodedata
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
import requests
from ddgs import DDGS  # ✅ Tambahan baru untuk pencarian web gratis

# ── Logging Configuration ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("SignalRadar")

# ── File Paths ──
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
DATA_FILE        = os.path.join(BASE_DIR, "data.json")
RESUME_FILE      = os.path.join(BASE_DIR, "resume.json")
HISTORY_FILE     = os.path.join(BASE_DIR, "history.json")
PATHWAY_FILE     = os.path.join(BASE_DIR, "pathways.json")

# ── Konfigurasi Jadwal ──
DATA_INTERVAL_DAYS   = int(os.environ.get("DATA_INTERVAL_DAYS", 1))
RESUME_INTERVAL_DAYS = int(os.environ.get("RESUME_INTERVAL_DAYS", 90))
MAX_ITEMS_PER_RUN    = int(os.environ.get("MAX_ITEMS_PER_RUN", 2))

# ── Domain Keyword (DIPERSINGKAT UNTUK EFISIENSI) ──
KEYWORDS =[
    # --- Ocean ---
    "turtle entangled plastic debris local beach",
    "unusual coral bleaching observation early sign",
    "microplastic accumulation coastal fishing village",
    "mangrove die-off unexplained coastal erosion",
    "red tide algal bloom fishing community",
    "dead fish washed ashore sudden event",

    # --- DRR (Disaster Risk Reduction) ---
    "soil cracks early sign landslide village",
    "unusual river color muddy upstream warning",
    "ground subsidence local residential area",
    "animal migration sudden earthquake sign",
    "drying wells drought indicator local farming",
    "unusual water receding beach tsunami sign",

    # --- Climate ---
    "unusual flowering time indigenous local observation",
    "extreme localized heatwave emerging threat",
    "insect migration pattern shift farming disruption",
    "permafrost melting early sign local structure damage",
    "unseasonal frost destroying local crops",

    # --- Water ---
    "groundwater salinity increase coastal farming",
    "river drying up unexpected season",
    "toxic foam local river pollution sign",
    "lake water level dropping drastically",
    "heavy metal contamination suspicion well water",

    # --- Biodiversity ---
    "mass bird death unexplained local area",
    "invasive species spreading rapidly local forest",
    "amphibian disappearance local pond ecosystem",
    "bee colony collapse sudden local farm",
    "unusual wildlife entering human settlement",

    # --- Social/Behavioral ---
    "community informal waste dumping riverbank",
    "illegal sand mining escalating local river",
    "overfishing signs juvenile fish local market",
    "slash and burn farming early haze sign",
    "abandoned industrial waste local site",

    # --- Ocean (Tambahan) ---
    "unusual jellyfish bloom coastal waters",
    "thinning oyster shells local acidification sign",
    "seagrass meadow dieback unexplained",
    "invasive lionfish spotted new local reef",
    "coastal salt marsh degrading suddenly",
    "ocean temperature anomaly local fish catch drop",

    # --- DRR / Disaster Risk Reduction (Tambahan) ---
    "sulfur smell gas emission local volcano warning",
    "frequent micro-tremors felt by village",
    "glacial lake ice dam cracking early sign",
    "small sinkhole forming residential road",
    "rockfall frequency increasing steep mountain slope",
    "unusual silence of birds insects before storm",

    # --- Climate (Tambahan) ---
    "tree line shifting higher local mountain observation",
    "bears waking early hibernation anomaly",
    "prolonged dry spell in traditionally humid rainforest",
    "glacier retreating rapidly indigenous observation",
    "traditional local weather predicting failing",
    "unusual wind pattern shift disrupting local sailing",

    # --- Water (Tambahan) ---
    "cyanobacteria blue green algae local reservoir",
    "ancient artesian spring stopped flowing village",
    "strange odor in community well water",
    "micro seepage earthen dam wall warning",
    "saltwater pushing further inland local estuary",
    "sudden drop in local groundwater pressure",

    # --- Biodiversity (Tambahan) ---
    "apex predator missing from local forest ecosystem",
    "sudden rodent overpopulation destroying local crops",
    "unexplained wildlife disease outbreak local deer",
    "specific butterfly pollinator missing this season",
    "strange fungal infection killing native trees",
    "fish spawning grounds shifting location unexpectedly",

    # --- Social/Behavioral (Tambahan) ---
    "unregulated industrial groundwater pumping rural area",
    "new unauthorized logging road visible satellite",
    "critical wildlife corridor blocked by new settlement",
    "panic buying of water local market rumor",
    "local fishing fleet ignoring seasonal quotas",
    "rapid deforestation for informal mining camp",       # Social
]

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def load_json_file(filepath, default_val):
    if not os.path.exists(filepath): return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading {filepath}: {e}")
        return default_val

def save_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_json_safe(text):
    try:
        text = text.strip()
        tick3 = '`' * 3
        if text.startswith(tick3 + 'json'): text = text[7:]
        if text.startswith(tick3): text = text[3:]
        if text.endswith(tick3): text = text[:-3]
        text = text.strip()
        start_idx = text.find('{') if '{' in text else text.find('[')
        end_idx = text.rfind('}') if '}' in text else text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            return json.loads(text[start_idx:end_idx+1])
        return json.loads(text)
    except Exception as e:
        log.error(f"JSON Parse Error: {e}")
        return None

def normalize_title(title):
    return unicodedata.normalize("NFKC", title).strip().lower()

def clean_url(url):
    url = str(url).strip()
    if "google.com/url" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if 'q' in qs: return qs['q'][0]
        elif 'url' in qs: return qs['url'][0]
    return url

def get_coordinates(location_name):
    if not location_name or str(location_name).lower() == "unknown":
        return None, None
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
    headers = {"User-Agent": "SignalRadarApp/2.2 (research-bot)"}
    try:
        time.sleep(1.5)
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data: return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        log.warning(f"Geocoding failed for {location_name}: {e}")
    return None, None

def get_current_quarter():
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"Q{quarter} {now.year}"

# ✅ NEW: FUNGSI PENCARIAN WEB (GRATIS VIA DUCKDUCKGO)
def search_ddgs(query, max_results=5):
    """Search the web with DuckDuckGo. Failure is isolated from other providers."""
    results = []

    try:
        log.info(f"🦆 DDGS search: '{query}'")
        with DDGS() as ddgs:
            raw_results = ddgs.text(query, max_results=max_results)

            if raw_results:
                for r in raw_results:
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", "")
                    })

        log.info(f"🦆 DDGS returned {len(results)} results")

    except Exception as e:
        log.error(f"❌ DDGS search error: {e}")

    return results


def search_tinyfish(query, max_results=5):
    """
    Search the live web through TinyFish Search.

    TinyFish is optional: when TINYFISH_API_KEY is missing or the API fails,
    this function returns an empty list so DDGS can continue normally.
    """
    results = []
    api_key = os.environ.get("TINYFISH_API_KEY", "").strip()

    if not api_key:
        log.info("🐟 TinyFish disabled: TINYFISH_API_KEY not configured")
        return results

    try:
        log.info(f"🐟 TinyFish search: '{query}'")

        response = requests.get(
            "https://api.search.tinyfish.ai",
            params={
                "query": query,
                "page": 0
            },
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        for r in data.get("results", [])[:max_results]:
            if not isinstance(r, dict):
                continue

            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "url": r.get("url", "")
            })

        log.info(f"🐟 TinyFish returned {len(results)} results")

    except requests.exceptions.RequestException as e:
        log.warning(f"⚠️ TinyFish unavailable; continuing with DDGS: {e}")

    except (ValueError, TypeError, KeyError) as e:
        log.warning(f"⚠️ TinyFish returned unexpected data; continuing with DDGS: {e}")

    except Exception as e:
        # Never allow an optional search provider to stop the radar.
        log.warning(f"⚠️ TinyFish search error; continuing with DDGS: {e}")

    return results


def _dedupe_search_results(results):
    """Deduplicate by canonical URL, falling back to title when URL is absent."""
    deduped = []
    seen = set()

    for item in results:
        if not item:
            continue

        url = clean_url(item.get("url", ""))
        title = normalize_title(item.get("title", ""))

        if url:
            key = f"url:{url.lower()}"
        elif title:
            key = f"title:{title}"
        else:
            continue

        if key in seen:
            continue

        seen.add(key)

        item["url"] = url
        deduped.append(item)

    return deduped


def get_real_world_signals(keyword, max_results=5):
    """
    Multi-engine discovery layer.

    TinyFish and DDGS run in parallel. Their results are interleaved so one
    provider cannot completely dominate the candidate set. If one provider
    fails, the other provider's results are still returned. If both fail,
    the existing pipeline simply receives an empty list.
    """
    query = f"{keyword} news"
    log.info(f"🌐 Parallel web discovery: '{query}'")

    provider_results = {
        "tinyfish": [],
        "ddgs": []
    }

    # Run both search providers concurrently. This adds resilience without
    # adding a serial TinyFish -> DDGS delay.
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(search_tinyfish, query, max_results): "tinyfish",
            executor.submit(search_ddgs, query, max_results): "ddgs"
        }

        for future in as_completed(futures):
            provider = futures[future]

            try:
                provider_results[provider] = future.result()
            except Exception as e:
                log.warning(f"⚠️ {provider} worker failed: {e}")
                provider_results[provider] = []

    # Interleave providers to increase source diversity.
    merged = []
    for i in range(max_results):
        for provider in ("tinyfish", "ddgs"):
            items = provider_results.get(provider, [])
            if i < len(items):
                item = dict(items[i])
                item["search_provider"] = provider
                merged.append(item)

    merged = _dedupe_search_results(merged)
    merged = merged[:max_results]

    tinyfish_count = len(provider_results.get("tinyfish", []))
    ddgs_count = len(provider_results.get("ddgs", []))

    log.info(
        f"🔎 Discovery complete: TinyFish={tinyfish_count}, "
        f"DDGS={ddgs_count}, unique candidates={len(merged)}"
    )

    if not merged:
        log.warning("⚠️ No raw signals found from either search provider.")

    return merged

# =====================================================================
# CORE AI ENGINE (GEMINI 1.5 FLASH)
# =====================================================================

def call_gemini(api_key, prompt, system_instruction, expect_json=True):
    if not isinstance(prompt, str): prompt = json.dumps(prompt)
        
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")# ✅ Menggunakan model stabil & gratis
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    payload = {
        "contents":[{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts":[{"text": system_instruction}]},
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json" if expect_json else "text/plain"
        }
    }
        
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status() 
    
    try:
        data = response.json()
        raw_text = data.get("candidates",[{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        if expect_json: return extract_json_safe(raw_text)
        return raw_text
    except Exception as e:
        log.error(f"Gemini Data Parse Error: {e}")
        return None

def call_gemini_with_retry(api_key, prompt, system_instruction, retries=4, **kwargs):
    for attempt in range(retries):
        try:
            time.sleep(5) # Jeda aman 5 detik
            result = call_gemini(api_key, prompt, system_instruction, **kwargs)
            if result: return result
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else 500
            
            if status_code == 429:
                wait_time = 45 # Tidur 45 detik jika kena Rate Limit Google
                log.warning(f"⚠️ [429] Rate Limit Hit. Sleeping {wait_time}s... (Attempt {attempt+1}/{retries})")
                time.sleep(wait_time)
                continue
                
            if status_code in [400, 403, 404]: 
                log.error(f"Fatal API Error {status_code}: {e}")
                break
                
            log.error(f"HTTP Error {status_code}: {e}")
            
        except Exception as e:
            log.error(f"Unexpected Request Error: {e}")
            
        time.sleep(2 ** attempt)
        
    return None

# =====================================================================
# 4-LAYER PIPELINE (LATENT SIGNAL DISCOVERY)
# =====================================================================

def pass_1_validate(api_key, raw_content):
    sys_prompt = """Determine whether the following news snippet represents a real-world LATENT SIGNAL (early warning, anomaly, or creeping environmental/societal degradation). 
    CRITICAL RULES:
    - Must be a problem, risk, or degradation (NOT a solution).
    - Must NOT be a finalized historical disaster. Focus on early signs.
    Return exactly: {"is_signal": true/false, "confidence": 0.0-1.0}"""
    res = call_gemini_with_retry(api_key, raw_content, sys_prompt)
    return res if res else {"is_signal": False, "confidence": 0}

def pass_2_extract(api_key, raw_content):
    sys_prompt = """Extract structured data from this latent signal.
    CLASSIFICATION MUST BE ONE OF:[DRR, Ocean, Climate, Water, Biodiversity, Social/Behavioral].
    Return EXACTLY this JSON:
{"title": "", "summary": "", "domain_classification":[], "signal_intensity": "weak | moderate | strong", "location": {"country": "", "region": ""}, "manifestation": {"how_it_is_observed": "", "key_indicators":[]}, "potential_impact": {"threat_level": "low | medium | high", "affected_elements":[]}, "escalation": {"speed": "slow | medium | fast", "urgency": "low | medium | high"}}"""
    return call_gemini_with_retry(api_key, raw_content, sys_prompt)

def pass_3_risk(api_key, raw_content):
    sys_prompt = """Analyze this latent signal and assess potential disaster risks if left unaddressed. Return EXACTLY this JSON:
{"risk_score": <int 1-10>, "risk_type": ["type1"], "severity_level": "low|medium|high", "needs_immediate_intervention": true/false, "explanation": ""}"""
    return call_gemini_with_retry(api_key, raw_content, sys_prompt)

def pass_4_lineage(api_key, raw_content):
    sys_prompt = """Determine the underlying root cause. Options:[anthropogenic, systemic_failure, natural_anomaly, policy_gap, behavioral_neglect]. Return EXACTLY this JSON: {"root_cause": ["cause1"]}"""
    return call_gemini_with_retry(api_key, raw_content, sys_prompt)

def calculate_advanced_metrics(data):
    try:
        threat_map = {"high": 10, "medium": 6, "low": 2, "unknown": 0}
        urgency_map = {"high": 10, "medium": 5, "low": 2, "unknown": 0}
        
        threat_val = threat_map.get(str(data.get("potential_impact", {}).get("threat_level", "")).lower(), 0)
        urgency_val = urgency_map.get(str(data.get("escalation", {}).get("urgency", "")).lower(), 0)
        risk_val = data.get("risk_assessment", {}).get("risk_score", 1)

        priority_score = int(((threat_val * 0.4) + (risk_val * 0.4) + (urgency_val * 0.2)) * 10)
        data["priority_score"] = min(100, max(0, priority_score))

        has_critical = any(k in t.lower() for t in data.get("risk_assessment", {}).get("risk_type",[]) for k in["fatal", "extinction", "catastrophe"])
        data["critical_flag"] = bool(risk_val >= 8 and has_critical)
        return data
    except Exception:
        return data


# =====================================================================
# SIGNAL PATHWAY CLASSIFICATION
# =====================================================================

def normalize_pathway_text(value):
    return " ".join(
        unicodedata.normalize("NFKC", str(value or ""))
        .lower()
        .replace("&", " and ")
        .split()
    )


def classify_signal_pathway(item, taxonomy):
    """
    Map one latent-signal record onto the controlled Signal Pathway taxonomy.

    Mapping is deliberately auditable:
    - evidence_linked: explicit domain / manifestation / impact / risk evidence
    - heuristic: title / summary / root-cause language
    """
    matches = []
    domains = taxonomy.get("domains", {}) if isinstance(taxonomy, dict) else {}

    manifestation = item.get("manifestation") or {}
    impact = item.get("potential_impact") or {}
    escalation = item.get("escalation") or {}
    risk = item.get("risk_assessment") or {}
    root = item.get("root_cause_analysis") or {}

    title_n = normalize_pathway_text(item.get("title", ""))
    summary_n = normalize_pathway_text(item.get("summary", ""))
    domain_values = [
        normalize_pathway_text(x)
        for x in (item.get("domain_classification") or [])
    ]

    manifest_text = normalize_pathway_text(
        " ".join([
            str(manifestation.get("how_it_is_observed", "")),
            " ".join(manifestation.get("key_indicators", []) or [])
        ])
    )
    impact_text = normalize_pathway_text(
        " ".join([
            " ".join(impact.get("affected_elements", []) or []),
            str(impact.get("threat_level", "")),
            str(escalation.get("speed", "")),
            str(escalation.get("urgency", ""))
        ])
    )
    risk_text = normalize_pathway_text(
        " ".join([
            " ".join(risk.get("risk_type", []) or []),
            str(risk.get("severity_level", "")),
            str(risk.get("explanation", ""))
        ])
    )
    root_text = normalize_pathway_text(
        " ".join(root.get("root_cause", []) or [])
    )

    full_evidence = " ".join([
        title_n, summary_n, manifest_text, impact_text, risk_text, root_text
    ])

    for domain_id, domain in domains.items():
        domain_label = normalize_pathway_text(domain.get("label", domain_id))

        for node in domain.get("nodes", []) or []:
            aliases = [
                normalize_pathway_text(x)
                for x in (node.get("aliases", []) or [])
                if normalize_pathway_text(x)
            ]
            keywords = [
                normalize_pathway_text(x)
                for x in (node.get("keywords", []) or [])
                if normalize_pathway_text(x)
            ]

            score = 0.0
            evidence = []
            exact = False

            # Domain alignment is strong evidence but not sufficient on its own
            # for most downstream nodes.
            if domain_id == "cross_system_cascade":
                domain_hit = bool(domain_values)
            else:
                domain_hit = (
                    normalize_pathway_text(domain_id.replace("_", " ")) in domain_values
                    or domain_label in domain_values
                    or any(
                        token and any(token in d for d in domain_values)
                        for token in domain_label.split()
                        if len(token) > 3
                    )
                )

            if domain_hit and node.get("kind") == "signal":
                score = max(score, 0.74)
                evidence.append("domain_classification")

            # Manifestation / affected-system evidence is preferred for
            # evidence-linked mappings.
            if any(a and (a in manifest_text or manifest_text in a) for a in aliases):
                score = max(score, 0.88)
                evidence.append("manifestation")
                exact = True

            if any(k and k in manifest_text for k in keywords):
                score = max(score, 0.82)
                evidence.append("manifestation")
                exact = True

            if any(k and k in impact_text for k in keywords):
                score = max(score, 0.72)
                evidence.append("potential_impact")
                exact = True

            if any(k and k in risk_text for k in keywords):
                score = max(score, 0.66)
                evidence.append("risk_assessment")

            # Narrative matching is intentionally lower-confidence.
            if any(a and a in title_n for a in aliases):
                score = max(score, 0.78)
                evidence.append("title")

            if any(k and k in summary_n for k in keywords) or any(a and a in summary_n for a in aliases):
                score = max(score, 0.68)
                evidence.append("summary")

            if any(a and a in root_text for a in aliases):
                score = max(score, 0.60)
                evidence.append("root_cause")

            # Do not classify a static intervention node purely because its
            # generic response keywords happen to appear in a risk explanation.
            if node.get("kind") == "intervention" and not any(
                e in evidence for e in ("manifestation", "potential_impact", "domain_classification")
            ):
                score = min(score, 0.45)

            if score < 0.58:
                continue

            matches.append({
                "domain_id": domain_id,
                "domain": domain.get("label", domain_id),
                "node_id": node.get("id"),
                "node": node.get("label", node.get("id")),
                "stage": node.get("stage", ""),
                "kind": node.get("kind", "stress"),
                "match": "evidence_linked" if exact or score >= 0.80 else "heuristic",
                "confidence": round(min(1.0, score), 2),
                "evidence": sorted(set(evidence))
            })

    # Keep the strongest evidence for each node and cap the number of mappings
    # so one noisy record does not light up the whole pathway.
    best = {}
    for match in matches:
        key = (match["domain_id"], match["node_id"])
        if key not in best or (
            match["confidence"],
            match["match"] == "evidence_linked"
        ) > (
            best[key]["confidence"],
            best[key]["match"] == "evidence_linked"
        ):
            best[key] = match

    matches = list(best.values())
    matches.sort(
        key=lambda x: (-x["confidence"], x["domain_id"], x["node_id"])
    )
    return matches[:12]


def enrich_signal_pathways(database, taxonomy):
    """Retroactively refresh pathway mappings for all stored records."""
    changed = False

    for item in database:
        new_matches = classify_signal_pathway(item, taxonomy)
        old_matches = item.get("pathway_matches", [])

        if old_matches != new_matches:
            item["pathway_matches"] = new_matches
            changed = True

    return changed

# =====================================================================
# CORE TASKS: DATA CRAWL & RESUME GENERATION
# =====================================================================

def run_discovery_pipeline(api_key, database, max_items=2):
    keyword = random.choice(KEYWORDS)
    log.info(f"🚀 Initiating radar ping for: '{keyword}'")

    # 1. PYTHON MENCARI DATA DI WEB
    raw_web_data = get_real_world_signals(keyword, max_results=5)
    
    if not raw_web_data:
        log.warning("⚠️ No raw signals found on web this run.")
        return 0

    success_count = 0

    # 2. GEMINI MENGANALISA DATA
    for item in raw_web_data:
        if success_count >= max_items: break

        # Gabungkan judul dan deskripsi dari web
        raw_text = f"Title: {item['title']}\nSummary: {item['snippet']}\nURL: {item['url']}"
        discovered_url = clean_url(item['url'])

        # Cek apakah artikel ini membicarakan Sinyal Laten
        validation = pass_1_validate(api_key, raw_text)
        if not validation.get("is_signal") or validation.get("confidence", 0) < 0.6:
            continue

        base_data = pass_2_extract(api_key, raw_text)
        if not base_data or not base_data.get("title"):
            continue

        normalized_title = normalize_title(base_data["title"])
        country = base_data.get("location", {}).get("country", "unknown").lower()
        unique_string = f"{normalized_title}-{country}"
        title_hash = hashlib.md5(unique_string.encode('utf-8')).hexdigest()

        # Cegah duplikasi data
        if any(db_item.get("id") == title_hash for db_item in database):
            continue

        risk_data = pass_3_risk(api_key, raw_text)
        lineage_data = pass_4_lineage(api_key, raw_text)

        final_item = {
            "id": title_hash, 
            "timestamp": datetime.now().isoformat(),
            **base_data,
            "sources": [discovered_url] if discovered_url else [],
            "root_cause_analysis": lineage_data if lineage_data else {"root_cause":[]},
            "risk_assessment": risk_data if risk_data else {}
        }

        # Dapatkan Lat/Lon untuk Map
        loc_str = f"{final_item.get('location', {}).get('region', '')}, {country}".strip(", ")
        lat, lon = get_coordinates(loc_str)
        final_item["location"]["lat"] = lat
        final_item["location"]["lon"] = lon

        final_item = calculate_advanced_metrics(final_item)

        taxonomy = load_json_file(PATHWAY_FILE, {"version": "1.0", "domains": {}})
        final_item["pathway_matches"] = classify_signal_pathway(final_item, taxonomy)

        database.append(final_item)
        success_count += 1
        
        log.info(f"🚨 Signal Detected: {final_item['title']} ({final_item.get('domain_classification')})")
        log.info("⏳ Throttling API calls... waiting 15 seconds.")
        time.sleep(15)

    return success_count
    
def generate_intelligence_report(api_key, database):
    if not database:
        log.warning("Database is empty. Skipping report generation.")
        return

    log.info("📊 Generating Latent Signal Intelligence Report...")
    quarter = get_current_quarter()
    db_string = json.dumps(database, ensure_ascii=False)

    sys_prompt = """You are an elite AI Intelligence Analyst generating a global report on Latent Environmental & Societal Signals.
OUTPUT FORMAT (STRICT JSON ONLY):
{
  "report_metadata": { "report_id": "gsi-current", "generated_at": "", "period": "", "total_signals_analyzed": 0 },
  "global_summary": { "total_signals": 0, "high_urgency_percentage": 0, "anthropogenic_percentage": 0 },
  "domain_insights":[ { "domain": "", "count": 0, "key_pattern": "" } ],
  "geographic_threats":[ { "region": "", "dominant_issue": "", "threat_level": "low|medium|high" } ],
  "risk_analysis": { "high_risk_cases": 0, "critical_cases": 0, "top_threats": [], "emerging_risks":[] }
}"""

    prompt = f"Analyze this dataset and generate the report.\n\nDATASET:\n{db_string}"
    new_report = call_gemini_with_retry(api_key, prompt, sys_prompt, expect_json=True)

    if new_report:
        new_report["report_metadata"]["total_signals_analyzed"] = len(database)
        new_report["report_metadata"]["generated_at"] = datetime.now().isoformat()
        new_report["report_metadata"]["period"] = quarter
        new_report["report_metadata"]["report_id"] = "gsi-current"
        
        resume_db = load_json_file(RESUME_FILE,[])
        for report in resume_db:
            if isinstance(report, dict):
                report.setdefault("report_metadata", {})["report_id"] = "gsi-older"

        resume_db.append(new_report)
        save_json_file(RESUME_FILE, resume_db)
        log.info(f"✅ Resume successfully generated.")
    else:
        log.error("Failed to generate intelligence report.")


# =====================================================================
# MAIN SCHEDULER & EXECUTION CONTROLLER
# =====================================================================

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    run_type = os.environ.get("RUN_TYPE", "auto").strip().lower()

    if not api_key:
        log.error("GEMINI_API_KEY not found or empty!")
        return

    try:
        db = load_json_file(DATA_FILE, [])
        if not isinstance(db, list): db =[]

        pathway_taxonomy = load_json_file(
            PATHWAY_FILE,
            {"version": "1.0", "domains": {}}
        )
        pathway_changed = enrich_signal_pathways(db, pathway_taxonomy)
            
        history = load_json_file(HISTORY_FILE, {
            "last_data_crawl": "2000-01-01T00:00:00",
            "last_resume_gen": "2000-01-01T00:00:00"
        })

        now = datetime.now()
        last_data_time = datetime.fromisoformat(history.get("last_data_crawl", "2000-01-01T00:00:00"))
        last_resume_time = datetime.fromisoformat(history.get("last_resume_gen", "2000-01-01T00:00:00"))

        do_data = False
        do_resume = False

        if run_type == "force_data": do_data = True
        elif run_type == "force_resume": do_resume = True
        elif run_type == "force_both": do_data = do_resume = True
        else:
            log.info("⏳ TRIGGER: Auto Schedule Mode. Checking Timestamps...")
            if now - last_data_time >= timedelta(days=DATA_INTERVAL_DAYS): do_data = True
            if now - last_resume_time >= timedelta(days=RESUME_INTERVAL_DAYS): do_resume = True

        if do_data:
            log.info("--- 🟢 STARTING SIGNAL PIPELINE ---")
            found = run_discovery_pipeline(api_key, db, max_items=MAX_ITEMS_PER_RUN)
            pathway_changed = enrich_signal_pathways(db, pathway_taxonomy)

            if found > 0 or pathway_changed:
                save_json_file(DATA_FILE, db)

            history["last_data_crawl"] = now.isoformat()
            log.info(
                f"🟢 COMPLETE. Added {found} new signals. "
                f"Pathway mappings refreshed: {pathway_changed}. Total: {len(db)}"
            )

        if do_resume:
            log.info("--- 🔵 STARTING RESUME PIPELINE ---")
            generate_intelligence_report(api_key, db)
            history["last_resume_gen"] = now.isoformat()
            log.info("🔵 COMPLETE.")

        save_json_file(HISTORY_FILE, history)
        log.info("✅ All requested tasks completed.")

    except Exception as e:
        log.error(f"Fatal Error during execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
