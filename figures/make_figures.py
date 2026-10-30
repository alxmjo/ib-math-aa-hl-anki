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


def arc(c, r, a1, a2, acc=False, w=1.4):
    """Arc counterclockwise (maths convention, y up) from angle a1 to a2 in degrees."""
    span = (a2 - a1) % 360
    x1, y1 = c[0] + r * math.cos(math.radians(a1)), c[1] - r * math.sin(math.radians(a1))
    x2, y2 = c[0] + r * math.cos(math.radians(a2)), c[1] - r * math.sin(math.radians(a2))
    large = 1 if span > 180 else 0
    s = f'<path d="M {f(x1)} {f(y1)} A {r} {r} 0 {large} 0 {f(x2)} {f(y2)}" fill="none" stroke="{ACC if acc else "currentColor"}" stroke-width="{w}"'
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


def circle(c, r):
    return f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{r}" fill="none" stroke="currentColor" stroke-width="1.6"/>'


def pt(c, r, a):
    """Point at angle a (degrees, anticlockwise from the positive x-axis) on the circle centre c, radius r."""
    return (c[0] + r * math.cos(math.radians(a)), c[1] - r * math.sin(math.radians(a)))


def axes(c, r, extra=22):
    return (line((c[0] - r - extra, c[1]), (c[0] + r + extra, c[1]), w=1.2) + line((c[0], c[1] + r + extra), (c[0], c[1] - r - extra), w=1.2)
            + text(c[0] + r + extra + 4, c[1] + 5, "x", anchor="start", italic=True, size=13)
            + text(c[0] + 6, c[1] - r - extra + 4, "y", anchor="start", italic=True, size=13))


def unit_circle(c, r):
    return axes(c, r) + circle(c, r)


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


# ---------- Chapter 1.8 ----------
# 1.8-A01: one radian
O, r = P(110, 85), 60
A, B = pt(O, r, -28.65), pt(O, r, 28.65)
FIGS["1.8-A01"] = svg(220, 170, circle(O, r) + line(O, A) + line(O, B) + arc(O, r, -28.65, 28.65, acc=True, w=3)
    + arc(O, 16, -28.65, 28.65) + text(O[0] + 21, O[1] + 4, "1 rad", anchor="start", size=12) + dot(O)
    + text(O[0] + 24, O[1] - 26, "r", italic=True) + text(O[0] + 24, O[1] + 35, "r", italic=True)
    + text(O[0] + r + 8, O[1] + 5, "r", italic=True, acc=True, anchor="start") + text(O[0] - 8, O[1] + 5, "O", anchor="end"))

# 1.8-C01: cos and sin as coordinates
O, r = P(155, 95), 65; Pp = pt(O, r, 140)
FIGS["1.8-C01"] = svg(280, 185, unit_circle(O, r) + line(O, Pp, acc=True) + line(Pp, (Pp[0], O[1]), dash=True) + line(Pp, (O[0], Pp[1]), dash=True)
    + arc(O, 16, 0, 140, acc=True) + angle_label(O, 28, 0, 140, "θ", italic=True, acc=True) + dot(Pp)
    + text(Pp[0] - 6, Pp[1] - 8, "P(cos θ, sin θ)", anchor="end", size=12)
    + text(Pp[0], O[1] + 16, "cos θ", size=12) + text(O[0] + 6, Pp[1] + 4, "sin θ", anchor="start", size=12)
    + text(O[0] + r + 3, O[1] + 16, "1", anchor="start", size=12))

# 1.8-C02: which ratios are positive in each quadrant
O, r = P(130, 85), 60
FIGS["1.8-C02"] = svg(260, 175, axes(O, r)
    + text(O[0] + 40, O[1] - 30, "All", acc=True) + text(O[0] - 40, O[1] - 30, "sin", acc=True)
    + text(O[0] - 40, O[1] + 40, "tan", acc=True) + text(O[0] + 40, O[1] + 40, "cos", acc=True)
    + text(O[0] + 40, O[1] - 48, "1st", size=11) + text(O[0] - 40, O[1] - 48, "2nd", size=11)
    + text(O[0] - 40, O[1] + 22, "3rd", size=11) + text(O[0] + 40, O[1] + 22, "4th", size=11))

