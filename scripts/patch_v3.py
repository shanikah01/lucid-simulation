p = '/app/frontend/public/lucidflex-app.html'
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


card = '''            <!-- Backup & Review Export -->
            <div class="neon-card p-5 space-y-4" data-testid="backup-export-card">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
                    <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2"><i data-lucide="hard-drive-download" class="lf-ic text-amber-600"></i> Backup, Strategy &amp; Review Export</h3>
                    <span class="text-[11px] text-slate-500">Review your record before you pay for a real funded account.</span>
                </div>
                <div>
                    <label for="strategyNotes" class="block text-xs font-bold text-slate-600 mb-1">My Strategy / Playbook <span class="font-medium text-slate-400">(setups, entry rules, risk plan, saved automatically)</span></label>
                    <textarea id="strategyNotes" data-testid="strategy-notes-input" rows="4" oninput="saveStrategyNotes()" placeholder="e.g. Gold NY open pullback to VWAP, 1:2 R/R, max 2 trades a day, stop after 2 losses..." class="w-full p-2.5 rounded-xl border border-stone-200 text-xs font-medium text-slate-800"></textarea>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    <button onclick="openReviewReport()" data-testid="export-review-report-btn" class="neon-btn neon-btn-primary py-2.5 px-3 text-xs flex items-center justify-center gap-2"><i data-lucide="file-text" class="lf-ic"></i> Review Report (PDF)</button>
                    <button onclick="exportTradesCsv()" data-testid="export-trades-csv-btn" class="neon-btn bg-emerald-100 hover:bg-emerald-200 text-emerald-800 py-2.5 px-3 text-xs flex items-center justify-center gap-2"><i data-lucide="sheet" class="lf-ic"></i> All Trades (CSV)</button>
                    <button onclick="exportBackup()" data-testid="export-backup-btn" class="neon-btn bg-amber-100 hover:bg-amber-200 text-amber-800 py-2.5 px-3 text-xs flex items-center justify-center gap-2"><i data-lucide="download" class="lf-ic"></i> Export Backup</button>
                    <button onclick="document.getElementById('importBackupFile').click()" data-testid="import-backup-btn" class="neon-btn bg-stone-100 hover:bg-stone-200 text-slate-700 py-2.5 px-3 text-xs flex items-center justify-center gap-2"><i data-lucide="upload" class="lf-ic"></i> Import Backup</button>
                    <input type="file" id="importBackupFile" data-testid="import-backup-file" accept=".json,application/json" class="hidden" onchange="importBackup(event)">
                </div>
                <p class="text-[11px] text-slate-500">The backup is one .json file with every run, trade, payout, badge, rule and setting. Import it on any device to restore everything. The review report opens as a printable page, where you can tap Print, then Save as PDF.</p>
            </div>

            <!-- Achievement Badges Grid -->'''
rep('            <!-- Achievement Badges Grid -->', card)
rep('            careerHistory: []\n        };', '            careerHistory: [],\n            strategyNotes: \'\'\n        };')

