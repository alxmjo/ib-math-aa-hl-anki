#!/usr/bin/env python3
"""Generates the SVG figures in this folder. Run: python3 figures/make_figures.py
Lines and text use currentColor so figures follow Anki's day/night text colour.
Accent elements carry class "acc" (stroke) or "acct" (text); the card CSS lightens them in night mode."""
import math, os

ACC = "#1a5fb4"
HERE = os.path.dirname(os.path.abspath(__file__))


def P(x, y): return (float(x), float(y))
def add(p, q, k=1): return (p[0] + k * q[0], p[1] + k * q[1])
def unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); return (dx / L, dy / L)
def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")


def line(p, q, acc=False, dash=False, w=1.6):
    s = f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" stroke="{ACC if acc else "currentColor"}" stroke-width="{w}"'
    if dash: s += ' stroke-dasharray="5 4"'
    if acc: s += ' class="acc"'
    return s + "/>"


def poly(pts, acc=False, closed=True, dash=False):
    d = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    tag = "polygon" if closed else "polyline"
    s = f'<{tag} points="{d}" fill="none" stroke="{ACC if acc else "currentColor"}" stroke-width="1.6" stroke-linejoin="round"'
    if dash: s += ' stroke-dasharray="5 4"'
    if acc: s += ' class="acc"'
    return s + "/>"


def text(x, y, s, anchor="middle", italic=False, acc=False, size=14):
    st = ' font-style="italic"' if italic else ""
    cl = ' class="acct"' if acc else ""
    return f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-size="{size}"{st} fill="{ACC if acc else "currentColor"}"{cl}>{s}</text>'


def right_angle(v, a, b, s=9):
    u1, u2 = unit(v, a), unit(v, b)
    p1 = add(v, u1, s); p2 = add(p1, u2, s); p3 = add(v, u2, s)
    return poly([p1, p2, p3], closed=False)


def arc(c, r, a1, a2, acc=False):
    """Arc counterclockwise (maths convention, y up) from angle a1 to a2 in degrees."""
    span = (a2 - a1) % 360
    x1, y1 = c[0] + r * math.cos(math.radians(a1)), c[1] - r * math.sin(math.radians(a1))
    x2, y2 = c[0] + r * math.cos(math.radians(a2)), c[1] - r * math.sin(math.radians(a2))
    large = 1 if span > 180 else 0
    s = f'<path d="M {f(x1)} {f(y1)} A {r} {r} 0 {large} 0 {f(x2)} {f(y2)}" fill="none" stroke="{ACC if acc else "currentColor"}" stroke-width="1.4"'
    if acc: s += ' class="acc"'
    return s + "/>"


def arc_tick(c, r, a, L=9):
    """A short radial tick crossing an angle arc at angle a, to mark equal angles."""
    u = (math.cos(math.radians(a)), -math.sin(math.radians(a)))
    return line(add(c, u, r - L / 2), add(c, u, r + L / 2), w=1.4)


def angle_label(c, r, a1, a2, s, **kw):
    """Label placed on the bisector of the angle from a1 to a2 (counterclockwise), at distance r from c."""
    m = math.radians(a1 + ((a2 - a1) % 360) / 2)
    return text(c[0] + r * math.cos(m), c[1] - r * math.sin(m) + 5, s, **kw)


def ang(p, q):
    """Direction of p->q in degrees, maths convention (y up)."""
    return math.degrees(math.atan2(-(q[1] - p[1]), q[0] - p[0]))


def ticks(p, q, n=1, L=7, gap=4):
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2); u = unit(p, q); nrm = (-u[1], u[0]); out = []
    for i in range(n):
        c = add(m, u, (i - (n - 1) / 2) * gap)
        out.append(line(add(c, nrm, -L / 2), add(c, nrm, L / 2), w=1.4))
    return "".join(out)


def dot(p, r=2.5): return f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{r}" fill="currentColor"/>'


def north(p, length=60):
    top = (p[0], p[1] - length)
    return (line(p, top, dash=True) + poly([(top[0], top[1] - 7), (top[0] - 4, top[1] + 1), (top[0] + 4, top[1] + 1)])
            + text(top[0], top[1] - 11, "N"))


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="sans-serif">{body}</svg>')


