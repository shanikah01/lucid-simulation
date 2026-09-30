import re, sys

SRC = '/tmp/a.html'
DST = '/app/frontend/public/lucidflex.html'
s = open(SRC, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'Expected {count} got {n}: {old[:80]!r}')
    s = s.replace(old, new)


def rep_fn(name, new):
    global s
    start = s.index(f'\n        function {name}(')
    end = s.index('\n        }\n', start) + len('\n        }')
    s = s[:start] + '\n' + new.rstrip() + s[end:]


# ---------- 1. THEME ----------
head_start = s.index('    <script>\n        tailwind.config')
head_end = s.index('</style>') + len('</style>')
s = s[:head_start] + open('/app/scripts/lucidflex_head.html', encoding='utf-8').read().rstrip() + s[head_end:]
rep('<meta name="color-scheme" content="light">', '<meta name="color-scheme" content="dark">')
rep('family=Quicksand:wght@500;600;700&family=Inter:wght@400;500;600;700', 'family=Chakra+Petch:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700')
for a, b in [('cozy-card', 'neon-card'), ('cozy-btn', 'neon-btn'), ('cozy-badge', 'neon-badge'), ('tab-btn', 'neon-tab')]:
    s = s.replace(a, b)
s = s.replace('bg-slate-900/40 backdrop-blur-sm', 'neon-backdrop')
s = s.replace('neon-btn bg-emerald-400 hover:bg-emerald-500 text-slate-900', 'neon-btn neon-btn-primary')
rep('Cozy Paper Trading Battle Pass & Rule Companion ✨', 'Hardened Paper Trading Battle Pass &amp; Rule Companion')
rep('Simple, cozy explanations', 'Simple, no-fluff explanations')
rep('font-semibold">DLL OFF</span>', 'font-semibold" id="headerDllBadge" data-testid="header-dll-badge">DLL $1,000</span>')
rep('id="headerStageBadge" class="neon-badge', 'id="headerStageBadge" data-testid="header-stage-badge" class="neon-badge neon-stage')
rep('''<span class="font-bold text-amber-800">What does DLL OFF mean?</span>
                        <p class="mt-0.5">There is <strong>no Daily Loss Limit</strong> kick-out rule! You only need to protect your EOD trailing balance from dropping below the safety floor.</p>''',
    '''<span class="font-bold text-amber-800">What is the Daily Loss Limit?</span>
                        <p class="mt-0.5">This hardened tracker enforces a <strong>$1,000 Daily Loss Limit</strong>. Lose that much in one trading day and the run is blown and resets to Stage 1.</p>''')
rep('class="fixed left-1/2 -translate-x-1/2 bottom-6 z-[60] hidden max-w-sm w-[90%] bg-slate-800 text-white',
    'data-testid="toast" class="fixed left-1/2 -translate-x-1/2 bottom-6 z-[70] hidden max-w-sm w-[90%] bg-stone-100 text-slate-800 border border-amber-400')

# ---------- 8. BANNERS ----------
def banner(tid):
    return f'''
            <div class="reset-banner rounded-xl px-4 py-3 flex items-center justify-between gap-3" data-testid="reset-warning-banner-{tid}">
                <div class="flex items-center gap-3 text-sm"><span class="pulse-dot"></span><span><strong class="text-amber-700 tracking-wider">HARD RULES ARMED.</strong> Break any hard rule &rarr; account resets to Stage 1. All stats archive as a failed run.</span></div>
                <button onclick="dismissBanner()" data-testid="dismiss-banner-{tid}" class="text-xs font-bold text-slate-500 hover:text-slate-800 px-3 py-1 rounded-lg border border-stone-200 flex-shrink-0">Dismiss</button>
            </div>'''

