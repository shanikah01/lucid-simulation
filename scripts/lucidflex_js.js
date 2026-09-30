//@@ DEFAULTSTATE
        // Default App State
        const defaultState = {
            beginnerMode: true,
            exchangeRate: 1.70,
            settings: {
                startingBalance: 50000.00,
                dailyLossLimit: 1000.00,
                // Unit conversion table (source of truth for Calculator + Journal). Rules use micros/minis only.
                assets: {
                    MES: { name: 'Micro E-mini S&P 500', mini: 'ES', tickSize: 0.25, tickVal: 1.25, unitsPerMicro: null, unit: '' },
                    MNQ: { name: 'Micro E-mini Nasdaq', mini: 'NQ', tickSize: 0.25, tickVal: 0.50, unitsPerMicro: null, unit: '' },
                    MGC: { name: 'Micro Gold', mini: 'GC', tickSize: 0.10, tickVal: 1.00, unitsPerMicro: 10, unit: 'oz gold' },
                    MCL: { name: 'Micro Crude Oil', mini: 'CL', tickSize: 0.01, tickVal: 1.00, unitsPerMicro: 100, unit: 'barrels oil' },
                    MBT: { name: 'Micro Bitcoin', mini: 'BTC', tickSize: 5.00, tickVal: 0.05, unitsPerMicro: 0.01, unit: 'BTC' },
                    MET: { name: 'Micro Ether', mini: 'ETH', tickSize: 0.50, tickVal: 0.005, unitsPerMicro: 0.01, unit: 'ETH' }
                }
            },
            activeRun: {
                runNum: 1,
                stage: 1, // 1: Eval, 2: Funded Payout 1-4, 3: Final Payout 5, 4: Live Review
                balance: 50000.00,
                highWaterMark: 50000.00,
                eodThreshold: 48000.00,
                totalPayoutsUsd: 0.00,
                payoutCount: 0,
                dailyLossToday: 0.00,
                consistencyBreached: false,
                positionCapMicros: 40,
                trades: [],
                payouts: []
            },
            personalRules: [
                { id: 1, text: 'Maximum $250 USD risk on any single trade.', isLucid: false },
                { id: 2, text: 'No holding positions across 4:45 PM ET market close.', isLucid: true },
                { id: 3, text: 'Maximum 20 micros during initial funded stage.', isLucid: true },
                { id: 4, text: 'Stop trading for the day after 2 consecutive losses.', isLucid: false }
            ],
            careerHistory: []
        };