FIGS = {}

# 1.7-A01: labelled right-angled triangle
A, B, C = P(30, 130), P(210, 130), P(210, 35)
FIGS["1.7-A01"] = svg(250, 155, poly([A, B, C]) + right_angle(B, A, C) + arc(A, 30, 0, ang(A, C), acc=True)
    + angle_label(A, 43, 0, ang(A, C), "θ", italic=True, acc=True) + text(105, 72, "HYP") + text(216, 88, "OPP", anchor="start")
    + text(120, 148, "ADJ"))

# 1.7-C01: isosceles triangle, altitude bisects base and apex angle
T, L, R = P(120, 20), P(40, 140), P(200, 140); M = P(120, 140)
FIGS["1.7-C01"] = svg(240, 155, poly([T, L, R]) + line(T, M, acc=True, dash=True) + right_angle(M, R, T)
    + ticks(T, L) + ticks(T, R) + ticks(L, M, 2) + ticks(M, R, 2)
    + arc(T, 36, ang(T, L), -90) + arc(T, 36, -90, ang(T, R))
    + arc_tick(T, 36, (ang(T, L) - 90) / 2) + arc_tick(T, 36, (-90 + ang(T, R)) / 2))

# 1.7-C02: perpendicular from the centre bisects a chord
O, r = P(120, 82), 66
ca = (O[0] + r * math.cos(math.radians(210)), O[1] + r * 0.5); cb = (O[0] + r * math.cos(math.radians(330)), O[1] + r * 0.5)
M = ((ca[0] + cb[0]) / 2, ca[1])
FIGS["1.7-C02"] = svg(240, 160, f'<circle cx="{f(O[0])}" cy="{f(O[1])}" r="{r}" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    + line(ca, cb) + line(O, ca) + line(O, cb) + line(O, M, acc=True, dash=True) + right_angle(M, cb, O)
    + ticks(ca, M, 2) + ticks(M, cb, 2) + dot(O) + text(O[0], O[1] - 8, "O"))

# 1.7-C03: tangent perpendicular to radius
O, r = P(95, 68), 50; T = P(95, 118); Q = P(215, 118)
FIGS["1.7-C03"] = svg(240, 140, f'<circle cx="{f(O[0])}" cy="{f(O[1])}" r="{r}" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    + line(P(15, 118), P(225, 118)) + line(O, T, acc=True) + line(O, Q, dash=True) + right_angle(T, Q, O)
    + dot(O) + text(O[0] - 10, O[1] - 2, "O") + text(T[0], T[1] + 16, "T") + text(Q[0], Q[1] + 16, "P")
    + text(18, 135, "tangent", anchor="start", size=12))

# 1.7-C04: angle in a semicircle
O, r = P(120, 120), 90; A, B = P(30, 120), P(210, 120)
Pt = (O[0] + r * math.cos(math.radians(60)), O[1] - r * math.sin(math.radians(60)))
FIGS["1.7-C04"] = svg(240, 140, f'<path d="M 30 120 A 90 90 0 0 1 210 120" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    + line(A, B) + poly([A, Pt, B], acc=True, closed=False) + right_angle(Pt, A, B) + dot(O)
    + text(O[0], O[1] + 16, "O") + text(A[0] - 2, A[1] + 16, "A") + text(B[0] + 2, B[1] + 16, "B")
    + text(Pt[0] + 6, Pt[1] - 6, "P", anchor="start"))

# 1.7-C05: rhombus diagonals
L, T, R, B = P(30, 80), P(120, 30), P(210, 80), P(120, 130); M = P(120, 80)
FIGS["1.7-C05"] = svg(240, 150, poly([L, T, R, B]) + line(L, R, acc=True, dash=True) + line(T, B, acc=True, dash=True)
    + right_angle(M, R, T) + ticks(L, M) + ticks(M, R) + ticks(T, M, 2) + ticks(M, B, 2)
    + arc(L, 30, 0, ang(L, T)) + arc(L, 30, ang(L, B), 0) + arc(R, 30, ang(R, T), 180) + arc(R, 30, 180, ang(R, B) + 360)
    + arc_tick(L, 30, ang(L, T) / 2) + arc_tick(L, 30, ang(L, B) / 2)
    + arc_tick(R, 30, (ang(R, T) + 180) / 2) + arc_tick(R, 30, (180 + ang(R, B) + 360) / 2))

