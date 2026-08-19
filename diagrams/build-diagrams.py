#!/usr/bin/env python3
"""Build AIS-original setup schematics for the ais-learning-environment skill.

One SVG per setup, 30 in total, plus an index gallery. All artwork is generated
from the primitive layer below, so the visual language is changed in one place.

Run:  python3 build-diagrams.py
Out:  <strand-slug>/<setup-slug>.svg  and  index.html
"""

import os

W, H = 420, 280

STYLE = """<style>
  :root{--ink:#1f2430;--muted:#8b93a3;--line:#c9cedb;--wash:#f2f3f8;--paper:#fff;--accent:#6d4df6;--accent-wash:#ece7ff}
  @media (prefers-color-scheme: dark){
    :root{--ink:#e8eaf2;--muted:#8d95a8;--line:#3a4157;--wash:#1b2030;--paper:#111521;--accent:#9b86ff;--accent-wash:#241f3d}
  }
  .t{font:600 13px/1.2 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;fill:var(--ink)}
  .s{font:500 10px/1.2 ui-sans-serif,system-ui,sans-serif;fill:var(--muted);letter-spacing:.02em}
  .l{font:500 9.5px/1.2 ui-sans-serif,system-ui,sans-serif;fill:var(--ink)}
  .lm{font:500 9px/1.2 ui-sans-serif,system-ui,sans-serif;fill:var(--muted)}
  .la{font:600 9.5px/1.2 ui-sans-serif,system-ui,sans-serif;fill:var(--accent)}
  .halo{paint-order:stroke;stroke:var(--paper);stroke-width:3.5px;stroke-linejoin:round}
  .stroke{fill:none;stroke:var(--line);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
  .acc{fill:none;stroke:var(--accent);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
  .fillw{fill:var(--wash)}
  .filla{fill:var(--accent-wash)}
  .fillp{fill:var(--paper)}
  .dash{stroke-dasharray:4 3}
</style>"""


# ---------- primitives -------------------------------------------------------

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def txt(x, y, t, cls="l", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(t)}</text>'


def rect(x, y, w, h, r=3, cls="stroke", fill=None):
    f = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{fill}"/>' if fill else ""
    return f + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def panel(x, y, w, h, label=None, accent=False, lines=0):
    """A wall panel or board."""
    out = rect(x, y, w, h, 4, "acc" if accent else "stroke", "filla" if accent else "fillw")
    for i in range(lines):
        yy = y + h * (i + 1) / (lines + 1)
        out += f'<line x1="{x+8}" y1="{yy:.1f}" x2="{x+w-8}" y2="{yy:.1f}" class="stroke dash"/>'
    if label:
        out += txt(x + w / 2, y + h + 12, label, "la" if accent else "lm", "middle")
    return out


def desk(x, y, w=64, h=34, label=None, accent=False):
    out = rect(x, y, w, h, 4, "acc" if accent else "stroke", "filla" if accent else "fillp")
    if label:
        out += txt(x + w / 2, y + h / 2 + 3.5, label, "l", "middle")
    return out


def pupil(cx, cy, r=7, filled=False, accent=False):
    cls = "acc" if accent else "stroke"
    fill = "filla" if (filled and accent) else ("fillw" if filled else None)
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" class="{fill}"/>' if fill else ""
    return out + f'<circle cx="{cx}" cy="{cy}" r="{r}" class="{cls}"/>'


def teacher(cx, cy, r=8):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" class="filla"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" class="acc"/>'
            f'<text x="{cx}" y="{cy+3.2}" class="la" text-anchor="middle">T</text>')


def door(x, y, h=54, label="door"):
    out = rect(x, y, 12, h, 2, "stroke", "fillw")
    out += f'<path d="M{x+12} {y} A{h*0.7} {h*0.7} 0 0 1 {x+12+h*0.34} {y+h*0.5}" class="stroke dash"/>'
    if label:
        out += txt(x + 6, y + h + 12, label, "lm", "middle")
    return out