//@@ DICTMERGE
        const newDictionaryTerms = [
            { term: 'Market Order', category: 'ORDER TYPES', icon: '🚀', simple: 'Buy or sell right now at the best available price.', why: 'Guarantees a fill, not a price. Fast markets can fill you worse than expected.', example: 'Clicking BUY MKT on MES fills instantly at the current ask.' },
            { term: 'Limit Order', category: 'ORDER TYPES', icon: '🎯', simple: 'An order that only fills at your price or better.', why: 'Controls your entry price, but the market may never reach it.', example: 'Buy limit MGC at 2,350.0 only fills at 2,350.0 or lower.' },
            { term: 'Stop Order', category: 'ORDER TYPES', icon: '🛑', simple: 'Becomes a market order once price touches your trigger.', why: 'The standard way to place a protective stop loss.', example: 'Long MES at 5,000 with a sell stop at 4,990.' },
            { term: 'Stop-Limit Order', category: 'ORDER TYPES', icon: '🧱', simple: 'A stop that turns into a limit order instead of a market order.', why: 'Avoids bad fills, but can skip right past you in a fast move and leave you unprotected.', example: 'Stop 4,990, limit 4,989: will not sell below 4,989.' },
            { term: 'Bracket Order (OCO)', category: 'ORDER TYPES', icon: '🧷', simple: 'An entry with an attached stop loss and profit target; one cancels the other.', why: 'Your risk and reward are set before emotions kick in.', example: 'Entry 5,000, target 5,020, stop 4,990.' },
            { term: 'Stop Loss', category: 'RISK', icon: '🧯', simple: 'The pre-planned price where you admit you are wrong and exit.', why: 'Without one, a single trade can blow the EOD drawdown.', example: 'Risking 10 pts on 4 MES = $200 max loss.' },
            { term: 'Position Sizing', category: 'RISK', icon: '📐', simple: 'Choosing how many contracts to trade based on risk, not feelings.', why: 'Keeps each loss small and inside the stage cap. Over the cap = blown.', example: 'Risk $200 / $50 per micro = 4 micros.' },
            { term: 'Max Drawdown', category: 'RISK', icon: '📉', simple: 'The biggest drop from a peak balance to a low point.', why: 'Prop firms fail accounts when drawdown passes a set limit.', example: 'Peak $51,500 down to $50,000 = $1,500 drawdown.' },
            { term: 'Mini Contract', category: 'CONTRACTS', icon: '📦', simple: 'The full-size standard futures contract. 1 mini = 10 micros.', why: 'Caps are listed in both: 40 micros equals 4 minis.', example: '1 GC mini = 10 MGC micros = 100 oz gold.' },
            { term: 'Contract Multiplier', category: 'CONTRACTS', icon: '✖️', simple: 'Dollar value of a 1-point move for one contract.', why: 'Tells you how fast P&L moves per point.', example: 'MES = $5 per point; MGC = $10 per $1 move in gold.' },
            { term: 'Tick Value', category: 'CONTRACTS', icon: '💲', simple: 'Dollars gained or lost when price moves one tick.', why: 'Used by the calculator to size positions exactly.', example: 'MCL tick = $0.01 = $1.00 per micro.' },
            { term: 'Underlying Units', category: 'CONTRACTS', icon: '⚖️', simple: 'The real quantity of the asset one contract represents.', why: 'Helps you feel the true size of a position.', example: '40 MGC micros ≈ 400 oz gold; 10 MCL micros ≈ 1,000 barrels.' },
            { term: 'Expiration & Rollover', category: 'CONTRACTS', icon: '📅', simple: 'Futures expire; traders move to the next month before that.', why: 'Trading the wrong month means thin liquidity and odd prices.', example: 'Roll MES from June (M) to September (U) contract.' },
            { term: 'Support & Resistance', category: 'ANALYSIS', icon: '🧭', simple: 'Price zones where buying (support) or selling (resistance) tends to show up.', why: 'Good places for entries, stops and targets.', example: 'MES bounced at 4,980 three times: that is support.' },
            { term: 'VWAP', category: 'ANALYSIS', icon: '〰️', simple: 'Volume-Weighted Average Price for the session.', why: 'Institutions benchmark fills to it; price often reacts around it.', example: 'Longs above VWAP, shorts below it as a simple bias.' },
            { term: 'Moving Average', category: 'ANALYSIS', icon: '📈', simple: 'The average closing price over the last N bars, drawn as a line.', why: 'Smooths noise and shows the trend direction.', example: '20 EMA sloping up = short-term uptrend.' },
            { term: 'ATR (Average True Range)', category: 'ANALYSIS', icon: '🌊', simple: 'How far price typically moves per bar.', why: 'Sets realistic stop distances so noise does not stop you out.', example: 'ATR 6 pts on MES 5-min: a 2 pt stop is too tight.' },
            { term: 'Bid-Ask Spread', category: 'MARKET STRUCTURE', icon: '↔️', simple: 'The gap between the best buy price and best sell price.', why: 'It is a hidden cost on every market order.', example: 'Bid 5,000.00 / Ask 5,000.25 = 1 tick spread.' },
            { term: 'Liquidity', category: 'MARKET STRUCTURE', icon: '💧', simple: 'How easily you can trade without moving the price.', why: 'Thin markets mean slippage and surprise fills.', example: 'MES at 10 AM ET is very liquid; at 3 AM it is thin.' },
            { term: 'Higher Highs / Higher Lows', category: 'MARKET STRUCTURE', icon: '🪜', simple: 'An uptrend makes each swing high and low above the last.', why: 'Breaking the pattern warns the trend may be ending.', example: 'Lows at 4,980 → 4,990 → 5,000 = higher lows.' },
            { term: 'TICK', category: 'FUTURES', icon: '📏', simple: 'Duplicate casing test entry.', why: 'Should be deduped.', example: '-' },
            { term: 'risk-to-reward ratio (r/r)', category: 'RISK', icon: '⚖️', simple: 'Duplicate casing test entry.', why: 'Should be deduped.', example: '-' }
        ];
        // Merge + dedupe by lowercased term; existing entries win on collision.
        const dictionaryTerms = (() => {
            const seen = new Set(baseDictionaryTerms.map(t => t.term.trim().toLowerCase()));
            const out = [...baseDictionaryTerms];
            newDictionaryTerms.forEach(t => {
                const k = t.term.trim().toLowerCase();
                if (!seen.has(k)) { seen.add(k); out.push(t); }
            });
            return out;
        })();
        const DICT_CATS = [['ALL', 'All Terms'], ['LUCID', 'Lucid Rules'], ['FUTURES', 'Futures Mechanics'], ['RISK', 'Risk & Psychology'], ['ORDER TYPES', 'Order Types'], ['CONTRACTS', 'Contracts'], ['ANALYSIS', 'Analysis'], ['MARKET STRUCTURE', 'Market Structure']];