# 1.7-D01: angle of depression equals angle of elevation
A, B = P(45, 40), P(205, 128)
FIGS["1.7-D01"] = svg(250, 150, line(P(45, 40), P(45, 128)) + line(P(20, 128), P(235, 128))
    + line(A, P(215, 40), dash=True) + line(A, B, acc=True)
    + arc(A, 40, ang(A, B), 0) + text(100, 36, "depression", anchor="start", size=12)
    + arc(B, 40, ang(B, A), 180) + text(150, 142, "elevation", anchor="middle", size=12)
    + text(A[0] - 8, A[1] + 4, "A", anchor="end") + text(B[0] + 8, B[1] + 4, "B", anchor="start"))

# 1.7-D02: space diagonal of a cuboid
off = (50, -35)
F0, F1, F2, F3 = P(30, 140), P(170, 140), P(170, 60), P(30, 60)
B0, B1, B2, B3 = add(F0, off), add(F1, off), add(F2, off), add(F3, off)
FIGS["1.7-D02"] = svg(250, 160, poly([F0, F1, F2, F3]) + line(F1, B1) + line(F2, B2) + line(F3, B3) + line(B3, B2) + line(B1, B2)
    + line(B0, F0, dash=True) + line(B0, B1, dash=True) + line(B0, B3, dash=True)
    + line(F0, B1, acc=True, dash=True) + line(F0, B2, acc=True) + right_angle(B1, F0, B2, 8)
    + text(100, 155, "a", italic=True) + text(203, 130, "b", italic=True) + text(228, 70, "c", italic=True, anchor="start")
    + text(118, 82, "d", italic=True, acc=True))

# 1.7-E01: a true bearing, clockwise from north
A = P(100, 105); Bd = 120; r = 85
B = (A[0] + r * math.sin(math.radians(Bd)), A[1] - r * math.cos(math.radians(Bd)))
FIGS["1.7-E01"] = svg(240, 160, north(A, 70) + line(A, B, acc=True) + arc(A, 26, 90 - Bd, 90, acc=True)
    + text(140, 95, "120°", anchor="start", acc=True, size=13) + dot(A) + text(A[0] - 8, A[1] + 4, "A", anchor="end")
    + text(B[0] + 6, B[1] + 4, "B", anchor="start"))

# 1.7-E02: back bearing differs by 180 degrees
A, B = P(55, 145), P(175, 80)
FIGS["1.7-E02"] = svg(280, 170, north(A, 62) + north(B, 45) + line(A, B, acc=True)
    + arc(A, 24, ang(A, B), 90) + angle_label(A, 36, ang(A, B), 90, "θ", italic=True)
    + arc(B, 16, ang(B, A), 90) + text(198, 104, "θ + 180°", anchor="start", size=12)
    + dot(A) + dot(B) + text(A[0] - 8, A[1] + 12, "A", anchor="end") + text(B[0] - 10, B[1] - 8, "B", anchor="end"))

# 1.7-F01: angle between a line and a plane
A, Pp, N = P(70, 118), P(170, 28), P(170, 106)
FIGS["1.7-F01"] = svg(240, 145, poly([P(15, 132), P(170, 132), P(225, 82), P(70, 82)])
    + line(Pp, N, dash=True) + right_angle(N, A, Pp, 8) + line(A, N, acc=True, dash=True) + line(A, Pp, acc=True)
    + arc(A, 34, ang(A, N), ang(A, Pp), acc=True) + angle_label(A, 47, ang(A, N), ang(A, Pp), "θ", italic=True, acc=True)
    + dot(A) + dot(N) + text(A[0] - 8, A[1] + 4, "A", anchor="end") + text(Pp[0] + 6, Pp[1] + 4, "P", anchor="start")
    + text(N[0] + 7, N[1] + 12, "N", anchor="start"))

if __name__ == "__main__":
    for name, s in FIGS.items():
        open(os.path.join(HERE, f"{name}.svg"), "w").write(s + "\n")
    print(len(FIGS), "figures written")
