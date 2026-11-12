#!/usr/bin/env python3
"""Generate the README's SVG assets (light + dark variants).

    python3 scripts/build_assets.py          # writes docs/assets/*.svg

Standard library only. GitHub renders README images through <img>: no scripts or web
fonts, but CSS animation, media queries and prefers-reduced-motion inside the SVG work.
Drawn at 880 px wide (the README column) so text renders close to 1:1. The palette is
shared with the maintainer's other repositories ("datasheet" palette).

Everything drawn here is illustrative: no measured number appears in any asset.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(
        paper="#F7F5F0",
        paper2="#EFECE4",
        rule="#D9D4C7",
        rule2="#BDB6A6",
        ink="#15171C",
        ink2="#353A44",
        graphite="#555C6A",
        signal="#1D4ED8",
        copper="#B4470E",
        fault="#C2261D",
    ),
    "dark": dict(
        paper="#10151D",
        paper2="#171E29",
        rule="#2A3341",
        rule2="#3B4656",
        ink="#ECE8E0",
        ink2="#CFCAC0",
        graphite="#A3ABB8",
        signal="#86A8FF",
        copper="#F0935C",
        fault="#FF7D73",
    ),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def base_css(t: dict[str, str]) -> str:
    return f"""
    .kick {{ font: 700 12.5px {MONO}; letter-spacing: .14em; fill: {t["ink"]}; }}
    .kick2 {{ font: 600 11px {MONO}; letter-spacing: .1em; fill: {t["graphite"]}; }}
    .h {{ font: 650 25px {SANS}; fill: {t["ink"]}; letter-spacing: -.014em; }}
    .sub {{ font: 500 12px {MONO}; fill: {t["ink2"]}; }}
    .cap {{ font: 600 10.5px {MONO}; fill: {t["graphite"]}; letter-spacing: .06em; }}
    .lbl {{ font: 600 11px {MONO}; fill: {t["ink"]}; }}
    .lbl2 {{ font: 500 10.5px {MONO}; fill: {t["graphite"]}; }}
    .title {{ font: 650 13px {SANS}; fill: {t["ink"]}; }}
    .box {{ fill: {t["paper2"]}; stroke: {t["rule2"]}; stroke-width: 1.2; }}
    .card {{ fill: {t["paper"]}; stroke: {t["ink"]}; stroke-width: 1.3; }}
    .wire {{ fill: none; stroke: {t["rule2"]}; stroke-width: 1.4; }}
    .ink {{ fill: none; stroke: {t["ink"]}; stroke-width: 1.4; }}
    .sig {{ fill: none; stroke: {t["signal"]}; stroke-width: 1.6; }}
    .cu {{ fill: none; stroke: {t["copper"]}; stroke-width: 1.8; }}
    .dash {{ stroke-dasharray: 4 4; }}
    .fs {{ fill: {t["signal"]}; }} .fc {{ fill: {t["copper"]}; }} .ff {{ fill: {t["fault"]}; }}
    .fg {{ fill: {t["graphite"]}; }} .fi {{ fill: {t["ink"]}; }} .fp {{ fill: {t["paper"]}; }}
    .chip {{ fill: {t["paper"]}; stroke: {t["rule2"]}; stroke-width: 1; }}
    .chipt {{ font: 600 10.5px {MONO}; fill: {t["ink2"]}; letter-spacing: .04em; }}
    """


def svg(
    w: int, h: int, title: str, desc: str, css: str, body: str, t: dict[str, str], defs: str = ""
) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f"<defs>{defs}</defs>\n<style>{css}\n"
        "    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }\n"
        f'</style>\n<rect width="{w}" height="{h}" rx="12" fill="{t["paper"]}"/>\n'
        f"{body}\n</svg>\n"
    )


def text(x: float, y: float, s: str, cls: str, anchor: str = "start", extra: str = "") -> str:
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    return f'<text x="{x}" y="{y}" class="{cls}"{a}{extra}>{esc(s)}</text>'


def chip(x: float, y: float, s: str, w: float | None = None) -> str:
    w = w or 14 + len(s) * 6.6
    return f'<rect x="{x}" y="{y}" width="{w:.0f}" height="22" rx="11" class="chip"/>' + text(
        x + w / 2, y + 15, s, "chipt", "middle"
    )


def accent_bar(t: dict[str, str], w: int) -> tuple[str, str]:
    defs = (
        '<linearGradient id="acc" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{t["signal"]}"/>'
        f'<stop offset=".6" stop-color="{t["copper"]}"/>'
        f'<stop offset="1" stop-color="{t["fault"]}"/></linearGradient>'
    )
    return defs, f'<rect x="24" y="14" width="{w - 48}" height="3" rx="1.5" fill="url(#acc)"/>'


# ───────────────────────────── banner ─────────────────────────────


def banner(t: dict[str, str], w: int = 880, h: int = 300, scale_note: bool = True) -> str:
    defs, bar = accent_bar(t, w)
    cycle = 9
    css = (
        base_css(t)
        + f"""
    .gpu {{ fill: {t["paper"]}; stroke: {t["ink"]}; stroke-width: 1.2; }}
    .stuck {{ stroke: {t["copper"]}; stroke-width: 2; }}
    .nic {{ fill: {t["paper"]}; stroke: {t["ink"]}; stroke-width: 1.2; }}
    .bad {{ fill: {t["fault"]}; stroke: {t["fault"]}; stroke-width: 2; fill-opacity: .22;
            animation: bad {cycle}s ease-in-out infinite; }}
    @keyframes bad {{ 0%, 30% {{ fill-opacity: 0; stroke-opacity: .2; }}
                     36%, 100% {{ fill-opacity: .22; stroke-opacity: 1; }} }}
    .badl {{ stroke: {t["fault"]}; stroke-width: 1.8; fill: none; stroke-dasharray: 3 4;
             animation: badl {cycle}s linear infinite; }}
    @keyframes badl {{ 0%, 30% {{ opacity: 0; }} 36%, 100% {{ opacity: 1; }} }}
    .ev1 {{ animation: ev1 {cycle}s step-end infinite; }}
    .ev2 {{ animation: ev2 {cycle}s step-end infinite; }}
    .ev3 {{ animation: ev3 {cycle}s step-end infinite; }}
    .vd {{ animation: vd {cycle}s step-end infinite; }}
    @keyframes ev1 {{ 0% {{ opacity: .25; }} 42% {{ opacity: 1; }} }}
    @keyframes ev2 {{ 0% {{ opacity: .25; }} 52% {{ opacity: 1; }} }}
    @keyframes ev3 {{ 0% {{ opacity: .25; }} 62% {{ opacity: 1; }} }}
    @keyframes vd {{ 0% {{ opacity: 0; }} 72% {{ opacity: 1; }} }}
    .flow {{ stroke-dasharray: 2 5; animation: flow 1.2s linear infinite; }}
    @keyframes flow {{ to {{ stroke-dashoffset: -14; }} }}
    """
    )
    b = [bar]
    # Left: wordmark and message.
    b.append(text(32, 58, "GOODPUT", "kick"))
    b.append(text(32, 78, "FAULT ATTRIBUTION · MULTI-NODE LLM TRAINING", "kick2"))
    b.append(text(32, 124, "Symptoms are global.", "h"))
    b.append('<text x="32" y="156" class="h">Causes are <tspan class="fc">local</tspan>.</text>')
    b.append(text(32, 190, "flight recorder × DCGM × RDMA counters", "sub"))
    b.append(text(32, 208, "→ topology join → culprit rank + component", "sub"))
    b.append(text(32, 226, "→ the smallest safe recovery", "sub"))
    x = 32
    for c in ("pre-alpha · M1a", "CPU-testable control plane", "Apache-2.0"):
        b.append(chip(x, 250, c))
        x += 14 + len(c) * 6.6 + 8

    # Right: leaf switch, two nodes x 4 GPUs (NIC on top), evidence converging on a verdict.
    b.append('<rect x="603" y="38" width="150" height="26" rx="5" class="card"/>')
    b.append(text(678, 55, "leaf switch", "lbl", "middle"))
    for i, nx in enumerate((512, 694)):
        b.append(f'<rect x="{nx}" y="100" width="150" height="72" rx="8" class="box"/>')
        b.append(text(nx + 10, 126, f"node-{i}", "lbl2"))
        for g in range(4):
            gx = nx + 12 + g * 33
            gcls = "gpu stuck" if 4 * i + g == 6 else "gpu"
            b.append(f'<rect x="{gx}" y="136" width="26" height="24" rx="3" class="{gcls}"/>')
            b.append(text(gx + 13, 152, f"{4 * i + g}", "lbl2", "middle"))
        px = nx + 95
        cls = "nic bad" if i == 1 else "nic"
        b.append(f'<rect x="{px}" y="92" width="44" height="18" rx="4" class="{cls}"/>')
        b.append(text(px + 22, 105, "nic", "lbl", "middle"))
        path = (
            f'<path d="M{px + 22} 92 L{px + 22} 64"'
            if i == 0
            else f'<path d="M{px + 22} 92 L{px + 22} 78 L730 78 L730 64"'
        )
        if i == 1:
            b.append(path + ' class="wire"/>')
            b.append(path + ' class="badl"/>')
        else:
            b.append(path + ' class="sig flow"/>')

    ev = [
        ("ev1", "flight recorder", "rank 6 stuck"),
        ("ev2", "rdma counters", "link_downed +1"),
        ("ev3", "dcgm", "gpu healthy"),
    ]
    for k, (cls, src, val) in enumerate(ev):
        x0 = 512 + k * 115
        b.append(f'<path d="M{x0 + 55} 226 L{x0 + 55} 240 L678 240 L678 250" class="wire {cls}"/>')
        b.append(
            f'<g class="{cls}"><rect x="{x0}" y="190" width="110" height="36" rx="6" '
            f'class="chip"/>'
            + text(x0 + 9, 205, src, "lbl2")
            + text(x0 + 9, 219, val, "lbl")
            + "</g>"
        )
    b.append(
        f'<g class="vd"><rect x="530" y="250" width="296" height="28" rx="14" '
        f'fill="{t["ink"]}"/>' + f'<text x="678" y="268" text-anchor="middle" class="lbl" '
        f'style="fill:{t["paper"]}">verdict  nic_link_down → node-1/nic</text></g>'
    )
    if scale_note:
        b.append(text(w - 24, 36, "illustrative", "cap", "end"))
    desc = (
        "Two nodes of four GPUs under a leaf switch. node-1's NIC link fails; evidence from "
        "the flight recorder, RDMA counters and DCGM converges on one verdict naming the "
        "port, not just the first rank to time out. Illustrative, not a measurement."
    )
    return svg(
        w, h, "goodput: symptoms are global, causes are local", desc, css, "\n".join(b), t, defs
    )


# ───────────────────────────── architecture ─────────────────────────────


def architecture(t: dict[str, str]) -> str:
    w, h = 880, 470
    defs, bar = accent_bar(t, w)
    defs += (
        f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" '
        f'fill="{t["ink2"]}"/></marker>'
        f'<marker id="arc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" '
        f'fill="{t["copper"]}"/></marker>'
    )
    css = (
        base_css(t)
        + f"""
    .arr {{ fill: none; stroke: {t["ink2"]}; stroke-width: 1.3; marker-end: url(#ar); }}
    .arrc {{ fill: none; stroke: {t["copper"]}; stroke-width: 1.6; marker-end: url(#arc); }}
    .hl {{ fill: {t["paper"]}; stroke: {t["copper"]}; stroke-width: 2; }}
    .zone {{ fill: none; stroke: {t["rule2"]}; stroke-width: 1.2; stroke-dasharray: 5 5; }}
    """
    )
    b = [
        bar,
        text(32, 46, "SYSTEM CONTEXT", "kick"),
        text(
            32,
            64,
            "out of the data path · attribution before action · ground truth isolated",
            "kick2",
        ),
    ]
    # System-under-test zone
    b.append('<rect x="20" y="82" width="840" height="276" rx="12" class="zone"/>')
    b.append(text(34, 100, "goodput · system under test", "cap"))

    # Node box
    b.append('<rect x="36" y="112" width="284" height="230" rx="10" class="box"/>')
    b.append(text(52, 134, "Node × N", "title"))
    b.append('<rect x="52" y="146" width="252" height="62" rx="7" class="card"/>')
    b.append(text(66, 168, "ranks", "lbl"))
    b.append(text(66, 186, "torchtitan + hooks", "lbl2"))
    b.append(text(66, 200, "progress beacon · flight recorder", "lbl2"))
    b.append('<rect x="52" y="222" width="252" height="62" rx="7" class="card"/>')
    b.append(text(66, 244, "node agent", "lbl"))
    b.append(text(66, 262, "liveness · DCGM · RDMA counters", "lbl2"))
    b.append(text(66, 276, "kernel log · host", "lbl2"))
    b.append('<path d="M178 208 L178 220" class="arr"/>')
    for i, (tier, lab) in enumerate([("0", "host mem"), ("1", "peer"), ("2", "durable")]):
        x = 52 + i * 86
        b.append(f'<rect x="{x}" y="296" width="80" height="34" rx="6" class="chip"/>')
        b.append(text(x + 40, 310, f"tier {tier}", "lbl", "middle"))
        b.append(text(x + 40, 324, lab, "lbl2", "middle"))

    # Controller
    b.append('<rect x="384" y="112" width="460" height="230" rx="10" class="box"/>')
    b.append(text(400, 134, "Controller · one per job", "title"))
    stages = [
        ("state", "machine"),
        ("correlator", "topology join"),
        ("classifier", "rules · model"),
        ("policy", "+ placer"),
    ]
    for i, (a, c) in enumerate(stages):
        x = 400 + i * 111
        cls = "hl" if i == 1 else "card"
        b.append(f'<rect x="{x}" y="150" width="98" height="58" rx="7" class="{cls}"/>')
        b.append(text(x + 49, 174, a, "lbl", "middle"))
        b.append(text(x + 49, 192, c, "lbl2", "middle"))
        if i < 3:
            b.append(f'<path d="M{x + 98} 179 L{x + 111} 179" class="arr"/>')
    b.append('<rect x="400" y="226" width="198" height="54" rx="7" class="card"/>')
    b.append(text(414, 248, "event log", "lbl"))
    b.append(text(414, 266, "append-only · all metrics", "lbl2"))
    b.append('<rect x="622" y="226" width="208" height="54" rx="7" class="card"/>')
    b.append(text(636, 248, "actions (with evidence)", "lbl"))
    b.append(text(636, 266, "reinit · restart · replace", "lbl2"))
    b.append('<path d="M782 208 L782 224" class="arr"/>')

    # node agent <-> controller
    b.append('<path d="M304 240 L344 240 L344 179 L398 179" class="arr"/>')
    b.append(text(350, 172, "events", "lbl2"))
    b.append('<path d="M726 280 L726 312 L362 312 L362 268 L306 268" class="arrc"/>')
    b.append(text(560, 306, "smallest safe action", "lbl2", "middle"))

    # Outside the system under test
    b.append('<rect x="36" y="374" width="300" height="62" rx="10" class="card dash"/>')
    b.append(text(52, 397, "faultlab", "lbl"))
    b.append(text(52, 415, "injects faults · ground-truth ledger", "lbl2"))
    b.append('<path d="M186 374 L186 344" class="arrc dash"/>')
    b.append('<rect x="544" y="374" width="300" height="62" rx="10" class="card dash"/>')
    b.append(text(560, 397, "bench", "lbl"))
    b.append(text(560, 415, "the only place ledger meets verdicts", "lbl2"))
    b.append('<path d="M694 374 L694 344" class="arr dash"/>')
    b.append('<path d="M336 405 L540 405" class="arr dash"/>')
    b.append(text(438, 398, "ledger", "lbl2", "middle"))
    b.append(text(438, 458, "import boundary enforced by a test (ADR-0004)", "cap", "middle"))
    desc = (
        "Each node runs ranks with lightweight hooks and a node agent with collectors. The "
        "controller's state machine, correlator (the topology join), classifier and policy "
        "turn anomalies into evidence-backed actions. faultlab injects faults and keeps the "
        "ground-truth ledger outside the system under test; only bench sees both."
    )
    return svg(w, h, "goodput architecture", desc, css, "\n".join(b), t, defs)


REPO = "github.com/nareshns2004/fault-tolerant-training-orchestrator"


def social(t: dict[str, str], repo: str) -> str:
    """1280 × 640 card: the banner scaled up, with the repository path underneath."""
    inner = banner(t, scale_note=False).split("\n", 1)[1].rsplit("</svg>", 1)[0]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">'
        f'<rect width="1280" height="640" fill="{t["paper"]}"/>'
        '<svg x="0" y="70" width="1280" height="436" viewBox="0 0 880 300">'
        "<style>* { animation: none !important; }</style>" + inner + "</svg>"
        f'<text x="640" y="590" text-anchor="middle" style="font: 600 22px {MONO}; '
        f'fill: {t["graphite"]}; letter-spacing: .04em">{esc(repo)}</text></svg>\n'
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(banner(t))
        (OUT / f"architecture-{name}.svg").write_text(architecture(t))
    # Social preview card for repository settings (rendered to PNG by scripts/render_png.sh).
    (OUT / "social-preview.svg").write_text(social(THEMES["light"], REPO))
    print(f"wrote {len(list(OUT.glob('*.svg')))} SVGs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