//@@ HELPERS
        const freshRun = n => Object.assign(JSON.parse(JSON.stringify(defaultState.activeRun)), { runNum: n });
        const capFor = (funded, profit) => !funded ? 40 : (profit >= 2000 ? 40 : profit >= 1000 ? 30 : 20);
        const assetOf = sym => appState.settings.assets[sym];

        function unitsText(sym, micros) {
            const a = assetOf(sym);
            if (!a || !a.unitsPerMicro) return `${micros} micros (${a ? a.mini : sym} index contract, no physical units)`;
            const u = +(micros * a.unitsPerMicro).toFixed(4);
            return `${micros} micros ≈ ${u.toLocaleString('en-US')} ${a.unit}`;
        }

        function sizeCell(t) {
            const main = t.sizeUnit === 'minis' ? `${t.contracts / 10} Minis` : `${t.contracts} Micros`;
            return `${main}<div class="text-[10px] text-slate-500">${unitsText(t.symbol, t.contracts).replace(/^\d+ micros /, '')}</div>`;
        }

        const BADGES = [
            { id: 'first_trade', title: 'First Trade', icon: '⭐', desc: 'Logged your 1st paper trade', test: (m, T) => T.length > 0 },
            { id: 'green_day', title: 'Green Day', icon: '🍃', desc: 'Hit +$150 USD net profit day', test: (m, T) => { const d = {}; T.forEach(t => d[t.date] = (d[t.date] || 0) + t.pnl); return Object.values(d).some(v => v >= 150); } },
            { id: 'consistency', title: 'Consistency Master', icon: '🎯', desc: '50% consistency rule passing', test: m => m.totalWinProfit > 0 && m.consistencyPct <= 50 },
            { id: 'eval_passed', title: 'Eval Passed', icon: '🎓', desc: 'Reached the Funded stage', test: m => m.funded },
            { id: 'first_payout', title: 'First Payout', icon: '💰', desc: 'Requested 1st profit payout', test: m => m.payN > 0 },
            { id: 'champion', title: 'Battle Pass Champion', icon: '🏆', desc: 'Completed all 5 payouts', test: m => m.complete },
            { id: 'calc_scholar', title: 'Calculator Scholar', icon: '🧮', desc: 'Calculated safe contract size', test: () => true },
            { id: 'rule_follower', title: 'Rule Follower', icon: '📜', desc: 'Maintained discipline checklist', test: () => true },
        ];
        const earnedBadgeIds = m => {
            const T = (appState.activeRun.trades || []).filter(t => !m.ignored.has(t.id));
            return BADGES.filter(b => b.test(m, T)).map(b => b.id);
        };

        function migrateHistory(h) {
            const o = String(h.outcome || '');
            const outcome = ['passed', 'failed', 'manual_reset'].includes(o) ? o : o.includes('BREACHED') ? 'failed' : o.includes('COMPLETED') ? 'passed' : 'manual_reset';
            return Object.assign({ blownReason: outcome === 'failed' ? 'EOD trailing drawdown (legacy run)' : null, badgesEarned: [] }, h, { outcome });
        }

        function archiveRun(outcome, m, reason) {
            const run = appState.activeRun;
            const nzd = (run.payouts || []).reduce((a, p) => m.ignored.has(p.id) ? a : a + p.gross * 0.9 * p.fx, 0);
            const rec = {
                runNum: run.runNum, outcome, blownReason: reason || null, badgesEarned: earnedBadgeIds(m),
                finalStage: m.stageNum, finalBalance: m.balance, payoutsUsd: m.paidUsd, payoutsNzd: nzd,
                dateEnded: fmtD(m.endDate || todayNZ()),
                trades: JSON.parse(JSON.stringify(run.trades || [])), payouts: JSON.parse(JSON.stringify(run.payouts || []))
            };
            appState.careerHistory.push(rec);
            appState.activeRun = freshRun(run.runNum + 1);
            lastLogDate = null;
            return rec;
        }

        // Atomic auto-reset: freeze -> snapshot as failed -> runNum++ -> fresh Stage 1.
        function enforceRules() {
            const m = replay();
            if (!m.breached) return null;
            return archiveRun('failed', m, m.blownReason);
        }

        function showBlownModal(rec) {
            document.getElementById('blownModalText').innerText = `Account blown — ${rec.blownReason}. Reset to Stage 1.`;
            document.getElementById('blownModalSub').innerText = `Run #${rec.runNum} was archived as a failed run on ${rec.dateEnded}. You are now on Run #${appState.activeRun.runNum} at ${usd(appState.settings.startingBalance)}.`;
            document.getElementById('modalBlown').classList.remove('hidden');
        }
        function closeBlownModal() { document.getElementById('modalBlown').classList.add('hidden'); }

        let pendingDeleteRun = null;
        function badgesUniqueTo(runNum) {
            const h = appState.careerHistory.find(x => x.runNum === runNum);
            const held = new Set(earnedBadgeIds(replay()));
            appState.careerHistory.forEach(x => { if (x.runNum !== runNum) (x.badgesEarned || []).forEach(id => held.add(id)); });
            return (h.badgesEarned || []).filter(id => !held.has(id));
        }
        function openDeleteRunModal(runNum) {
            pendingDeleteRun = runNum;
            const n = badgesUniqueTo(runNum).length;
            document.getElementById('deleteRunTitle').innerText = `Delete Run #${runNum}?`;
            document.getElementById('deleteRunText').innerText = `Delete Run #${runNum}? This revokes ${n} badge${n === 1 ? '' : 's'} and removes it from lifetime stats. Cannot be undone.`;
            document.getElementById('modalDeleteRun').classList.remove('hidden');
        }
        function closeDeleteRunModal() { pendingDeleteRun = null; document.getElementById('modalDeleteRun').classList.add('hidden'); }
        function confirmDeleteRun() {
            const id = pendingDeleteRun;
            appState.careerHistory = appState.careerHistory.filter(h => h.runNum !== id);
            closeDeleteRunModal();
            saveState();
            toast(`Run #${id} deleted. Lifetime stats recomputed.`);
        }

        const BANNER_KEY = 'lucidflex_reset_banner_dismissed';
        function renderBanners() {
            const off = sessionStorage.getItem(BANNER_KEY) === '1';
            document.querySelectorAll('.reset-banner').forEach(b => b.classList.toggle('hidden', off));
        }
        function dismissBanner() { sessionStorage.setItem(BANNER_KEY, '1'); renderBanners(); }

        function renderDictPills() {
            document.getElementById('dictCatPills').innerHTML = DICT_CATS.map(([c, label]) => {
                const on = c === activeDictCategory;
                return `<button onclick="setDictCategory('${c}')" data-testid="dict-cat-${c.toLowerCase().replace(/ /g, '-')}" class="px-3 py-1.5 rounded-xl font-bold whitespace-nowrap border ${on ? 'bg-amber-200 text-amber-900 border-amber-400 neon-stage' : 'bg-stone-100 text-slate-600 border-stone-200'}">${label}</button>`;
            }).join('');
        }

        function tradeMicros() {
            const q = parseFloat(document.getElementById('tradeContracts').value) || 0;
            return document.getElementById('tradeSizeUnit').value === 'minis' ? Math.round(q * 10) : Math.round(q);
        }