def arrow(x1, y1, x2, y2, dashed=False, accent=True, label=None):
    cls = ("acc" if accent else "stroke") + (" dash" if dashed else "")
    head = 4.6
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - head * math.cos(a), y2 - head * math.sin(a)
    p1 = (hx - head * math.cos(a - 0.5), hy - head * math.sin(a - 0.5))
    p2 = (hx - head * math.cos(a + 0.5), hy - head * math.sin(a + 0.5))
    out = (f'<line x1="{x1}" y1="{y1}" x2="{hx:.1f}" y2="{hy:.1f}" class="{cls}"/>'
           f'<path d="M{x2} {y2} L{p1[0]:.1f} {p1[1]:.1f} M{x2} {y2} L{p2[0]:.1f} {p2[1]:.1f}" '
           f'class="{"acc" if accent else "stroke"}"/>')
    if label:
        cl = ("la" if accent else "lm") + " halo"
        out += txt((x1 + x2) / 2, (y1 + y2) / 2 - 9, label, cl, "middle")
    return out


def note(x, y, s=18, accent=False, mark=None):
    out = rect(x, y, s, s, 2, "acc" if accent else "stroke", "filla" if accent else "fillw")
    if mark:
        out += txt(x + s / 2, y + s / 2 + 3.5, mark, "la" if accent else "lm", "middle")
    return out


def card(x, y, w, h, t=None, accent=False):
    out = rect(x, y, w, h, 2, "acc" if accent else "stroke", "filla" if accent else "fillp")
    if t:
        out += txt(x + w / 2, y + h / 2 + 3.4, t, "la" if accent else "l", "middle")
    return out


def pen(x, y, accent=True):
    cls = "acc" if accent else "stroke"
    return (f'<line x1="{x}" y1="{y}" x2="{x+14}" y2="{y-8}" class="{cls}"/>'
            f'<path d="M{x+14} {y-8} l4 -2 -2 4 z" class="{cls}"/>')


def floorline(y=236):
    return f'<line x1="16" y1="{y}" x2="{W-16}" y2="{y}" class="stroke"/>'


def timer(cx, cy, t, r=13):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" class="fillw"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" class="stroke"/>'
            f'<text x="{cx}" y="{cy+3.4}" class="la" text-anchor="middle">{esc(t)}</text>')


def table_of_four(cx, cy, accent_pupils=(), labels=("1", "2", "3", "4")):
    """Square table seen from above with four pupils."""
    out = rect(cx - 30, cy - 22, 60, 44, 4, "stroke", "fillp")
    pos = [(cx - 44, cy - 10), (cx + 44, cy - 10), (cx - 44, cy + 12), (cx + 44, cy + 12)]
    for i, (px, py) in enumerate(pos):
        acc = i in accent_pupils
        out += pupil(px, py, 8, filled=acc, accent=acc)
        if labels:
            out += txt(px, py + 3.4, labels[i], "la" if acc else "lm", "middle")
    return out


# ---------- page assembly ----------------------------------------------------

def svg(title, sub, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title><desc>{esc(sub)}</desc>{STYLE}'
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="none"/>'
            f'{txt(20, 26, title, "t")}{txt(20, 42, sub, "s")}'
            f'<g>{body}</g></svg>')


SCENES = []


def scene(strand, slug, title, sub, body):
    SCENES.append((strand, slug, title, sub, body))


# ===== Strand 1: metacognition and self-regulated learning ===================
S1 = "01-metacognition-self-regulation"

scene(S1, "stuck-ladder", "Stuck ladder", "Door frame · prep 5 min · runs itself",
      door(30, 90) +
      "".join(card(70, 78 + i * 26, 150, 20, f"{i+1}. {t}", accent=(i == 2))
              for i, t in enumerate(["reread the question", "check the model",
                                     "check my book", "ask my partner",
                                     "try one line", "ask the teacher"])) +
      pupil(258, 130, 8) + arrow(268, 130, 300, 130, label="rung 3") +
      txt(300, 152, "pupil names the rung", "lm") + floorline(248))

scene(S1, "live-model-mistakes", "Live model, mistakes left in", "Working wall · prep 0 · 6 min in lesson",
      panel(28, 70, 190, 130, "your attempt, not tidied", accent=True, lines=5) +
      f'<path d="M60 108 l40 0 M64 134 l30 0" class="acc"/>' +
      note(150, 96, 18, True, "✕") + note(150, 150, 18, True, "✕") +
      arrow(228, 112, 262, 112) + txt(266, 100, "\"here I stopped", "l") +
      txt(266, 114, "and checked\"", "l") +
      arrow(228, 168, 262, 168) + txt(266, 156, "\"here I changed", "l") +
      txt(266, 170, "my mind because\"", "l"))

