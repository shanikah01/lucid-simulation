import re
p = '/app/frontend/public/lucidflex.html'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


# ---- Units: Lucid market conversion (Gold / Silver / Crude) ----
start = s.index("                    MGC: { name: 'Micro Gold'")
end = s.index("                }\n            },\n            activeRun")
s = s[:start] + """                    MGC: { name: 'Micro Gold', mini: 'GC', tickSize: 0.10, tickVal: 1.00, unitsPerMicro: 10, unit: 'oz', cfd: 'XAUUSD' },
                    SIL: { name: 'Micro Silver', mini: 'SI', tickSize: 0.005, tickVal: 5.00, unitsPerMicro: 1000, unit: 'oz', cfd: 'XAGUSD' },
                    MCL: { name: 'Micro Crude Oil', mini: 'CL', tickSize: 0.01, tickVal: 1.00, unitsPerMicro: 100, unit: 'barrels', cfd: 'USOIL/XTIUSD' }
""" + s[end:]
rep("""            const u = +(micros * a.unitsPerMicro).toFixed(4);
            return `${micros} micros ≈ ${u.toLocaleString('en-US')} ${a.unit}`;""",
    """            const u = (micros * a.unitsPerMicro).toLocaleString('en-US');
            return `${micros} micros ≈ ${u} ${a.cfd} units (${u} ${a.unit})`;""")
rep("appState.settings.assets = Object.assign({}, ds.assets, appState.settings.assets || {});", "appState.settings.assets = ds.assets;")
rep("example: '40 MGC micros ≈ 400 oz gold; 10 MCL micros ≈ 1,000 barrels.'", "example: '20 MGC micros ≈ 200 XAUUSD units; 20 SIL ≈ 20,000 XAGUSD; 20 MCL ≈ 2,000 USOIL units.'")
rep("""            document.getElementById('calcRecommendationBox').innerText""",
    """            document.getElementById('convTableBody').innerHTML = Object.entries(assets).filter(([, a]) => a.unitsPerMicro).map(([k, a]) => {
                const f = n => (n * a.unitsPerMicro).toLocaleString('en-US');
                return `<tr class="hover:bg-stone-50" data-testid="conv-row-${k}"><td class="p-3 font-bold">${a.name.replace('Micro ', '')} (${k})</td><td class="p-3 num">${f(1)} ${a.unit}</td><td class="p-3 num">${f(20)} ${a.cfd} units</td><td class="p-3 num">${f(40)} units</td></tr>`;
            }).join('');
            document.getElementById('calcRecommendationBox').innerText""")
rep("""        </section>

        <!-- TAB 4: BEGINNER DICTIONARY -->""", """            <div class="neon-card overflow-hidden" data-testid="conversion-table">
                <div class="p-4 border-b border-stone-200 flex items-center justify-between">
                    <span class="font-bold text-slate-800 text-sm flex items-center gap-2"><i data-lucide="scale" class="lf-ic"></i> Lucid Market Unit Conversion</span>
                    <span class="text-[10px] text-slate-500">Read-only helper. Rules are enforced in micros / minis.</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs text-slate-700">
                        <thead class="bg-stone-100/70 text-slate-500 font-bold border-b border-stone-200">
                            <tr><th class="p-3">LUCID MARKET</th><th class="p-3">1 MICRO</th><th class="p-3">20 MICROS</th><th class="p-3">40 MICROS</th></tr>
                        </thead>
                        <tbody id="convTableBody" class="divide-y divide-stone-100 font-medium"></tbody>
                    </table>
                </div>
            </div>

        </section>

        <!-- TAB 4: BEGINNER DICTIONARY -->""")

# ---- Delete run renumbers run count ----
rep("""            appState.careerHistory = appState.careerHistory.filter(h => h.runNum !== id);
            closeDeleteRunModal();
            saveState();
            toast(`Run #${id} deleted. Lifetime stats recomputed.`);""",
    """            appState.careerHistory = appState.careerHistory.filter(h => h.runNum !== id).sort((a, b) => a.runNum - b.runNum);
            appState.careerHistory.forEach((h, i) => { h.runNum = i + 1; });
            appState.activeRun.runNum = appState.careerHistory.length + 1;
            closeDeleteRunModal();
            saveState();
            toast(`Run #${id} deleted. Runs renumbered, you are now on Run #${appState.activeRun.runNum}.`);""")

# ---- Emojis -> Lucide icons ----
ICONS = {'🇳🇿': 'globe', '🍃': 'leaf', '☕': 'coffee', '🧭': 'compass', '🌱': 'sprout', '🪙': 'coins', '↺': 'rotate-ccw',
         '📊': 'chart-column', '📝': 'notebook-pen', '🧮': 'calculator', '📚': 'book-open', '📜': 'scroll-text', '🏆': 'trophy',
         '🦊': 'bot', '💵': 'banknote', '⭐': 'star', '🛡': 'shield', '🎮': 'gamepad-2', '🎯': 'target', '🕒': 'clock',
         '✨': 'sparkles', '💰': 'wallet', '💡': 'lightbulb', '🔍': 'search', '🩷': 'shield-check', '🎀': 'user-check',
         '📈': 'trending-up', '📉': 'trending-down', '⚡': 'zap', '📏': 'ruler', '🪜': 'layers', '⚖': 'scale', '🚀': 'rocket',
         '🛑': 'octagon-x', '🧱': 'brick-wall', '🧷': 'link', '🧯': 'shield-alert', '📐': 'ruler-dimension-line', '📦': 'package',
         '✖': 'x', '💲': 'dollar-sign', '📅': 'calendar', '〰': 'activity', '🌊': 'waves', '💧': 'droplet', '🎓': 'graduation-cap',
         '💔': 'heart-crack', '✓': 'check', '⚠': 'triangle-alert', '🎉': 'party-popper', '🗑': 'trash-2', '✅': 'circle-check', '😰': 'frown'}
pat = re.compile('(' + '|'.join(map(re.escape, sorted(ICONS, key=len, reverse=True))) + ')\uFE0F?')
text_ctx = re.compile(r"innerText|toast\(|confirm\(|<option|stageNames = \[|mk\('")
lines = []
for line in s.split('\n'):
    if text_ctx.search(line):
        line = re.sub(pat.pattern + ' ?', '', line)
    else:
        line = pat.sub(lambda m: f'<i data-lucide="{ICONS[m.group(1)]}" class="lf-ic"></i>', line)
    lines.append(line)
s = '\n'.join(lines)
s = s.replace("'Stage 4: Live Review '", "'Stage 4: Live Review'").replace("'RUN BREACHED '", "'RUN BREACHED'")
leftover = re.findall('[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]', s)
print('leftover emojis:', leftover)

rep('<script src="https://cdn.tailwindcss.com"></script>', '<script src="https://cdn.tailwindcss.com"></script>\n    <script src="https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js"></script>')
rep('        .num {', "        .lf-ic { width: 1em; height: 1em; display: inline-block; vertical-align: -0.14em; stroke-width: 2; flex-shrink: 0; }\n        .num {")
rep("""            loadState();
            startNzClock();
            saveState();""", """            let iconQueued = false;
            new MutationObserver(() => {
                if (iconQueued || !document.querySelector('i[data-lucide]')) return;
                iconQueued = true;
                requestAnimationFrame(() => { iconQueued = false; lucide.createIcons(); });
            }).observe(document.body, { childList: true, subtree: true });
            loadState();
            startNzClock();
            saveState();
            lucide.createIcons();""")
open(p, 'w', encoding='utf-8').write(s)
print('OK')