//@@ saveState
        function saveState() {
            const blown = enforceRules();
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(appState));
            } catch (e) {
                console.error("Failed saving state", e);
            }
            renderAll();
            if (blown) showBlownModal(blown);
            return blown;
        }

//@@ loadState
        function loadState() {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) appState = Object.assign(JSON.parse(JSON.stringify(defaultState)), JSON.parse(saved));
            } catch (e) {
                console.error("Failed loading state", e);
            }
            const ds = JSON.parse(JSON.stringify(defaultState.settings));
            appState.settings = Object.assign(ds, appState.settings || {});
            appState.settings.assets = Object.assign({}, ds.assets, appState.settings.assets || {});
            appState.activeRun = Object.assign(freshRun(appState.activeRun.runNum || 1), appState.activeRun);
            appState.careerHistory = (appState.careerHistory || []).map(migrateHistory);
            migrateRun(appState.activeRun);
        }

//@@ replay
        function replay(asOf, before) {
            const run = appState.activeRun;
            const inRange = x => before ? x.date < asOf : (!asOf || x.date <= asOf);
            const T = (run.trades || []).filter(inRange);
            const P = (run.payouts || []).filter(inRange);
            const days = [...new Set([...T.map(t => t.date), ...P.map(p => p.date)])].sort();
            const dayPnl = {};
            T.forEach(t => dayPnl[t.date] = (dayPnl[t.date] || 0) + t.pnl);
            const dll = appState.settings.dailyLossLimit;

            const R = { phase: 'EVAL', balance: 50000, hwm: 50000, eodThreshold: 48000, greens: [], payN: 0,
                        evalDays: {}, passDate: null, endDate: null, ignored: new Set(), tradePhase: {}, paidUsd: 0,
                        reasons: [], consistencyBreached: false };
            const setFloor = () => { R.eodThreshold = Math.max(48000, Math.min(R.hwm - 2000, R.phase === 'EVAL' ? 50100 : 50000)); };
            const blow = (d, dp) => { R.phase = 'BREACHED'; R.endDate = d; dp.forEach(x => R.ignored.add(x.id)); };

            for (const d of days) {
                const dt = T.filter(t => t.date === d), dp = P.filter(p => p.date === d);
                if (R.phase === 'BREACHED' || R.phase === 'COMPLETE') { dt.concat(dp).forEach(x => R.ignored.add(x.id)); continue; }

                if (dt.length) {
                    const n = dayPnl[d];
                    // Cap is set by the stage at the start of the trading day. No grace.
                    const cap = capFor(R.phase !== 'EVAL', R.balance - 50000);
                    const worst = Math.max(...dt.map(t => t.contracts || 0));
                    dt.forEach(t => R.tradePhase[t.id] = R.phase);
                    if (worst > cap) R.reasons.push(`position size overrun (${worst} micros vs ${cap}-micro ${R.phase === 'EVAL' ? 'Evaluation' : 'Funded'} cap)`);
                    if (n <= -dll) R.reasons.push(`daily loss limit breached (${usd(n)} on ${fmtD(d)}, limit ${usd(dll)})`);
                    R.balance += n;
                    if (R.phase === 'EVAL') R.evalDays[d] = n;
                    else if (n >= 150) R.greens.push(d);
                    R.hwm = Math.max(R.hwm, R.balance);
                    setFloor();
                    if (R.balance <= R.eodThreshold) R.reasons.push(`EOD trailing drawdown breached (balance ${usd(R.balance)} hit floor ${usd(R.eodThreshold)})`);
                    const cons = consistencyOf(R.evalDays);
                    if (R.phase === 'EVAL' && R.balance >= 53000 && cons.pct > 50) {
                        R.consistencyBreached = true;
                        R.reasons.push(`consistency rule violated (best day ${cons.pct.toFixed(1)}% of profit at target, max 50%)`);
                    }
                    if (R.reasons.length) { blow(d, dp); continue; }
                    if (R.phase === 'EVAL' && R.balance >= 53000 && cons.pct <= 50) {
                        R.phase = 'FUNDED'; R.passDate = d;
                        R.balance = 50000; R.hwm = 50000; setFloor(); R.greens = [];
                    }
                }
                for (const p of dp) {
                    if (R.phase === 'BREACHED') { R.ignored.add(p.id); continue; }
                    if (R.phase !== 'FUNDED') { R.ignored.add(p.id); continue; }
                    R.balance -= p.gross; R.payN++; R.paidUsd += p.gross * 0.9; R.greens = [];
                    if (R.balance <= R.eodThreshold) { R.reasons.push(`EOD trailing drawdown breached after payout (balance ${usd(R.balance)})`); R.phase = 'BREACHED'; R.endDate = d; }
                    else if (R.payN >= 5) { R.phase = 'COMPLETE'; R.endDate = d; }
                }
            }

            const profit = R.balance - 50000;
            const cons = consistencyOf(R.evalDays);
            const funded = !!R.passDate;
            const maxMicros = capFor(funded, profit);
            const maxPayout = Math.min(2000, Math.floor(Math.max(0, profit) * 0.5));
            const [first, ...rest] = R.reasons;
            return {
                phase: R.phase, funded, passDate: R.passDate, endDate: R.endDate,
                stageNum: !funded ? 1 : R.phase === 'COMPLETE' ? 4 : (R.payN >= 4 ? 3 : 2),
                netPnL: profit, profit, balance: R.balance, highWaterMark: R.hwm,
                eodThreshold: R.eodThreshold, bufferRemaining: Math.max(0, R.balance - R.eodThreshold),
                greens: R.greens, greenDays: R.greens.length,
                consistencyPct: cons.pct, maxWinDay: cons.max, totalWinProfit: Math.max(0, cons.total),
                maxMicros, maxMinis: maxMicros / 10,
                breached: R.phase === 'BREACHED', complete: R.phase === 'COMPLETE',
                blownReasons: R.reasons,
                blownReason: first ? first.charAt(0).toUpperCase() + first.slice(1) + (rest.length ? ` (also: ${rest.join('; ')})` : '') : null,
                consistencyBreached: R.consistencyBreached, dayPnl,
                payN: R.payN, paidUsd: R.paidUsd, maxPayout,
                canPay: R.phase === 'FUNDED' && R.greens.length >= 5 && maxPayout >= 500,
                ignored: R.ignored, tradePhase: R.tradePhase
            };
        }