# 1.8-C04: supplementary angles (reflection in the y-axis)
O, r, t = P(150, 100), 62, 40; Pp, Q = pt(O, r, t), pt(O, r, 180 - t)
FIGS["1.8-C04"] = svg(300, 180, unit_circle(O, r) + line(O, Pp, acc=True) + line(O, Q, acc=True) + line(Q, Pp, dash=True)
    + arc(O, 14, 0, t) + angle_label(O, 26, 0, t, "θ", italic=True, size=12)
    + arc(O, 22, 0, 180 - t) + angle_label(O, 40, 110, 140, "π − θ", size=12)
    + dot(Pp) + dot(Q) + text(Pp[0] + 6, Pp[1] - 6, "(cos θ, sin θ)", anchor="start", size=11)
    + text(Q[0] - 6, Q[1] - 6, "(−cos θ, sin θ)", anchor="end", size=11))

# 1.8-C05: negative angles (reflection in the x-axis)
O, r, t = P(130, 92), 60, 35; Pp, Q = pt(O, r, t), pt(O, r, -t)
FIGS["1.8-C05"] = svg(300, 185, unit_circle(O, r) + line(O, Pp, acc=True) + line(O, Q, acc=True) + line(Pp, Q, dash=True)
    + arc(O, 16, 0, t) + angle_label(O, 29, 0, t, "θ", italic=True, size=12)
    + arc(O, 16, -t, 0) + angle_label(O, 31, -t, 0, "−θ", size=12)
    + dot(Pp) + dot(Q) + text(Pp[0] + 6, Pp[1] - 6, "(cos θ, sin θ)", anchor="start", size=11)
    + text(Q[0] + 6, Q[1] + 14, "(cos θ, −sin θ)", anchor="start", size=11))

# 1.8-D16: the two special triangles
A, B, C = P(20, 125), P(110, 125), P(110, 35)
D, E, F = P(165, 125), P(217, 125), P(217, 35)
FIGS["1.8-D16"] = svg(260, 150, poly([A, B, C]) + right_angle(B, A, C) + arc(A, 26, 0, 45) + angle_label(A, 42, 0, 45, "π/4", size=11)
    + arc(C, 22, 225, 270) + angle_label(C, 38, 225, 270, "π/4", size=11)
    + text(65, 142, "1") + text(118, 85, "1", anchor="start") + text(56, 72, "√2", anchor="end")
    + poly([D, E, F]) + right_angle(E, D, F) + arc(D, 20, 0, ang(D, F)) + angle_label(D, 36, 0, ang(D, F), "π/3", size=11)
    + arc(F, 24, ang(F, D), 270) + angle_label(F, 42, ang(F, D), 270, "π/6", size=11)
    + text(191, 142, "1") + text(225, 85, "√3", anchor="start") + text(183, 75, "2", anchor="end"))

# 1.8-D17: reference angle for 4π/3
O, r = P(140, 92), 62; Pp = pt(O, r, 240)
FIGS["1.8-D17"] = svg(260, 180, unit_circle(O, r) + line(O, Pp, acc=True) + line(Pp, (Pp[0], O[1]), dash=True)
    + arc(O, 14, 0, 240) + angle_label(O, 28, 0, 240, "4π/3", size=11)
    + arc(O, 30, 180, 240, acc=True) + angle_label(O, 50, 180, 220, "π/3", acc=True, size=11)
    + dot(Pp) + text(Pp[0] - 6, Pp[1] + 12, "P", anchor="end"))

# 1.8-D18: points at the quadrantal angles
O, r = P(140, 95), 60
FIGS["1.8-D18"] = svg(280, 185, unit_circle(O, r) + "".join(dot(pt(O, r, a)) for a in (0, 90, 180, 270))
    + text(O[0] + r + 4, O[1] + 16, "(1, 0)", anchor="start", size=12) + text(O[0] - 6, O[1] - r - 6, "(0, 1)", anchor="end", size=12)
    + text(O[0] - r - 4, O[1] + 16, "(−1, 0)", anchor="end", size=12) + text(O[0] + 6, O[1] + r + 15, "(0, −1)", anchor="start", size=12))

# 1.8-F01: sin θ = k, solutions α and π − α
O, r, a = P(140, 95), 60, 30; P1, P2 = pt(O, r, a), pt(O, r, 180 - a)
FIGS["1.8-F01"] = svg(280, 180, unit_circle(O, r) + line((O[0] - r - 18, P1[1]), (O[0] + r + 18, P1[1]), acc=True, dash=True)
    + text(O[0] + r + 20, P1[1] - 4, "y = k", anchor="start", italic=True, acc=True, size=12)
    + line(O, P1) + line(O, P2) + dot(P1) + dot(P2)
    + arc(O, 14, 0, a) + angle_label(O, 26, 0, a, "α", italic=True, size=12)
    + arc(O, 20, 0, 180 - a) + angle_label(O, 50, 0, 180 - a, "π − α", size=12))