scene(S1, "plan-boxes", "Plan boxes on the tabletop", "Desk · prep 10 min once · 90 seconds",
      desk(60, 96, 300, 96) +
      "".join(card(74 + i * 96, 112, 84, 44, None) for i in range(3)) +
      txt(116, 130, "what am I", "l", "middle") + txt(116, 142, "making", "l", "middle") +
      txt(212, 130, "what makes", "l", "middle") + txt(212, 142, "it good", "l", "middle") +
      txt(308, 130, "first move", "la", "middle") + txt(308, 142, "✓", "la", "middle") +
      timer(390, 74, "90s") + pupil(46, 120, 8) + pupil(46, 168, 8) +
      txt(210, 214, "one sleeve per pair, marker, pens down after 90 seconds", "lm", "middle"))

scene(S1, "two-colour-check", "Two colour check", "Books · prep 5 min once · last 5 min",
      panel(28, 72, 120, 96, "3 checks, front of room", lines=3) +
      rect(180, 72, 210, 130, 4, "stroke", "fillp") +
      "".join(f'<line x1="196" y1="{92+i*20}" x2="374" y2="{92+i*20}" class="stroke"/>' for i in range(5)) +
      f'<path d="M204 104 l52 0 M204 144 l70 0" class="acc"/>' +
      pen(300, 190) + txt(210, 226, "second colour only: nothing new, only better", "la", "middle"))

scene(S1, "exit-strip", "Exit strip", "Back of door · prep 10 min · 60 seconds",
      door(24, 84, 108, "inside the door") +
      "".join(card(62 + i * 100, 90, 88, 46, t, accent=(i == 1))
              for i, t in enumerate(["got it", "nearly", "lost me"])) +
      note(84, 146, 16, False) + note(184, 146, 16, True) + note(284, 146, 16, False) +
      arrow(240, 190, 200, 168) + txt(252, 192, "named note", "la") +
      txt(210, 228, "read in 90 seconds, sets the next lesson's first 3 minutes", "lm", "middle"))

# ===== Strand 2: emotional engagement =======================================
S2 = "02-emotional-engagement"

scene(S2, "covered-object", "Covered object", "Front bench · prep 2 min · 3 min in lesson",
      desk(200, 152, 140, 46) +
      f'<path d="M218 152 q52 -50 104 0 z" class="filla"/><path d="M218 152 q52 -50 104 0" class="acc"/>' +
      txt(270, 96, "covered all lesson", "la", "middle") +
      arrow(270, 106, 270, 122, accent=True) +
      pupil(58, 148, 8) + pupil(58, 176, 8) + pupil(88, 162, 8) +
      arrow(104, 162, 190, 162, dashed=True) +
      txt(147, 148, "1 closed question each", "lm halo", "middle") +
      txt(210, 232, "uncovered only when the content needs it", "lm", "middle"))