//@@ calculateMetrics
        function calculateMetrics() {
            const m = replay();
            const run = appState.activeRun;
            run.balance = m.balance; run.highWaterMark = m.highWaterMark; run.eodThreshold = m.eodThreshold;
            run.payoutCount = m.payN; run.stage = m.stageNum; run.totalPayoutsUsd = m.paidUsd;
            run.positionCapMicros = m.maxMicros;
            run.consistencyBreached = m.consistencyBreached;
            run.dailyLossToday = Math.max(0, -(m.dayPnl[todayNZ()] || 0));
            return m;
        }

//@@ updateTradeHint
        function updateTradeHint() {
            const el = document.getElementById('tradeDateHint');
            const sizeEl = document.getElementById('tradeSizeHint');
            const d = document.getElementById('tradeDate').value;
            const sym = document.getElementById('tradeSymbol').value;
            const micros = tradeMicros();
            const cap = d ? replay(d, true).maxMicros : replay().maxMicros;
            const over = micros > cap;
            sizeEl.className = 'text-[11px] font-semibold -mt-1 ' + (over ? 'text-rose-500' : 'text-slate-500');
            sizeEl.innerHTML = `${micros} micros = ${micros / 10} minis • ${unitsText(sym, micros).replace(/^\d+ micros /, '')}<br>Stage cap on this date: <strong>${cap} micros / ${cap / 10} minis</strong> (${unitsText(sym, cap)})${over ? '<br>⚠ OVER CAP — saving this trade BLOWS the account and resets to Stage 1.' : ''}`;
            if (!d) { el.innerText = ''; return; }
            const pnl = parseFloat(document.getElementById('tradePnLUsd').value) || 0;
            const existing = (appState.activeRun.trades || []).filter(t => t.date === d).reduce((a, t) => a + t.pnl, 0);
            const total = existing + pnl;
            const dll = appState.settings.dailyLossLimit;
            el.innerHTML = `${fmtD(d)} total with this trade: <strong class="${total >= 0 ? 'text-emerald-700' : 'text-rose-600'}">${usd(total)}</strong>${total >= 150 ? ' 🍃 green day' : ''}${total <= -dll ? ` <strong class="text-rose-500">⚠ breaches the ${usd(dll)} daily loss limit</strong>` : ''}`;
        }