rep('<section id="sec-dashboard" class="space-y-6">', '<section id="sec-dashboard" class="space-y-6">' + banner('dashboard'))
hard_rules = '''
            <div class="neon-card p-5 space-y-3" data-testid="hard-rules-card">
                <h3 class="font-bold text-slate-800 text-sm tracking-wider">HARD RULES (AUTO-ENFORCED)</h3>
                <ul class="text-xs text-slate-700 space-y-1.5 list-disc pl-5">
                    <li>EOD trailing drawdown: balance at or below the safety floor.</li>
                    <li>Daily loss limit: losing <span id="rulesDllText">$1,000</span> or more in one trading day.</li>
                    <li>Consistency: reaching the $53K target while your best day is over 50% of profit.</li>
                    <li>Position size: any trade over the current stage cap (no grace, 1 micro over = blown).</li>
                </ul>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
                    <div class="p-2 rounded-lg border border-stone-200"><div class="text-slate-500">Evaluation</div><div class="font-bold text-amber-700">40 micros / 4 minis</div></div>
                    <div class="p-2 rounded-lg border border-stone-200"><div class="text-slate-500">Funded $0&ndash;$999</div><div class="font-bold text-amber-700">20 micros / 2 minis</div></div>
                    <div class="p-2 rounded-lg border border-stone-200"><div class="text-slate-500">Funded $1,000&ndash;$1,999</div><div class="font-bold text-amber-700">30 micros / 3 minis</div></div>
                    <div class="p-2 rounded-lg border border-stone-200"><div class="text-slate-500">Funded $2,000+</div><div class="font-bold text-amber-700">40 micros / 4 minis</div></div>
                </div>
            </div>'''
rep('<section id="sec-rules" class="space-y-6 hidden">', '<section id="sec-rules" class="space-y-6 hidden">' + banner('rules') + hard_rules)

# ---------- 2. UNITS: calculator + journal ----------
rep('''
                            <option value="MES">MES - Micro E-mini S&P 500 ($1.25/tick, $5/pt)</option>
                            <option value="MNQ">MNQ - Micro E-mini Nasdaq ($0.50/tick, $2/pt)</option>
                            <option value="MCL">MCL - Micro Crude Oil ($1.00/tick, $10/pt)</option>
                            <option value="MGC">MGC - Micro Gold ($1.00/tick, $10/pt)</option>''', '')
rep('<select id="calcSymbol"', '<select id="calcSymbol" data-testid="calc-symbol-select"')
rep('<span id="calcCurrentCapBadge"', '<span id="calcCurrentCapBadge" data-testid="calc-cap-badge"')
rep('never violate Lucid limits!</p>', 'never violate Lucid limits!</p>\n                        <p id="calcCapUnits" data-testid="calc-cap-units" class="text-[11px] font-semibold text-indigo-700"></p>')
rep('id="calcResultMinis">Or 0 Full Minis</div>', 'id="calcResultMinis">Or 0 Full Minis</div>\n                        <div id="calcResultUnits" data-testid="calc-result-units" class="text-[11px] text-slate-500"></div>')
rep('<span id="calcResultMicros">', '<span id="calcResultMicros" data-testid="calc-result-micros">')
rep('''
                            <option value="MES">MES - Micro E-mini S&P</option>
                            <option value="MNQ">MNQ - Micro Nasdaq</option>
                            <option value="MCL">MCL - Micro Crude Oil</option>
                            <option value="MGC">MGC - Micro Gold</option>''', '')
rep('<select id="tradeSymbol" class=', '<select id="tradeSymbol" onchange="updateTradeHint()" data-testid="trade-symbol-select" class=')
rep('''                        <label class="block text-xs font-bold text-slate-600 mb-1">Micro Contracts Count</label>
                        <input type="number" id="tradeContracts" value="2" min="1" max="40" class="w-full p-2.5 rounded-xl border border-stone-200 text-xs font-bold text-slate-800">''',
    '''                        <label class="block text-xs font-bold text-slate-600 mb-1">Position Size</label>
                        <div class="flex gap-2">
                            <input type="number" id="tradeContracts" value="2" min="1" step="1" oninput="updateTradeHint()" data-testid="trade-size-input" class="w-3/5 p-2.5 rounded-xl border border-stone-200 text-xs font-bold text-slate-800">
                            <select id="tradeSizeUnit" onchange="updateTradeHint()" data-testid="trade-size-unit" class="w-2/5 p-2.5 rounded-xl border border-stone-200 text-xs font-bold text-slate-800"><option value="micros">Micros</option><option value="minis">Minis</option></select>
                        </div>''')
rep('                <!-- Emotion / Mindset -->', '                <p id="tradeSizeHint" data-testid="trade-size-hint" class="text-[11px] font-medium -mt-1"></p>\n                <!-- Emotion / Mindset -->')
rep('<input type="date" id="tradeDate"', '<input type="date" id="tradeDate" data-testid="trade-date-input"')
rep('<input type="number" id="tradePnLUsd"', '<input type="number" id="tradePnLUsd" data-testid="trade-pnl-input"')
rep('<button onclick="saveLoggedTrade()"', '<button onclick="saveLoggedTrade()" data-testid="save-trade-btn"')

