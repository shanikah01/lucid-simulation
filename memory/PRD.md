# LucidFlex $50K Battle Pass — Hardened Update

## Original problem
Single-page HTML/JS paper-trading battle pass for LucidFlex $50K. Surgical edits to the user's baseline file: dark neon purple theme, unit conversion layer, stage-based hard position caps, auto-reset on rule break (archived as failed run), career run delete, dictionary merge + dedupe (+20 terms), reset warning banner.

## Architecture
- `/app/frontend/public/lucidflex-app.html`: the entire app (Tailwind CDN, Lucide icons CDN, localStorage key `lucidflex_battlepass_v1`)
- `/app/frontend/src/App.js`: full-screen iframe wrapper with a cache-busting query
- Patch scripts live in `/app/scripts/` (for reference only)
- No backend usage

## Implemented (Sep 2026)
- Dark neon purple theme, neon GREEN success, rose danger; neon-card/btn/badge/tab classes; glow on active tab/buttons/stage badge; blurred modal backdrops
- Emojis replaced with Lucide icons
- Instruments: Gold MGC, Silver SIL, Crude MCL only. Units come from `settings.assets` (MGC 10 oz/XAUUSD, SIL 1,000 oz/XAGUSD, MCL 100 bbl/USOIL). The calculator shows "or N units" next to every micro/mini figure, plus a conversion table
- Stage caps (Eval 40, Funded 20/30/40 by profit), evaluated at the start of each day inside replay(); 1 micro over = blown
- Auto-reset triggers: EOD drawdown, consistency (hitting the $53K target with best day >50%), position overrun. NO daily loss limit (DLL OFF, per user)
- Atomic archive → careerHistory {outcome, blownReason, badgesEarned, snapshot}. Blown modal. Backdated trades are handled by replay
- Career delete with confirmation; revokes unique badges; renumbers runs and resets the run count; recomputes win rate
- Dictionary: 20 new terms merged, deduped case-insensitively, new category pills
- Session-dismissible "HARD RULES ARMED" banner on Dashboard + Rules

- How-it-works guide screen: auto-opens on first visit, can be reopened from the header "Guide" button. Covers the TradingView paper-trading workflow in units, the hard rules, levelling/payouts and a daily routine

## Backlog
- P1: Editable cap/rule settings panel
- P2: Export/import career JSON backup
- P2: Per-trade edit (not just delete)