# 1.8-F02: cos θ = k, solutions α and 2π − α
O, r, a = P(130, 95), 60, 50; P1, P2 = pt(O, r, a), pt(O, r, -a)
FIGS["1.8-F02"] = svg(270, 185, unit_circle(O, r) + line((P1[0], O[1] - r - 18), (P1[0], O[1] + r + 18), acc=True, dash=True)
    + text(P1[0] + 6, O[1] - r - 8, "x = k", anchor="start", italic=True, acc=True, size=12)
    + line(O, P1) + line(O, P2) + dot(P1) + dot(P2)
    + arc(O, 14, 0, a) + angle_label(O, 27, 0, a, "α", italic=True, size=12)
    + arc(O, 20, 0, 360 - a) + angle_label(O, 40, 0, 360 - a, "2π − α", size=12))

# 1.8-F03: tan θ = k, solutions α and π + α
O, r, a = P(130, 95), 60, 40; P1, P2 = pt(O, r, a), pt(O, r, 180 + a)
FIGS["1.8-F03"] = svg(260, 185, unit_circle(O, r) + line(P2, P1, acc=True) + dot(P1) + dot(P2)
    + arc(O, 14, 0, a) + angle_label(O, 27, 0, a, "α", italic=True, size=12)
    + arc(O, 22, 0, 180 + a) + angle_label(O, 40, 0, 180 + a, "π + α", size=12))

# 1.8-G01: gradient of a line is tan θ
X = P(95, 125); t = 35; m = math.tan(math.radians(t))
FIGS["1.8-G01"] = svg(260, 170, line(P(15, 125), P(245, 125), w=1.2) + line(P(55, 160), P(55, 15), w=1.2)
    + text(248, 130, "x", anchor="start", italic=True, size=13) + text(61, 19, "y", anchor="start", italic=True, size=13)
    + line(P(40, 125 + 55 * m), P(235, 125 - 140 * m), acc=True)
    + line(X, P(185, 125), dash=True) + line(P(185, 125), P(185, 125 - 90 * m), dash=True) + right_angle(P(185, 125), X, P(185, 50), 7)
    + arc(X, 24, 0, t, acc=True) + angle_label(X, 38, 0, t, "θ", italic=True, acc=True)
    + text(140, 142, "run", size=12) + text(191, 125 - 45 * m + 4, "rise", anchor="start", size=12))


# ---------- Chapter 1.9 ----------
# 1.9-A01: labelling convention, side a opposite angle A
A, B, C = P(30, 135), P(215, 135), P(150, 30)
def side_label(p, q, s, out=12):
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2); u = unit(p, q); n = (u[1], -u[0])
    return text(m[0] + n[0] * out, m[1] + n[1] * out + 5, s, italic=True, acc=True)
FIGS["1.9-A01"] = svg(245, 160, poly([A, B, C]) + text(A[0] - 8, A[1] + 5, "A", anchor="end") + text(B[0] + 8, B[1] + 5, "B", anchor="start")
    + text(C[0], C[1] - 8, "C") + side_label(B, C, "a", -12) + side_label(C, A, "b", -12) + side_label(A, B, "c", -12))

# 1.9-A02: area, two sides and the included angle C
C, A, B = P(40, 130), P(150, 35), P(215, 130)
FIGS["1.9-A02"] = svg(245, 155, poly([A, B, C]) + arc(C, 28, 0, ang(C, A), acc=True) + angle_label(C, 42, 0, ang(C, A), "C", italic=True, acc=True)
    + text(C[0] - 8, C[1] + 5, "C", anchor="end") + text(A[0], A[1] - 8, "A") + text(B[0] + 8, B[1] + 5, "B", anchor="start")
    + side_label(C, B, "a", -14) + side_label(A, C, "b", -14))