js = r'''
        const esc = v => String(v ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
        const stamp = () => todayNZ();
        function downloadFile(name, text, type) {
            const url = URL.createObjectURL(new Blob([text], { type }));
            const a = Object.assign(document.createElement('a'), { href: url, download: name });
            document.body.appendChild(a); a.click(); a.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        }

        let strategyTimer = null;
        function saveStrategyNotes() {
            appState.strategyNotes = document.getElementById('strategyNotes').value;
            clearTimeout(strategyTimer);
            strategyTimer = setTimeout(() => localStorage.setItem(STORAGE_KEY, JSON.stringify(appState)), 400);
        }

        function exportBackup() {
            const payload = { app: 'lucidflex-battlepass', version: 2, exportedAt: new Date().toISOString(), state: appState };
            downloadFile(`lucidflex-backup-${stamp()}.json`, JSON.stringify(payload, null, 2), 'application/json');
            toast('Backup exported. Keep the file somewhere safe.');
        }

        function importBackup(ev) {
            const file = ev.target.files[0];
            ev.target.value = '';
            if (!file) return;
            const reader = new FileReader();
            reader.onload = () => {
                let data;
                try { data = JSON.parse(reader.result); } catch (e) { toast('That file is not a valid backup.'); return; }
                const st = data && data.state ? data.state : data;
                if (!st || !st.activeRun || !Array.isArray(st.careerHistory)) { toast('That file is not a LucidFlex backup.'); return; }
                if (!confirm(`Import this backup? It replaces your current data with ${st.careerHistory.length} archived run(s) plus the active Run #${st.activeRun.runNum}.`)) return;
                localStorage.setItem(STORAGE_KEY, JSON.stringify(st));
                loadState();
                document.getElementById('strategyNotes').value = appState.strategyNotes || '';
                saveState();
                toast('Backup imported. Everything is restored.');
            };
            reader.readAsText(file);
        }

        function allRuns() {
            const m = replay();
            const run = appState.activeRun;
            const active = { runNum: run.runNum, outcome: m.complete ? 'passed' : 'active', blownReason: null, finalStage: m.stageNum, finalBalance: m.balance, payoutsUsd: m.paidUsd, trades: run.trades || [], payouts: run.payouts || [], dateEnded: 'In progress' };
            return [...(appState.careerHistory || []), active];
        }

        function tradeStats(T) {
            const wins = T.filter(t => t.pnl > 0), losses = T.filter(t => t.pnl < 0);
            const gw = wins.reduce((a, t) => a + t.pnl, 0), gl = Math.abs(losses.reduce((a, t) => a + t.pnl, 0));
            const days = {};
            T.forEach(t => days[t.date] = (days[t.date] || 0) + t.pnl);
            const dv = Object.values(days);
            const group = key => {
                const g = {};
                T.forEach(t => { const k = key(t) || '-'; g[k] = g[k] || { n: 0, w: 0, pnl: 0 }; g[k].n++; if (t.pnl > 0) g[k].w++; g[k].pnl += t.pnl; });
                return g;
            };
            return {
                n: T.length, wins: wins.length, losses: losses.length,
                winRate: T.length ? wins.length / T.length * 100 : 0,
                net: gw - gl, pf: gl > 0 ? gw / gl : (gw > 0 ? Infinity : 0),
                avgWin: wins.length ? gw / wins.length : 0, avgLoss: losses.length ? gl / losses.length : 0,
                expectancy: T.length ? (gw - gl) / T.length : 0,
                followedPct: T.length ? T.filter(t => t.followed).length / T.length * 100 : 0,
                days: dv.length, greenDays: dv.filter(v => v >= 150).length,
                bestDay: dv.length ? Math.max(...dv) : 0, worstDay: dv.length ? Math.min(...dv) : 0,
                maxMicros: T.length ? Math.max(...T.map(t => t.contracts || 0)) : 0,
                bySymbol: group(t => t.symbol), byEmotion: group(t => t.emotion), byRules: group(t => t.followed ? 'Followed plan' : 'Broke plan')
            };
        }

        function exportTradesCsv() {
            const rows = [['Run', 'Run Outcome', 'Date', 'Symbol', 'Side', 'Micros', 'Minis', 'Units (TradingView)', 'Net P&L USD', 'Emotion', 'Followed Plan', 'Notes']];
            allRuns().forEach(r => (r.trades || []).slice().sort((a, b) => a.date.localeCompare(b.date)).forEach(t => {
                const a = assetOf(t.symbol);
                rows.push([r.runNum, r.outcome, t.date, t.symbol, t.side, t.contracts, t.contracts / 10, a && a.unitsPerMicro ? `${t.contracts * a.unitsPerMicro} ${a.cfd}` : '', t.pnl.toFixed(2), t.emotion, t.followed ? 'Yes' : 'No', t.notes || '']);
            }));
            if (rows.length === 1) { toast('No trades to export yet.'); return; }
            const csv = rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n');
            downloadFile(`lucidflex-trades-${stamp()}.csv`, csv, 'text/csv');
            toast(`${rows.length - 1} trades exported.`);
        }

        function buildReviewHtml() {
            const runs = allRuns();
            const archived = appState.careerHistory || [];
            const T = runs.flatMap(r => r.trades || []);
            const st = tradeStats(T);
            const passed = archived.filter(h => h.outcome === 'passed').length;
            const failed = archived.filter(h => h.outcome === 'failed').length;
            const evalPasses = runs.filter(r => (r.finalStage || 1) >= 2).length;
            const reasons = {};
            archived.filter(h => h.outcome === 'failed').forEach(h => { const k = (h.blownReason || 'Unknown').split(' (')[0]; reasons[k] = (reasons[k] || 0) + 1; });
            const paid = runs.reduce((a, r) => a + (r.payoutsUsd || 0), 0);
            const pfTxt = st.pf === Infinity ? '∞' : st.pf.toFixed(2);
            const checks = [
                ['Passed at least one evaluation', evalPasses >= 1],
                ['Completed a full battle pass (5 payouts)', passed >= 1],
                ['At least 30 logged trades', st.n >= 30],
                ['Profit factor 1.5 or higher', st.pf >= 1.5],
                ['Followed your plan on 90%+ of trades', st.followedPct >= 90],
                ['Last archived run was not a failure', !archived.length || archived[archived.length - 1].outcome !== 'failed']
            ];
            const score = checks.filter(c => c[1]).length;
            const tbl = (title, g) => `<h3>${title}</h3><table><tr><th>Group</th><th>Trades</th><th>Win rate</th><th>Net P&amp;L</th></tr>${Object.entries(g).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v.n}</td><td>${(v.w / v.n * 100).toFixed(0)}%</td><td class="${v.pnl >= 0 ? 'pos' : 'neg'}">${usd(v.pnl)}</td></tr>`).join('') || '<tr><td colspan="4">No data</td></tr>'}</table>`;
            const card = (l, v, cls = '') => `<div class="card"><div class="l">${l}</div><div class="v ${cls}">${v}</div></div>`;
            return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LucidFlex Review Report ${stamp()}</title>
<style>body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0;padding:28px;color:#1a1a24;background:#fff;max-width:960px;margin:auto}h1{margin:0 0 4px;font-size:26px}h2{margin:28px 0 10px;font-size:17px;border-bottom:2px solid #a855f7;padding-bottom:4px}h3{font-size:13px;margin:16px 0 6px}.sub{color:#666;font-size:12px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}.card{border:1px solid #e3d9f7;border-radius:10px;padding:10px}.l{font-size:10px;color:#777;text-transform:uppercase;letter-spacing:.05em}.v{font-size:18px;font-weight:700;margin-top:2px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #eee;vertical-align:top}th{background:#f6f1ff}.pos{color:#0a8f4a}.neg{color:#d61f45}.ok{color:#0a8f4a;font-weight:700}.no{color:#d61f45;font-weight:700}.verdict{padding:14px;border-radius:10px;background:#f6f1ff;border:1px solid #a855f7;font-size:13px}pre{white-space:pre-wrap;font-family:inherit;font-size:12px;background:#fafafa;border:1px solid #eee;border-radius:8px;padding:10px;margin:0}.btn{position:fixed;top:14px;right:14px;background:#7c3aed;color:#fff;border:0;border-radius:8px;padding:10px 16px;font-weight:700;cursor:pointer}@media print{.btn{display:none}body{padding:0}h2{break-after:avoid}table{break-inside:auto}tr{break-inside:avoid}}</style></head><body>
<button class="btn" onclick="window.print()">Print / Save PDF</button>
<h1>LucidFlex $50K Battle Pass: Review Report</h1><div class="sub">Generated ${new Date().toLocaleString('en-NZ', { timeZone: 'Pacific/Auckland' })} NZT • Paper trading record • Not financial advice</div>
<h2>Funded-Account Readiness (${score} / ${checks.length})</h2>
<div class="verdict">${score >= 5 ? '<strong>Looking ready.</strong> Your paper record shows the consistency Lucid rewards. Consider a real evaluation.' : score >= 3 ? '<strong>Getting close.</strong> Fix the unchecked items below before paying for a real evaluation.' : '<strong>Not ready yet.</strong> Keep running the battle pass until more of these checks pass.'}</div>
<table style="margin-top:10px">${checks.map(c => `<tr><td>${c[0]}</td><td class="${c[1] ? 'ok' : 'no'}">${c[1] ? 'PASS' : 'NOT YET'}</td></tr>`).join('')}</table>
<h2>Career Overview</h2><div class="grid">${card('Total runs', runs.length)}${card('Evals passed', evalPasses)}${card('Battle passes won', passed)}${card('Failed runs', failed, failed ? 'neg' : '')}${card('Run win rate', archived.length ? (passed / archived.length * 100).toFixed(0) + '%' : '—')}${card('Payouts to you (USD)', usd(paid), 'pos')}</div>
<h2>Trading Statistics (all runs)</h2><div class="grid">${card('Trades', st.n)}${card('Trade win rate', st.winRate.toFixed(0) + '%')}${card('Net P&L', usd(st.net), st.net >= 0 ? 'pos' : 'neg')}${card('Profit factor', pfTxt)}${card('Avg win', usd(st.avgWin), 'pos')}${card('Avg loss', usd(-st.avgLoss), 'neg')}${card('Expectancy / trade', usd(st.expectancy), st.expectancy >= 0 ? 'pos' : 'neg')}${card('Plan followed', st.followedPct.toFixed(0) + '%')}${card('Trading days', st.days)}${card('Green days (+$150)', st.greenDays)}${card('Best day', usd(st.bestDay), 'pos')}${card('Worst day', usd(st.worstDay), 'neg')}${card('Largest size', st.maxMicros + ' micros')}</div>
${tbl('By market', st.bySymbol)}${tbl('By emotion', st.byEmotion)}${tbl('Plan discipline', st.byRules)}
<h2>Why Runs Failed</h2><table><tr><th>Reason</th><th>Count</th></tr>${Object.entries(reasons).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v}</td></tr>`).join('') || '<tr><td colspan="2">No failed runs</td></tr>'}</table>
<h2>My Strategy / Playbook</h2><pre>${esc(appState.strategyNotes || 'No strategy written yet. Add one in the Career tab.')}</pre>
<h3>Personal &amp; Lucid rules</h3><ul style="font-size:12px">${appState.personalRules.map(r => `<li>${esc(r.text)}${r.isLucid ? ' <em>(Lucid)</em>' : ''}</li>`).join('')}</ul>
<h2>Run History</h2><table><tr><th>Run</th><th>Outcome</th><th>Stage</th><th>Trades</th><th>Net P&amp;L</th><th>Payouts</th><th>Ended</th><th>Reason</th></tr>${runs.map(r => { const s2 = tradeStats(r.trades || []); return `<tr><td>#${r.runNum}</td><td>${esc(r.outcome)}</td><td>${r.finalStage}</td><td>${s2.n}</td><td class="${s2.net >= 0 ? 'pos' : 'neg'}">${usd(s2.net)}</td><td>${usd(r.payoutsUsd || 0)}</td><td>${esc(r.dateEnded)}</td><td>${esc(r.blownReason || '')}</td></tr>`; }).join('')}</table>
<h2>Trade Log</h2><table><tr><th>Run</th><th>Date</th><th>Market</th><th>Side</th><th>Size</th><th>P&amp;L</th><th>Emotion</th><th>Plan</th><th>Notes</th></tr>${runs.flatMap(r => (r.trades || []).slice().sort((a, b) => a.date.localeCompare(b.date)).map(t => `<tr><td>#${r.runNum}</td><td>${t.date}</td><td>${esc(t.symbol)}</td><td>${esc(t.side)}</td><td>${t.contracts} micros</td><td class="${t.pnl >= 0 ? 'pos' : 'neg'}">${usd(t.pnl)}</td><td>${esc(t.emotion)}</td><td>${t.followed ? 'Yes' : 'No'}</td><td>${esc(t.notes)}</td></tr>`)).join('') || '<tr><td colspan="9">No trades yet</td></tr>'}</table>
</body></html>`;
        }

        function openReviewReport() {
            const html = buildReviewHtml();
            const w = window.open('', '_blank');
            if (w) { w.document.open(); w.document.write(html); w.document.close(); }
            else downloadFile(`lucidflex-review-${stamp()}.html`, html, 'text/html');
        }
'''
rep('        function migrateRun(run) {', js + '        function migrateRun(run) {')
rep("            saveState();\n            if (!localStorage.getItem('lucidflex_guide_seen')) openGuide();",
    "            document.getElementById('strategyNotes').value = appState.strategyNotes || '';\n            saveState();\n            if (!localStorage.getItem('lucidflex_guide_seen')) openGuide();")
open(p, 'w', encoding='utf-8').write(s)
js2 = s[s.index('<script>\n        /* ==='):]
js2 = js2[8:js2.index('</script>')]
open('/tmp/t.js', 'w').write(js2)
print('OK')