scene(S2, "wrong-answer-wall", "Wrong answer wall", "One wall panel · prep 5 min · 4 min weekly",
      panel(28, 66, 250, 146, "plausible wrong answers, unnamed") +
      "".join(note(44 + (i % 4) * 56, 82 + (i // 4) * 46, 20, accent=(i == 5)) for i in range(11)) +
      arrow(288, 132, 322, 132, label="pick one") +
      card(326, 108, 76, 48, "dismantle", True) +
      txt(210, 244, "\"which of these would fool a sensible person?\"", "lm", "middle"))

scene(S2, "threshold-question", "Threshold question", "Door · prep 1 min · 3 min in lesson",
      door(40, 104) + card(60, 112, 112, 40, "one question", True) +
      txt(210, 82, "crossing the threshold", "la", "middle") +
      arrow(178, 132, 218, 132) +
      pupil(238, 118, 8) + pupil(262, 132, 8) + pupil(238, 146, 8) +
      teacher(346, 132) + arrow(282, 132, 330, 132, dashed=True) +
      txt(210, 200, "answered out loud or on a note, never assessed", "lm", "middle") +
      txt(210, 218, "3 pupils asked back by name once seated", "la", "middle") + floorline(240))

scene(S2, "pupil-owned-corner", "The Pupil Corner", "1 metre square · prep 10 min · weekly",
      f'<path d="M28 200 L28 76 L152 76" class="stroke"/>' +
      panel(36, 84, 108, 108, "curated by the students", accent=True) +
      note(52, 100, 22, True) + card(84, 100, 48, 22, "clipping") +
      card(52, 136, 80, 22, "artefact") + card(52, 166, 80, 18, "open question") +
      pupil(176, 120, 8) + pupil(176, 148, 8) +
      txt(212, 108, "60 second", "la", "middle") + txt(212, 120, "present", "la", "middle") +
      arrow(192, 134, 244, 134) +
      card(252, 114, 140, 44, None, True) +
      txt(322, 132, "you build the next 5 min on it", "la", "middle") +
      txt(210, 236, "fortnightly rotation", "lm", "middle"))

scene(S2, "countdown-reveal", "Countdown reveal", "Wall strip · prep 15 min per unit · 2 min",
      "".join(card(30 + i * 62, 110, 52, 56, str(i + 1), accent=(i == 3)) for i in range(6)) +
      "".join(txt(56 + i * 62, 182, "turned", "lm", "middle") for i in range(4)) +
      txt(304, 182, "still hidden", "lm", "middle") + txt(366, 182, "resolves it", "lm", "middle") +
      arrow(210, 92, 210, 104) + txt(210, 84, "one card per lesson", "la", "middle") +
      txt(210, 216, "\"what does card 4 change about Tuesday?\"", "lm", "middle"))

# ===== Strand 3: retrieval and revision =====================================
S3 = "03-retrieval-and-revision"

scene(S3, "three-shelf-wall", "Three shelf knowledge wall", "One wall · prep 20 min · 5 min starter",
      panel(28, 72, 300, 34, None) + txt(178, 94, "band 1 · this fortnight · 1 question", "l", "middle") +
      panel(28, 116, 300, 34, None) + txt(178, 138, "band 2 · this term · 2 questions", "l", "middle") +
      panel(28, 160, 300, 34, None, accent=True) + txt(178, 182, "band 3 · last year · 3 questions", "la", "middle") +
      arrow(344, 88, 344, 176, dashed=True, label=None) +
      txt(352, 134, "items age", "lm") + txt(352, 148, "downward,", "lm") + txt(352, 162, "never removed", "lm") +
      txt(178, 224, "\"two from the bottom shelf first\"", "lm", "middle"))

scene(S3, "blank-first-book-second", "Blank first, book second", "Books · prep 0 · 5 min",
      rect(40, 90, 150, 104, 4, "stroke", "fillw") + txt(115, 126, "shut", "l", "middle") +
      txt(115, 142, "silent", "l", "middle") + timer(115, 172, "3m") +
      arrow(200, 142, 236, 142) +
      rect(246, 90, 150, 104, 4, "acc", "filla") +
      "".join(f'<line x1="262" y1="{112+i*18}" x2="380" y2="{112+i*18}" class="stroke"/>' for i in range(4)) +
      pen(340, 186) + txt(321, 100, "correct in 2nd colour", "la", "middle") +
      txt(210, 226, "the corrections are the diagnostic, not the score", "lm", "middle"))

scene(S3, "question-grid", "Question grid on the tabletop", "Desk · prep 30 min per unit · 5 min",
      "".join("".join(card(96 + c * 34, 84 + r * 22, 32, 20, None,
                          accent=(r == 3 and c == 4)) for c in range(6)) for r in range(6)) +
      "".join(txt(112 + c * 34, 78, str(c + 1), "lm", "middle") for c in range(6)) +
      "".join(txt(88, 98 + r * 22, str(r + 1), "lm", "middle") for r in range(6)) +
      card(316, 148, 20, 20, "5", True) + card(340, 148, 20, 20, "4", True) +
      txt(328, 140, "roll", "lm", "middle") +
      pupil(56, 130, 8) + pupil(56, 158, 8) + arrow(56, 176, 56, 196, dashed=True) +
      txt(56, 212, "pairs,", "lm", "middle") + txt(56, 224, "out loud", "lm", "middle") +
      txt(240, 232, "4 rolls each, partner checks the answer card", "lm", "middle"))

scene(S3, "forgetting-queue", "Forgetting queue", "Back wall or corridor · prep 10 min · 3 min",
      f'<line x1="28" y1="96" x2="392" y2="96" class="stroke"/>' +
      "".join(card(36 + i * 52, 104, 44, 44, None, accent=(i < 2)) for i in range(5)) +
      "".join(f'<line x1="{58+i*52}" y1="96" x2="{58+i*52}" y2="104" class="stroke"/>' for i in range(5)) +
      txt(120, 172, "questions the class fluffed, dated", "lm", "middle") +
      txt(320, 88, "beaten twice", "la", "middle") +
      arrow(292, 126, 330, 126) +
      panel(338, 104, 54, 44, "retired pile", accent=True) +
      txt(210, 216, "\"two off the queue. beat them and they come down\"", "lm", "middle"))

scene(S3, "twenty-word-strip", "Twenty word summary strip", "Wall strip · prep 10 min · 3 min",
      "".join(card(28 + i * 90, 96, 84, 40, f"lesson {i+1}", accent=(i == 3)) for i in range(4)) +
      "".join("".join(f'<rect x="{34+i*90+c*8}" y="{142}" width="6" height="10" rx="1" class="stroke"/>'
                     for c in range(9)) for i in range(4)) +
      txt(210, 176, "exactly twenty boxes, exactly twenty words", "lm", "middle") +
      arrow(210, 196, 210, 214, dashed=True) +
      txt(210, 232, "the finished strip is the unit's revision spine", "la", "middle"))

# ===== Strand 4: responsive teaching ========================================
S4 = "04-responsive-teaching"

scene(S4, "response-boards", "Whole class response boards", "Every desk · prep 10 min · 8 seconds",
      "".join(card(40 + (i % 4) * 88, 92 + (i // 4) * 60, 58, 38, None, accent=(i in (2, 5)))
              for i in range(8)) +
      "".join(pupil(69 + (i % 4) * 88, 142 + (i // 4) * 60, 6) for i in range(8)) +
      teacher(210, 222) + arrow(192, 214, 120, 190, dashed=True) + arrow(228, 214, 300, 190, dashed=True) +
      txt(210, 252, "scan, say what you saw, then move on or reteach", "lm", "middle") +
      txt(210, 74, "boards up on three · nothing collected", "la", "middle"))

scene(S4, "hinge-point", "Hinge point", "Mid lesson · prep 15 min per question · 2 min",
      panel(28, 72, 176, 96, "one question, 4 options") +
      "".join(txt(44, 96 + i * 20, f"{c}  {t}", "la" if c == "B" else "l")
              for i, (c, t) in enumerate([("A", "misconception 1"), ("B", "correct"),
                                          ("C", "misconception 2"), ("D", "misconception 3")])) +
      "".join(pupil(230 + (i % 3) * 26, 92 + (i // 3) * 26, 8, filled=(i in (1, 4)), accent=(i in (1, 4)))
              for i in range(9)) +
      txt(256, 160, "answered at once", "lm", "middle") +
      card(28, 186, 176, 42, "strong → move on", True) + card(214, 186, 176, 42, "weak → reteach now", True) +
      txt(210, 248, "two next moves prepared before the lesson", "lm", "middle"))

scene(S4, "weighted-name-draw", "Weighted name draw", "Jar on desk · prep 10 min · no extra time",
      f'<path d="M150 118 l8 84 q52 14 104 0 l8 -84 z" class="fillw"/>'
      f'<path d="M150 118 l8 84 q52 14 104 0 l8 -84 z" class="stroke"/>'
      f'<rect x="146" y="108" width="128" height="12" rx="3" class="stroke"/>' +
      "".join(f'<line x1="{168+i*14}" y1="{96+ (i%3)*6}" x2="{172+i*14}" y2="128" '
              f'class="{"acc" if i in (2,3,6) else "stroke"}"/>' for i in range(8)) +
      txt(210, 84, "duplicates for pupils you must hear from", "la", "middle") +
      arrow(288, 150, 330, 150, label="draw") + pupil(352, 150, 9) +
      arrow(330, 178, 288, 178, dashed=True, label=None) + txt(348, 182, "stick returns", "lm", "middle") +
      txt(210, 232, "thinking time first, then draw. nobody is safe after their turn", "lm", "middle"))

scene(S4, "traffic-light-margin", "Traffic light margin", "Pupil books · prep 0 · 90 seconds",
      rect(80, 78, 260, 138, 4, "stroke", "fillp") +
      f'<line x1="112" y1="78" x2="112" y2="216" class="stroke"/>' +
      "".join(f'<line x1="126" y1="{100+i*22}" x2="322" y2="{100+i*22}" class="stroke"/>' for i in range(6)) +
      card(92, 158, 14, 14, None, True) +
      arrow(60, 165, 82, 165, label=None) + txt(56, 152, "the line", "la", "end") +
      txt(56, 166, "it went wrong", "la", "end") + txt(56, 180, "not the page", "lm", "end") +
      txt(210, 246, "circulate reading margins only: a class takes about 90 seconds", "lm", "middle"))

scene(S4, "two-seat-surgery", "Two seat surgery", "Side table · prep 0 · 4 min",
      desk(256, 74, 120, 48, "surgery", True) +
      pupil(276, 140, 9, True, True) + pupil(306, 140, 9, True, True) + teacher(350, 140) +
      timer(398, 98, "4m") +
      "".join(desk(28 + (i % 2) * 88, 78 + (i // 2) * 54, 74, 36) for i in range(6)) +
      txt(210, 196, "named by the check", "la", "middle") +
      arrow(150, 188, 262, 156, dashed=True) +
      txt(210, 244, "rotate the seats visibly: normal, not remedial", "lm", "middle"))

# ===== Strand 5: oracy and word wealth ======================================
S5 = "05-oracy-and-word-wealth"

scene(S5, "sentence-stem-strip", "Sentence stem strip", "Wall pupils face · prep 10 min · no extra time",
      panel(24, 74, 372, 30, None) +
      txt(40, 93, "the evidence for that is    ·    I would challenge that because", "l") +
      panel(24, 112, 372, 30, None, accent=True) +
      txt(40, 131, "building on what Layla said    ·    that only works if", "la") +
      pupil(56, 186, 9) + arrow(68, 182, 112, 152, dashed=True) +
      txt(226, 190, "answers must start with a stem", "la", "middle") +
      txt(210, 210, "pupils may point at the one they are about to use", "lm", "middle") +
      txt(210, 234, "seated eye height · refreshed each half term", "lm", "middle"))

scene(S5, "takeable-word-wall", "Word wall pupils take words off", "Board · prep 20 min per unit · 1 min",
      panel(28, 72, 190, 128, "removable cards, not a printed list") +
      "".join(card(42 + (i % 3) * 58, 88 + (i // 3) * 38, 50, 26, None, accent=(i in (1, 4)))
              for i in range(9)) +
      arrow(228, 118, 268, 118, label="takes 2") +
      desk(276, 96, 116, 60) + card(288, 108, 44, 20, None, True) + card(336, 108, 44, 20, None, True) +
      txt(334, 146, "both words appear", "la", "middle") + txt(334, 160, "in the paragraph", "la", "middle") +
      arrow(268, 178, 228, 178, dashed=True) + txt(300, 192, "card returns", "lm", "middle") +
      txt(210, 244, "cards nobody takes are dead words: replace them", "lm", "middle"))

scene(S5, "talk-roles", "Talk roles on the table", "Table centre · prep 15 min · 4 min",
      table_of_four(200, 140, accent_pupils=(2,), labels=("B", "C", "S", "E")) +
      card(170, 126, 60, 28, "roles", True) +
      txt(64, 90, "B  builder", "l") + txt(64, 106, "C  challenger", "l") +
      txt(276, 90, "S  summariser", "la") + txt(276, 106, "E  evidence keeper", "l") +
      arrow(200, 178, 200, 200, label=None) +
      txt(200, 216, "summariser reports in one sentence and names who said what", "lm", "middle") +
      txt(200, 240, "take three summarisers, not one · roles rotate every discussion", "lm", "middle"))

scene(S5, "etymology-corner", "Etymology corner", "Small panel · prep 5 min per fortnight · 2 min",
      panel(96, 70, 228, 44, None, accent=True) +
      txt(210, 97, "pre · fix · root · suffix", "la", "middle") +
      "".join(arrow(210, 118, 118 + i * 92, 150, dashed=True) for i in range(3)) +
      "".join(card(78 + i * 92, 154, 84, 30, ["same root", "same root", "other subject"][i],
                   accent=(i == 2)) for i in range(3)) +
      txt(210, 208, "pupils add relatives they find", "lm", "middle") +
      txt(210, 232, "a mechanism for unfamiliar words, not a list to memorise", "lm", "middle"))

scene(S5, "sixty-second-talk", "Sixty second subject talk", "Marked floor spot · prep 2 min · 2 min",
      f'<ellipse cx="120" cy="196" rx="34" ry="12" class="filla"/>'
      f'<ellipse cx="120" cy="196" rx="34" ry="12" class="acc dash"/>' +
      pupil(120, 172, 10, True, True) + timer(178, 150, "60s") +
      "".join(pupil(246 + (i % 4) * 30, 150 + (i // 4) * 30, 8) for i in range(8)) +
      txt(306, 122, "listening for the two words", "lm", "middle") +
      card(60, 92, 120, 30, "prompt card", True) +
      txt(210, 226, "minimum two words off the word wall · class signals when they hear them", "lm", "middle"))

# ===== Strand 6: collaborative learning =====================================
S6 = "06-collaborative-learning"

scene(S6, "one-pen-four-hands", "One pen, four hands", "Table of four · prep 1 min · 10 min",
      rect(140, 82, 140, 96, 4, "stroke", "fillp") + txt(210, 98, "one A3 sheet", "lm", "middle") +
      "".join(f'<line x1="156" y1="{112+i*16}" x2="264" y2="{112+i*16}" class="stroke"/>' for i in range(4)) +
      pen(226, 168) +
      pupil(104, 104, 10, True, True) + pupil(104, 156, 10) + pupil(316, 104, 10) + pupil(316, 156, 10) +
      arrow(120, 96, 136, 92, dashed=True) + arrow(284, 92, 300, 96, dashed=True) +
      arrow(300, 164, 284, 168, dashed=True) + arrow(136, 168, 120, 164, dashed=True) +
      txt(210, 202, "pen passes after every sentence", "la", "middle") +
      txt(210, 224, "each pupil signs their own sentences in their own colour", "lm", "middle") +
      txt(210, 244, "you read the colours, not the content", "lm", "middle"))

scene(S6, "numbered-heads", "Numbered heads", "Tables of four · prep 5 min · no extra time",
      "".join(table_of_four(114 + i * 180, 128, accent_pupils=(2,) if i == 1 else ()) for i in range(2)) +
      card(158, 194, 104, 26, "draw a number", True) +
      arrow(240, 192, 268, 154) +
      txt(210, 244, "any number can be called, so the group brings everyone up to speed", "lm", "middle") +
      txt(210, 74, "one pupil reports for the whole group", "la", "middle"))

scene(S6, "jigsaw-stations", "Jigsaw stations", "Four stations · prep 20 min · 20 min",
      "".join(desk(36 + (i % 2) * 100, 88 + (i // 2) * 66, 76, 44,
                   ["src 1", "src 2", "src 3", "src 4"][i]) for i in range(4)) +
      txt(112, 76, "round 1 · become the expert", "la", "middle") +
      arrow(224, 132, 262, 132, label=None) +
      table_of_four(330, 132, accent_pupils=(0, 1, 2, 3), labels=("1", "2", "3", "4")) +
      txt(330, 76, "round 2 · one expert each", "la", "middle") +
      txt(210, 226, "the task cannot be finished without all four pieces", "lm", "middle"))

scene(S6, "silent-build", "Silent build", "Floor or joined tables · prep 10 min · 8 min",
      rect(96, 84, 228, 104, 4, "stroke", "fillw") +
      "".join(card(112 + (i % 4) * 52, 100 + (i // 4) * 40, 44, 30, None, accent=(i in (2, 6)))
              for i in range(8)) +
      timer(360, 100, "4m") + txt(360, 126, "silent", "la", "middle") +
      "".join(pupil(64, 104 + i * 30, 8) for i in range(3)) +
      arrow(80, 134, 100, 134, dashed=True, label=None) +
      txt(210, 210, "move, place, reorder, gesture · no talking", "la", "middle") +
      txt(210, 234, "talk opens after, from a shared arrangement", "lm", "middle"))

scene(S6, "critique-swap", "Two group critique swap", "Work at pupil height · prep 0 · 8 min",
      panel(32, 84, 150, 92, "group A work") + panel(238, 84, 150, 92, "group B work") +
      note(60, 100, 20, True, "+") + note(120, 100, 20, True, "?") +
      note(266, 100, 20, True, "+") + note(326, 100, 20, True, "?") +
      arrow(186, 112, 234, 112, label=None) + arrow(234, 148, 186, 148, dashed=True) +
      txt(210, 200, "exactly two notes: one specific strength, one specific question", "lm", "middle") +
      txt(210, 224, "five minutes to act on them before the work counts as finished", "la", "middle"))


# ---------- write ------------------------------------------------------------

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    strands = {}
    for strand, slug, title, sub, body in SCENES:
        d = os.path.join(here, strand)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, slug + ".svg"), "w") as f:
            f.write(svg(title, sub, body))
        strands.setdefault(strand, []).append((slug, title, sub))

    names = {
        "01-metacognition-self-regulation": "Strand 1 · Metacognition and self-regulated learning",
        "02-emotional-engagement": "Strand 2 · Emotional engagement",
        "03-retrieval-and-revision": "Strand 3 · Retrieval and revision",
        "04-responsive-teaching": "Strand 4 · Responsive teaching",
        "05-oracy-and-word-wealth": "Strand 5 · Oracy and word wealth",
        "06-collaborative-learning": "Strand 6 · Collaborative learning",
    }

    cards = []
    for strand in sorted(strands):
        items = "".join(
            f'<figure><img src="{strand}/{slug}.svg" alt="{title}" loading="lazy">'
            f'<figcaption><b>{title}</b><span>{sub}</span>'
            f'<code>{strand}/{slug}.svg</code></figcaption></figure>'
            for slug, title, sub in strands[strand])
        cards.append(f'<section><h2>{names.get(strand, strand)}</h2><div class="grid">{items}</div></section>')

    html = f"""<!doctype html><meta charset="utf-8"><title>AIS setup schematics</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 :root{{color-scheme:light dark;--bg:#fbfbfd;--fg:#1f2430;--mut:#79808f;--line:#e3e6ef;--card:#fff}}
 @media (prefers-color-scheme:dark){{:root{{--bg:#0e1118;--fg:#e8eaf2;--mut:#8d95a8;--line:#262c3c;--card:#151a26}}}}
 *{{box-sizing:border-box}}
 body{{margin:0;padding:40px 28px 72px;background:var(--bg);color:var(--fg);
   font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
 header{{max-width:1180px;margin:0 auto 36px}}
 h1{{font-size:24px;margin:0 0 6px}} header p{{margin:0;color:var(--mut);max-width:70ch}}
 section{{max-width:1180px;margin:0 auto 44px}}
 h2{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);
   margin:0 0 16px;padding-bottom:8px;border-bottom:1px solid var(--line)}}
 .grid{{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}}
 figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
 figure img{{display:block;width:100%;height:auto;background:transparent}}
 figcaption{{padding:12px 14px 14px;border-top:1px solid var(--line);display:grid;gap:3px}}
 figcaption span{{color:var(--mut);font-size:12px}}
 figcaption code{{color:var(--mut);font-size:11px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
</style>
<header><h1>AIS setup schematics</h1>
<p>Thirty AIS-original diagrams, one per setup in the <code>ais-learning-environment</code> skill.
Regenerate with <code>python3 build-diagrams.py</code>. Light and dark aware. Teacher photos of the
same setups drop into <code>photos/&lt;strand&gt;/&lt;setup&gt;.jpg</code> alongside these.</p></header>
{''.join(cards)}
"""
    with open(os.path.join(here, "index.html"), "w") as f:
        f.write(html)

    # manifest: what the one-pagers and the dashboard panel read.
    # photo wins over diagram when the file exists, so teacher photos need no code change.
    import json
    entries = []
    for strand in sorted(strands):
        for slug, title, sub in strands[strand]:
            photo = f"photos/{strand}/{slug}.jpg"
            entries.append({
                "strand": strand,
                "strand_title": names.get(strand, strand),
                "setup": slug,
                "title": title,
                "context": sub,
                "diagram": f"diagrams/{strand}/{slug}.svg",
                "photo": photo,
                "photo_present": os.path.exists(os.path.join(here, "..", photo)),
            })
    with open(os.path.join(here, "manifest.json"), "w") as f:
        json.dump({"count": len(entries), "setups": entries}, f, indent=2)

    have = sum(1 for e in entries if e["photo_present"])
    print(f"wrote {len(SCENES)} svgs across {len(strands)} strands + index.html + manifest.json")
    print(f"photos present: {have}/{len(entries)}")


if __name__ == "__main__":
    main()