//@@ openLogTradeModal
        function openLogTradeModal() {
            const sel = document.getElementById('tradeSymbol');
            if (!sel.options.length) sel.innerHTML = Object.entries(appState.settings.assets).map(([k, a]) => `<option value="${k}">${k} - ${a.name}</option>`).join('');
            document.getElementById('tradeDate').value = lastLogDate || todayNZ();
            updateTradeHint();
            document.getElementById('modalLogTrade').classList.remove('hidden');
        }

//@@ saveLoggedTrade
        function saveLoggedTrade() {
            const date = document.getElementById('tradeDate').value;
            if (!date) { toast('Pick a trade date first.'); return; }
            const micros = tradeMicros();
            if (micros < 1) { toast('Position size must be at least 1 micro.'); return; }
            const before = replay().phase;
            appState.activeRun.trades.push({
                id: Date.now() + Math.random(),
                date,
                symbol: document.getElementById('tradeSymbol').value,
                side: document.getElementById('tradeSide').value,
                contracts: micros,
                sizeUnit: document.getElementById('tradeSizeUnit').value,
                pnl: parseFloat(document.getElementById('tradePnLUsd').value) || 0,
                emotion: document.getElementById('tradeEmotion').value,
                followed: document.getElementById('tradeFollowedRules').checked,
                notes: document.getElementById('tradeNotes').value || ''
            });
            lastLogDate = date;
            document.getElementById('tradeNotes').value = '';
            closeLogTradeModal();
            if (saveState()) return;
            const after = replay().phase;
            if (before !== after) {
                if (after === 'FUNDED') toast('🎉 Evaluation passed! You are now on a fresh $50,000 funded account.');
                else if (after === 'COMPLETE') toast('🏆 Battle pass complete!');
            } else toast('Trade saved for ' + fmtD(date) + '.');
        }