# 1.9-C03: ambiguous case, two triangles from the same two sides and non-included angle
A, B = P(25, 150), P(217, 150); t = 30; u = (math.cos(math.radians(t)), -math.sin(math.radians(t)))
C1, C2 = add(A, u, 94.25), add(A, u, 238.35); R = 120
a1, a2 = ang(B, C2) - 13, ang(B, C1) + 13
x1, y1 = pt(B, R, a1); x2, y2 = pt(B, R, a2)
FIGS["1.9-C03"] = svg(285, 175, line(A, B) + line(A, add(A, u, 268))
    + f'<path d="M {f(x1)} {f(y1)} A {R} {R} 0 0 0 {f(x2)} {f(y2)}" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 4"/>'
    + line(B, C1, acc=True) + line(B, C2, acc=True) + dot(C1) + dot(C2)
    + arc(A, 30, 0, t) + text(A[0] - 8, A[1] + 5, "A", anchor="end") + text(B[0] + 8, B[1] + 5, "B", anchor="start")
    + text(C1[0] - 6, C1[1] - 8, "C₁", anchor="end") + text(C2[0] - 8, C2[1] - 4, "C₂", anchor="end")
    + text(121, 168, "c", italic=True) + side_label(C1, B, "a", 12) + side_label(B, C2, "a", 12))


# 1.9-D01 / D02: which information calls for which rule (known parts in accent, "?" marks what is found)
def given_triangle(dx, sides, angles, q_side=None, q_angle=None, caption=""):
    V = [P(15 + dx, 108), P(135 + dx, 108), P(92 + dx, 22)]
    out = ""
    for i in range(3):
        a, b = V[i], V[(i + 1) % 3]
        out += line(a, b, acc=i in sides, w=3.2 if i in sides else 1.6)
    for i in angles + ([q_angle] if q_angle is not None else []):
        v, p1, p2 = V[i], V[(i + 1) % 3], V[(i + 2) % 3]
        a1, a2 = ang(v, p1), ang(v, p2)
        if (a2 - a1) % 360 > 180: a1, a2 = a2, a1
        out += arc(v, 20, a1, a2, acc=i in angles, w=2.2 if i in angles else 1.4)
        if i == q_angle: out += angle_label(v, 34, a1, a2, "?", size=13)
    if q_side is not None:
        a, b = V[q_side], V[(q_side + 1) % 3]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); u = unit(a, b); n = (u[1], -u[0])
        out += text(m[0] - n[0] * 13, m[1] - n[1] * 13 + 5, "?", size=13)
    return out + text(75 + dx, 132, caption, size=11)
FIGS["1.9-D01"] = svg(340, 142, given_triangle(0, [0, 1, 2], [], q_angle=2, caption="three sides")
    + given_triangle(185, [0, 2], [0], q_side=1, caption="two sides, included angle"))
FIGS["1.9-D02"] = svg(340, 142, given_triangle(0, [0], [0, 1], q_side=1, caption="two angles, one side")
    + given_triangle(185, [0, 1], [0], q_angle=2, caption="two sides, non-included angle"))


# ---------- Chapter 1.14 ----------
def mk(ox, oy, s):
    """Maths coordinates -> SVG coordinates, origin (ox, oy), s pixels per unit."""
    return lambda x, y: (ox + s * x, oy - s * y)


