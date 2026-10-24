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

if __name__ == "__main__":
    for name, s in FIGS.items():
        open(os.path.join(HERE, f"{name}.svg"), "w").write(s + "\n")
    print(len(FIGS), "figures written")