# ---------- 5. CAREER ----------
rep('<div class="grid grid-cols-2 md:grid-cols-4 gap-4">\n                <div class="neon-card p-4 text-center">\n                    <div class="text-xs text-slate-500 font-bold">TOTAL ATTEMPTED RUNS</div>',
    '<div class="grid grid-cols-2 md:grid-cols-5 gap-4">\n                <div class="neon-card p-4 text-center">\n                    <div class="text-xs text-slate-500 font-bold">TOTAL ATTEMPTED RUNS</div>')
rep('<div id="cStatBestStage" class="text-2xl font-bold text-indigo-700 mt-1">Evaluation</div>\n                </div>',
    '''<div id="cStatBestStage" data-testid="career-best-stage" class="text-2xl font-bold text-indigo-700 mt-1">Evaluation</div>
                </div>
                <div class="neon-card p-4 text-center">
                    <div class="text-xs text-slate-500 font-bold">LIFETIME WIN RATE</div>
                    <div id="cStatWinRate" data-testid="career-win-rate" class="text-2xl font-bold text-emerald-600 mt-1">&mdash;</div>
                    <div id="cStatWinSub" data-testid="career-win-sub" class="text-[10px] text-slate-500 mt-0.5">0 passed / 0 failed / 0 reset</div>
                </div>''')
rep('id="cStatTotalRuns"', 'id="cStatTotalRuns" data-testid="career-total-runs"')
rep('<th class="p-3">DATE COMPLETED</th>', '<th class="p-3">DATE COMPLETED</th>\n                                <th class="p-3 text-right">ACTION</th>')

# ---------- 6. DICTIONARY pills ----------
rep('<div class="flex gap-2 overflow-x-auto pb-1 text-xs">', '<div id="dictCatPills" class="flex gap-2 overflow-x-auto pb-1 text-xs">')
s, n = re.subn(r'\n\s*<button onclick="setDictCategory\([^\n]*', '', s)
assert n == 4, n
rep('<input type="text" id="dictSearch"', '<input type="text" id="dictSearch" data-testid="dict-search-input"')

# ---------- NEW MODALS ----------
rep('    <script>\n        /* ===', open('/app/scripts/lucidflex_modals.html', encoding='utf-8').read() + '    <script>\n        /* ===')

# ---------- JS ----------
js = open('/app/scripts/lucidflex_js.js', encoding='utf-8').read()
blocks = dict(re.findall(r'//@@ (\S+)\n(.*?)(?=//@@ |\Z)', js, re.S))

ds_start = s.index('        // Default App State')
ds_end = s.index('        let appState = ')
s = s[:ds_start] + blocks['DEFAULTSTATE'] + s[ds_end:]
rep('const dictionaryTerms = [', 'const baseDictionaryTerms = [')
rep("        let activeDictCategory = 'ALL';", blocks['DICTMERGE'] + "        let activeDictCategory = 'ALL';")
rep('''            loadState();
            startNzClock();
            runCalculator();
            renderAll();''', '''            loadState();
            startNzClock();
            saveState();''')
for name in ['saveState', 'loadState', 'replay', 'calculateMetrics', 'updateTradeHint', 'openLogTradeModal',
             'saveLoggedTrade', 'confirmResetRun', 'renderCareerSection', 'renderBadges', 'runCalculator', 'setDictCategory']:
    rep_fn(name, blocks[name])
rep("function migrateRun(run) {", blocks['HELPERS'] + "\n        function migrateRun(run) {")

# renderAll tweaks
rep("document.getElementById('headerFxRate').innerText = appState.exchangeRate.toFixed(2);",
    "document.getElementById('headerFxRate').innerText = appState.exchangeRate.toFixed(2);\n            const dllTxt = usd(appState.settings.dailyLossLimit).replace('.00', '');\n            document.getElementById('headerDllBadge').innerText = 'DLL ' + dllTxt;\n            document.getElementById('rulesDllText').innerText = dllTxt;\n            renderBanners();\n            renderDictPills();")
rep("badge.className = 'neon-badge border ' +", "badge.className = 'neon-badge neon-stage border ' +")
rep("if (m.consistencyPct > 50) missing.push(`dilute your biggest winning day (currently ${m.consistencyPct.toFixed(1)}%, must be 50% or less)`);",
    "if (m.consistencyPct > 50) missing.push(`dilute your biggest winning day (currently ${m.consistencyPct.toFixed(1)}%, must be 50% or less, reaching $53K above 50% BLOWS the account)`);")
rep('<td class="p-3">${t.contracts} Micros</td>', '<td class="p-3">${sizeCell(t)}</td>')

open(DST, 'w', encoding='utf-8').write(s)
print('OK', len(s))