def curve(M, fn, x0, x1, n=60, acc=True, w=2.0):
    pts = [M(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]
    return poly(pts, acc=acc, closed=False).replace('stroke-width="1.6"', f'stroke-width="{w}"')


def xaxis(M, x0, x1, label=True):
    a, b = M(x0, 0), M(x1, 0)
    return line(a, b, w=1.2) + (text(b[0] + 4, b[1] + 5, "x", anchor="start", italic=True, size=13) if label else "")


def tick_label(M, x, s, below=True, acc=False, size=13):
    q = M(x, 0)
    return line((q[0], q[1] - 4), (q[0], q[1] + 4), w=1.2) + text(q[0], q[1] + (18 if below else -9), s, italic=True, acc=acc, size=size)


# 1.14-B01: sign of a, concave up (minimum) and concave down (maximum)
M1, M2 = mk(65, 70, 22), mk(205, 70, 22)
FIGS["1.14-B01"] = svg(280, 140, curve(M1, lambda x: x * x - 1.6, -1.95, 1.95) + dot(M1(0, -1.6), 3.2)
    + text(M1(0, -1.6)[0], M1(0, -1.6)[1] + 17, "minimum", size=12)
    + text(M1(0, 0)[0], 18, "a &gt; 0", italic=True, size=14, acc=True)
    + curve(M2, lambda x: 1.6 - x * x, -1.95, 1.95) + dot(M2(0, 1.6), 3.2)
    + text(M2(0, 1.6)[0], M2(0, 1.6)[1] - 9, "maximum", size=12)
    + text(M2(0, 0)[0], 132, "a &lt; 0", italic=True, size=14, acc=True))

# 1.14-B02: axis of symmetry midway between the x-intercepts p and q (tick marks: equal distances)
M = mk(20, 62, 26)
FIGS["1.14-B02"] = svg(250, 150, xaxis(M, 0, 8.3) + curve(M, lambda x: 0.35 * (x - 2) * (x - 6.5), 1.05, 7.45)
    + ticks(M(2, 0), M(4.25, 0)) + ticks(M(4.25, 0), M(6.5, 0))
    + line(M(4.25, 1.8), M(4.25, -2.6), acc=True, dash=True) + dot(M(2, 0)) + dot(M(6.5, 0))
    + text(M(2, 0)[0] - 6, M(2, 0)[1] + 17, "p", italic=True, anchor="end", size=14)
    + text(M(6.5, 0)[0] + 6, M(6.5, 0)[1] + 17, "q", italic=True, anchor="start", size=14)
    + text(M(4.25, 0)[0], 143, "x = (p + q)/2", italic=True, acc=True, size=13))

# 1.14-B03: vertex (h, k) of y = a(x - h)^2 + k
M = mk(25, 125, 26)
FIGS["1.14-B03"] = svg(250, 150, xaxis(M, 0, 8.1) + line(M(0, -0.6), M(0, 4.4), w=1.2)
    + text(M(0, 4.4)[0] + 6, M(0, 4.4)[1] + 4, "y", italic=True, anchor="start", size=13)
    + curve(M, lambda x: 0.75 * (x - 4.6) ** 2 + 1.5, 2.5, 6.7)
    + line(M(4.6, 0), M(4.6, 4.6), acc=True, dash=True) + dot(M(4.6, 1.5), 3.2)
    + text(M(4.6, 1.5)[0] + 10, M(4.6, 1.5)[1] + 16, "(h, k)", italic=True, anchor="start", acc=True, size=13)
    + text(M(4.6, 4.6)[0] + 6, M(4.6, 4.6)[1] + 8, "x = h", italic=True, anchor="start", size=13))


def three_panels(draw, captions, w=330, h=135):
    out = ""
    for i, (fn, cap) in enumerate(zip(draw, captions)):
        cx = 55 + 110 * i
        out += fn(mk(cx, 72, 18)) + text(cx, h - 4, cap, acc=True, size=19)
    return svg(w, h, out)


# 1.14-C01: discriminant and the x-axis, cuts / touches / misses
FIGS["1.14-C01"] = three_panels([
    lambda M: xaxis(M, -2.6, 2.6, False) + curve(M, lambda x: x * x - 1.8, -2.0, 2.0) + dot(M(-1.342, 0)) + dot(M(1.342, 0)),
    lambda M: xaxis(M, -2.6, 2.6, False) + curve(M, lambda x: x * x, -1.55, 1.55) + dot(M(0, 0)),
    lambda M: xaxis(M, -2.6, 2.6, False) + curve(M, lambda x: x * x + 0.9, -1.2, 1.2)],
    ["Δ &gt; 0", "Δ = 0", "Δ &lt; 0"])

# 1.14-C02 / C03: positive and negative definite
M = mk(110, 105, 22)
FIGS["1.14-C02"] = svg(240, 125, xaxis(M, -4.6, 4.6) + curve(M, lambda x: 0.6 * x * x + 0.8, -2.45, 2.45))
M = mk(110, 25, 22)
FIGS["1.14-C03"] = svg(240, 125, xaxis(M, -4.6, 4.6) + curve(M, lambda x: -0.6 * x * x - 0.8, -2.45, 2.45))

# 1.14-E01: a line and a parabola, two points / tangent / no points
def para_line(M, c):
    pa = curve(M, lambda x: x * x - 0.5, -1.9, 1.9, acc=False, w=1.8)
    ln = line(M(-2.4, 0.5 * -2.4 + c), M(2.4, 0.5 * 2.4 + c), acc=True, w=1.8)
    return pa + ln
def roots(c):  # x^2 - 0.5 = 0.5x + c
    import math as _m
    D = 0.25 + 4 * (0.5 + c)
    return [] if D < -1e-9 else sorted({(0.5 + s * _m.sqrt(max(D, 0))) / 2 for s in (-1, 1)})
FIGS["1.14-E01"] = three_panels([
    lambda M, c=0.4: para_line(M, c) + "".join(dot(M(x, x * x - 0.5)) for x in roots(c)),
    lambda M, c=-0.5625: para_line(M, c) + "".join(dot(M(x, x * x - 0.5)) for x in roots(c)),
    lambda M, c=-1.7: para_line(M, c)],
    ["Δ &gt; 0", "Δ = 0", "Δ &lt; 0"])

# 1.14-H03: sign diagram of a(x - p)(x - q), a > 0
M = mk(20, 62, 22)
N = 128
FIGS["1.14-H03"] = svg(250, 150, xaxis(M, 0, 9.6) + curve(M, lambda x: 0.42 * (x - 3) * (x - 6.8), 1.0, 8.8)
    + dot(M(3, 0)) + dot(M(6.8, 0))
    + line((M(0, 0)[0], N), (M(9.6, 0)[0], N), w=1.2) + text(M(9.6, 0)[0] + 4, N + 5, "x", anchor="start", italic=True, size=13)
    + line(M(3, 0), (M(3, 0)[0], N), dash=True, w=1.0) + line(M(6.8, 0), (M(6.8, 0)[0], N), dash=True, w=1.0)
    + text(M(1.4, 0)[0], N - 7, "+", acc=True, size=17) + text(M(4.9, 0)[0], N - 7, "−", acc=True, size=17)
    + text(M(8.3, 0)[0], N - 7, "+", acc=True, size=17)
    + text(M(3, 0)[0], N + 17, "p", italic=True, size=13) + text(M(6.8, 0)[0], N + 17, "q", italic=True, size=13))


# ---------- Chapter 1.15 ----------
def yaxis(M, y0, y1, label=True):
    a, b = M(0, y0), M(0, y1)
    return line(a, b, w=1.2) + (text(b[0] + 6, b[1] + 4, "y", anchor="start", italic=True, size=13) if label else "")


def dcurve(M, fn, x0, x1, n=60):
    """Dashed, plain-colour curve (the part of a graph that is left out)."""
    pts = [M(x0 + (x1 - x0) * i / n, fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]
    return poly(pts, closed=False, dash=True)


def pcurve(M, pts_fn, t0, t1, n=60, acc=True):
    """Parametric curve (x(t), y(t))."""
    pts = [M(*pts_fn(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]
    return poly(pts, acc=acc, closed=False).replace('stroke-width="1.6"', 'stroke-width="2"')


# 1.15-A01: vertical line test, a function (one meeting point) and a relation that is not (two)
M1, M2 = mk(75, 72, 20), mk(225, 72, 20)
FIGS["1.15-A01"] = svg(300, 150,
    xaxis(M1, -2.8, 2.8, False) + yaxis(M1, -2.6, 2.6, False) + curve(M1, lambda x: 0.3 * x ** 3 - 0.2 * x + 0.3, -2.0, 2.0)
    + line(M1(1.2, -2.7), M1(1.2, 2.7), dash=True, w=1.3) + dot(M1(1.2, 0.3 * 1.2 ** 3 - 0.24 + 0.3), 3.2)
    + text(M1(0, 0)[0], 143, "function", size=13)
    + xaxis(M2, -1.2, 3.6, False) + yaxis(M2, -2.6, 2.6, False) + pcurve(M2, lambda t: (0.55 * t * t, t), -2.3, 2.3)
    + line(M2(1.8, -2.7), M2(1.8, 2.7), dash=True, w=1.3) + dot(M2(1.8, 1.809), 3.2) + dot(M2(1.8, -1.809), 3.2)
    + text(M2(1.2, 0)[0], 143, "not a function", size=13))


# 1.15-D01 / D02: y = (ax + b)/(cx + d), one asymptote highlighted in each
def hyperbola(M):
    g = lambda x: 1 + 2 / (x - 2)
    return curve(M, g, 2.5, 8) + curve(M, g, -3, 1.6)
M = mk(61, 100, 17)
FIGS["1.15-D01"] = svg(250, 178, hyperbola(M)
    + line(M(2, -4), M(2, 5.2), acc=True, dash=True) + line(M(-3, 1), M(8, 1), dash=True, w=1.0)
    + text(M(2, 5.2)[0] - 7, M(2, 5.2)[1] + 12, "x = −d/c", anchor="end", italic=True, acc=True, size=13))
FIGS["1.15-D02"] = svg(250, 178, hyperbola(M)
    + line(M(-3, 1), M(8, 1), acc=True, dash=True) + line(M(2, -4), M(2, 5.2), dash=True, w=1.0)
    + text(M(-3, 1)[0], M(-3, 1)[1] - 8, "y = a/c", anchor="start", italic=True, acc=True, size=13))


# 1.15-F01: one-to-one, each vertical and each horizontal line meets the graph once
M = mk(120, 75, 24)
FIGS["1.15-F01"] = svg(240, 150, xaxis(M, -3.6, 3.6) + yaxis(M, -2.8, 2.8)
    + curve(M, lambda x: 0.35 * x ** 3, -1.95, 1.95)
    + line(M(-1.4, -2.9), M(-1.4, 2.9), dash=True, w=1.3) + dot(M(-1.4, 0.35 * -1.4 ** 3), 3.2)
    + line(M(-3.6, 1.5), M(3.6, 1.5), dash=True, w=1.3) + dot(M(1.5 ** (1 / 3) / 0.35 ** (1 / 3), 1.5), 3.2))


# 1.15-F03: horizontal line test, inverse exists (one meeting point) or not (two)
M1, M2 = mk(75, 68, 20), mk(225, 105, 20)
FIGS["1.15-F03"] = svg(300, 150,
    xaxis(M1, -2.8, 2.8, False) + yaxis(M1, -2.4, 2.6, False) + curve(M1, lambda x: 0.35 * x ** 3, -1.8, 1.95)
    + line(M1(-2.8, 1.2), M1(2.8, 1.2), dash=True, w=1.3) + dot(M1((1.2 / 0.35) ** (1 / 3), 1.2), 3.2)
    + text(M1(0, 0)[0], 143, "inverse exists", size=13)
    + xaxis(M2, -2.8, 2.8, False) + yaxis(M2, -0.6, 4.2, False) + curve(M2, lambda x: 0.8 * x * x, -2.2, 2.2)
    + line(M2(-2.8, 2.0), M2(2.8, 2.0), dash=True, w=1.3) + dot(M2(-1.581, 2.0), 3.2) + dot(M2(1.581, 2.0), 3.2)
    + text(M2(0, 0)[0], 143, "no inverse", size=13))


# 1.15-F05: y = f(x) and y = f^-1(x), reflections of each other in y = x
M = mk(66, 108, 20)
FIGS["1.15-F05"] = svg(250, 185, xaxis(M, -2.8, 5.8) + yaxis(M, -3.4, 4.8)
    + line(M(-2.8, -2.8), M(4.6, 4.6), dash=True, w=1.2)
    + text(M(4.6, 4.6)[0] + 4, M(4.6, 4.6)[1] + 4, "y = x", anchor="start", italic=True, size=12)
    + curve(M, lambda x: 2 ** x, -2.8, 2.0)
    + pcurve(M, lambda t: (2 ** t, t), -2.8, 2.0, acc=False)
    + text(M(-1.45, 1.35)[0], M(-1.45, 1.35)[1], "y = f(x)", italic=True, acc=True, size=12)
    + text(M(4, 2)[0] + 6, M(4, 2)[1] + 4, "y = f⁻¹(x)", anchor="start", italic=True, size=12))


# 1.15-F07: a quadratic restricted to x <= h passes the horizontal line test
M = mk(30, 128, 22)
q = lambda x: 0.6 * (x - 4) ** 2 + 0.8
FIGS["1.15-F07"] = svg(250, 150, xaxis(M, -0.6, 9.2) + yaxis(M, -0.4, 5.0)
    + curve(M, q, 1.3, 4) + dcurve(M, q, 4, 6.7) + dot(M(4, 0.8), 3.2)
    + line(M(4, 0), M(4, 5.0), dash=True, w=1.0)
    + text(M(4, 5.0)[0] + 6, M(4, 5.0)[1] + 8, "x = h", anchor="start", italic=True, size=13)
    + text(M(2.65, 0)[0], M(2.65, 0)[1] + 17, "x ≤ h", italic=True, acc=True, size=13))


if __name__ == "__main__":
    for name, s in FIGS.items():
        open(os.path.join(HERE, f"{name}.svg"), "w").write(s + "\n")
    print(len(FIGS), "figures written")