//@@ confirmResetRun
        function confirmResetRun() {
            if (!confirm("Archive this run and start a new one at $50,000? The finished run is saved in your Career tab.")) return;
            const m = replay();
            archiveRun(m.complete ? 'passed' : 'manual_reset', m, null);
            saveState();
        }

//@@ renderCareerSection
        function renderCareerSection() {
            const history = appState.careerHistory || [];
            const m = replay();
            const run = appState.activeRun;
            const activeNzd = (run.payouts || []).reduce((a, p) => m.ignored.has(p.id) ? a : a + p.gross * 0.9 * p.fx, 0);
            const totalPayoutsUsd = history.reduce((a, b) => a + (b.payoutsUsd || 0), 0) + m.paidUsd;
            const totalPayoutsNzd = history.reduce((a, b) => a + (b.payoutsNzd || 0), 0) + activeNzd;
            const cnt = o => history.filter(h => h.outcome === o).length;
            const passed = cnt('passed'), failed = cnt('failed'), resets = cnt('manual_reset');
            const stageNames = ['Evaluation', 'Funded 1-4', '5th Payout', 'Live Review'];
            const best = Math.max(m.stageNum, ...history.map(h => h.finalStage || 1));

            document.getElementById('cStatTotalRuns').innerText = history.length + 1;
            document.getElementById('cStatTotalUsd').innerText = usd(totalPayoutsUsd);
            document.getElementById('cStatTotalNzd').innerText = usd(totalPayoutsNzd);
            document.getElementById('cStatBestStage').innerText = stageNames[best - 1];
            document.getElementById('cStatWinRate').innerText = history.length ? `${((passed / history.length) * 100).toFixed(0)}%` : '—';
            document.getElementById('cStatWinSub').innerText = `${passed} passed / ${failed} failed / ${resets} reset`;

            const labels = { passed: ['PASSED 🏆', 'bg-emerald-100 text-emerald-800'], failed: ['FAILED 💔', 'bg-rose-100 text-rose-800'], manual_reset: ['RESET', 'bg-stone-200 text-slate-700'] };
            const tbody = document.getElementById('careerTableBody');
            const empty = document.getElementById('emptyCareerState');
            if (history.length === 0) {
                tbody.innerHTML = '';
                empty.classList.remove('hidden');
            } else {
                empty.classList.add('hidden');
                tbody.innerHTML = [...history].reverse().map(h => {
                    const [lbl, cls] = labels[h.outcome] || labels.manual_reset;
                    return `
                    <tr class="hover:bg-stone-50" data-testid="career-row-${h.runNum}">
                        <td class="p-3 font-bold">Run #${h.runNum}</td>
                        <td class="p-3"><span data-testid="career-outcome-${h.runNum}" class="px-2 py-0.5 rounded-full text-[10px] font-bold ${cls}">${lbl}</span>${h.blownReason ? `<div class="text-[10px] text-rose-400 mt-1 max-w-[260px]" data-testid="career-reason-${h.runNum}">${h.blownReason}</div>` : ''}</td>
                        <td class="p-3 font-semibold">Stage ${h.finalStage}</td>
                        <td class="p-3 font-bold num">${usd(h.finalBalance)}</td>
                        <td class="p-3 font-bold text-emerald-600 num">${usd(h.payoutsUsd)}</td>
                        <td class="p-3 font-bold text-teal-700 num">${usd(h.payoutsNzd)}</td>
                        <td class="p-3 text-slate-500">${h.dateEnded}</td>
                        <td class="p-3 text-right"><button onclick="openDeleteRunModal(${h.runNum})" data-testid="delete-run-btn-${h.runNum}" aria-label="Delete run" class="text-rose-400 hover:text-rose-600 font-bold">🗑</button></td>
                    </tr>`;
                }).join('');
            }
            renderBadges();
        }

//@@ renderBadges
        function renderBadges() {
            const held = new Set(earnedBadgeIds(replay()));
            (appState.careerHistory || []).forEach(h => (h.badgesEarned || []).forEach(id => held.add(id)));
            let html = '', count = 0;
            BADGES.forEach(b => {
                const unlocked = held.has(b.id);
                if (unlocked) count++;
                html += `
                    <div data-testid="badge-${b.id}" data-unlocked="${unlocked}" class="p-3 rounded-2xl border text-center space-y-1 ${unlocked ? 'bg-amber-50 border-amber-400 neon-stage' : 'bg-stone-50 border-stone-200 opacity-40'}">
                        <div class="text-2xl">${b.icon}</div>
                        <div class="font-bold text-xs text-slate-800">${b.title}</div>
                        <div class="text-[10px] text-slate-500">${b.desc}</div>
                    </div>`;
            });
            document.getElementById('badgesGrid').innerHTML = html;
            document.getElementById('badgeUnlockedCount').innerText = `${count} / ${BADGES.length} Unlocked`;
        }

//@@ runCalculator
        function runCalculator() {
            const sel = document.getElementById('calcSymbol');
            const assets = appState.settings.assets;
            if (!sel.options.length) sel.innerHTML = Object.entries(assets).map(([k, a]) => `<option value="${k}">${k} - ${a.name} ($${a.tickVal}/tick, ${a.tickSize} tick)</option>`).join('');
            const symbol = sel.value;
            const riskUsd = parseFloat(document.getElementById('calcRiskUsd').value) || 200;
            const entry = parseFloat(document.getElementById('calcEntryPrice').value) || 5000;
            const stop = parseFloat(document.getElementById('calcStopPrice').value) || 4990;
            const specs = assets[symbol];

            const pointDiff = Math.abs(entry - stop);
            const tickDiff = pointDiff / specs.tickSize;
            const riskPerMicro = tickDiff * specs.tickVal;

            let safeMicros = riskPerMicro > 0 ? Math.floor(riskUsd / riskPerMicro) : 0;
            safeMicros = Math.max(1, safeMicros);

            const m = calculateMetrics();
            const cappedMicros = Math.min(safeMicros, m.maxMicros);
            const totalActualRisk = cappedMicros * riskPerMicro;

            document.getElementById('calcCurrentCapBadge').innerText = `${m.maxMicros} Micros / ${m.maxMinis} Minis`;
            document.getElementById('calcCapUnits').innerText = `Cap in units: ${unitsText(symbol, m.maxMicros)}`;
            document.getElementById('calcResultMicros').innerText = cappedMicros;
            document.getElementById('calcResultMinis').innerText = `Or max ${(cappedMicros / 10).toFixed(1)} Minis`;
            document.getElementById('calcResultUnits').innerText = unitsText(symbol, cappedMicros);
            document.getElementById('calcResultPoints').innerText = `${pointDiff.toFixed(2)} pts (${tickDiff.toFixed(0)} ticks)`;
            document.getElementById('calcResultRiskPerMicro').innerText = `$${riskPerMicro.toFixed(2)} USD`;
            document.getElementById('calcResultTotalRisk').innerText = `$${totalActualRisk.toFixed(2)} USD`;

            document.getElementById('calcRecommendationBox').innerText = `💡 Plain English Advice: Trading ${cappedMicros} Micro contract(s) on ${symbol} (${unitsText(symbol, cappedMicros)}) with a ${pointDiff.toFixed(2)} pt stop loss risks exactly $${totalActualRisk.toFixed(2)} USD.`;
        }

//@@ setDictCategory
        function setDictCategory(cat) {
            activeDictCategory = cat;
            renderDictPills();
            renderDictionary();
        }
