import tkinter as tk
import math
import random

# ╔══════════════════════════════════════════════════════════════════╗
# ║                   TIMING CONTROLS  ⏱️                           ║
# ║  Change these values to sync with the song                      ║

LETTER_FLY_SPEED  = 40    # how fast letters fly (lower = faster, higher = slower)
LETTER_STAGGER    = 4     # delay between each letter (lower = faster stream)
LINE_STAY_TIME    = 2500  # how long lyrics stay on screen in ms (2500 = 2.5 sec)

# ╚══════════════════════════════════════════════════════════════════╝

# ── Lyrics ────────────────────────────────────────────────────────────────────
LYRICS_LINES = [
    [
        "Sambhaal ke rakha wo phool mera tu",
        "Meri shayari mein zaroor raha tu",
        "Jo aankhon mein pyaari si duniya basaayi",
    ],
    [
        "Wo duniya bhi tha tu, wo lamha bhi tha tu",
        "Haan, lagte hain mujhko ye kisse sataaane",
        "Deta na dil mera tujhko bhulaane",
    ],
    [
        "Adhoore se vaade, adhoori si raatein",
        "Ab hisse mein daakhil mere bas wo yaadein",
        "Rehna tha ban ke humdam tera",
    ],
    [
        "Aise jaana hi tha, phir tu kyun thehra?",
        "Ab na maane mera dil ke na tere qaabil",
        "Thi ik aarzu ki main kehta raha",
    ],
]

# ── Colors ────────────────────────────────────────────────────────────────────
PINK        = "#e63c6e"
PINK_LIGHT  = "#ff8fab"
PINK_DARK   = "#c0392b"
GOLD        = "#ffd700"
WHITE       = "#ffffff"
GRAD_COLORS = ["#0d0020","#150030","#1a0040","#220050","#1a0035","#100025","#0d0020"]
LINE_COLORS     = [WHITE, "#ddaaff", "#aa88cc"]
LINE_FONT_SIZES = [0, 0, 0]


# ── Helpers ───────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

def heart_polygon(cx, cy, scale=1.0, steps=120):
    pts = []
    for i in range(steps):
        t = 2*math.pi*i/steps
        x =  16*(math.sin(t)**3)
        y = -(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
        pts.extend([cx+x*scale, cy+y*scale])
    return pts

def measure_char_width(root, ch, font_size):
    tmp  = tk.Canvas(root)
    tid  = tmp.create_text(0, 0, text=ch,
                           font=("Segoe UI", font_size, "bold"),
                           anchor="center")
    bbox = tmp.bbox(tid)
    tmp.destroy()
    return (bbox[2]-bbox[0])+2 if bbox else int(font_size*0.6)


# ── Shooting Star ─────────────────────────────────────────────────────────────
class ShootingStar:
    def __init__(self, canvas, W, H):
        self.canvas = canvas
        self.W, self.H = W, H
        angle = random.uniform(20, 50)
        speed = random.uniform(8, 18)
        rad   = math.radians(angle)
        self.x  = random.uniform(0, W)
        self.y  = random.uniform(0, H*0.5)
        self.vx = math.cos(rad)*speed
        self.vy = math.sin(rad)*speed
        self.length = random.randint(40, 120)
        self.alpha  = 1.0
        self.active = True
        color = random.choice([WHITE, GOLD, "#c8c8ff"])
        tx = self.x-self.vx/speed*self.length
        ty = self.y-self.vy/speed*self.length
        self.id = canvas.create_line(tx, ty, self.x, self.y,
                                     fill=color, width=random.uniform(1,2.5),
                                     tags="star_layer")

    def update(self):
        if not self.active: return False
        self.x+=self.vx; self.y+=self.vy; self.alpha-=0.025
        if self.alpha<=0 or self.x>self.W or self.y>self.H:
            self.canvas.delete(self.id); self.active=False; return False
        spd = max(math.hypot(self.vx,self.vy), 0.1)
        tx  = self.x-(self.vx/spd)*self.length*self.alpha
        ty  = self.y-(self.vy/spd)*self.length*self.alpha
        self.canvas.coords(self.id, tx, ty, self.x, self.y)
        g = int(255*self.alpha)
        self.canvas.itemconfig(self.id, fill=f"#{g:02x}{g:02x}{g:02x}")
        return True


# ── Particle ──────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, canvas, cx, cy):
        self.canvas = canvas
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(1.5, 3.5)
        self.vx = math.cos(angle)*speed
        self.vy = math.sin(angle)*speed - 1.5
        ox,oy = random.uniform(-18,18), random.uniform(-12,12)
        r = random.randint(3,5)
        color = random.choice([PINK, PINK_LIGHT, "#ff6b9d", GOLD])
        self.id = canvas.create_oval(cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r,
                                     fill=color, outline="", tags="particle_layer")
        self.life = 0
        self.maxlife = random.randint(28, 50)

    def update(self):
        self.life += 1
        if self.life > self.maxlife:
            self.canvas.delete(self.id); return False
        self.canvas.move(self.id, self.vx, self.vy); self.vy += 0.1
        return True


# ── Flying Letter ─────────────────────────────────────────────────────────────
class FlyingLetter:
    def __init__(self, canvas, char, start_x, start_y,
                 end_x, end_y, delay_frames, font_size=20, land_color=WHITE):
        self.canvas       = canvas
        self.start_x      = start_x; self.start_y = start_y
        self.end_x        = end_x;   self.end_y   = end_y
        self.delay        = delay_frames
        self.elapsed      = 0
        self.total_frames = LETTER_FLY_SPEED   # ← uses timing control
        self.done         = False
        self.land_color   = land_color
        self.ctrl_x       = (start_x+end_x)/2
        self.ctrl_y       = min(start_y,end_y) - random.randint(60,120)
        self.id = canvas.create_text(-200, -200, text=char,
                                     font=("Segoe UI", font_size, "bold"),
                                     fill=WHITE, tags="letter_layer")

    def _bez(self, t):
        x = (1-t)**2*self.start_x + 2*(1-t)*t*self.ctrl_x + t**2*self.end_x
        y = (1-t)**2*self.start_y + 2*(1-t)*t*self.ctrl_y + t**2*self.end_y
        return x, y

    def update(self):
        if self.done: return True
        if self.delay > 0: self.delay -= 1; return True
        self.elapsed += 1
        t  = min(self.elapsed/self.total_frames, 1.0)
        te = t*t*(3-2*t)
        x,y  = self._bez(te)
        mid  = abs(te-0.5)
        glow = max(0.0, 1.0-mid*3.5)
        r = int(0xff+(0xe6-0xff)*glow)
        g = int(0xff+(0x3c-0xff)*glow)
        b = int(0xff+(0x6e-0xff)*glow)
        self.canvas.coords(self.id, x, y)
        self.canvas.itemconfig(self.id, fill=f"#{r:02x}{g:02x}{b:02x}")
        if t >= 1.0:
            self.done = True
            self.canvas.coords(self.id, self.end_x, self.end_y)
            self.canvas.itemconfig(self.id, fill=self.land_color)
        return True

    def delete(self):
        self.canvas.delete(self.id)


# ── Main App ──────────────────────────────────────────────────────────────────
class HeartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heart Lyrics ❤️")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("f",        lambda e: self.toggle_fullscreen())

        self.W  = self.root.winfo_screenwidth()
        self.H  = self.root.winfo_screenheight()
        self.CX = self.W//2
        self.CY = self.H//2 + 50
        self.HEART_SCALE_FACTOR = self.H/680

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#0d0020", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        LINE_FONT_SIZES[0] = max(17, self.H//38)
        LINE_FONT_SIZES[1] = max(14, self.H//46)
        LINE_FONT_SIZES[2] = max(12, self.H//54)

        self.phase        = "envelope"
        self.env_y        = float(self.H+100)
        self.env_open     = 0.0
        self.heart_scale  = 0.0
        self.beat_scale   = 1.0
        self.beat_phase   = 0
        self.beat_growing = True
        self.beat_speed   = 0.005

        self.lyric_idx    = 0
        self.particles    = []
        self.stars        = []
        self.star_timer   = 0
        self.line_letters = [[], [], []]

        line_spacing = max(34, self.H//20)
        self.line_ys = [
            self.CY - int(self.H*0.30),
            self.CY - int(self.H*0.30) + line_spacing,
            self.CY - int(self.H*0.30) + line_spacing*2,
        ]

        self.env_body  = None; self.env_flap  = None
        self.env_heart = None; self.env_lines = []
        self.env_EW    = 300;  self.env_EH    = 200
        self.heart_id  = None; self.shine_id  = None

        self.draw_gradient()
        self.draw_static_stars()
        self.build_envelope()
        self.build_heart()
        self.build_hint()
        self.animate()

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def draw_gradient(self):
        rows = 120; stops = GRAD_COLORS
        for i in range(rows):
            t = i/rows; seg = t*(len(stops)-1); idx = int(seg); loc = seg-idx
            color = stops[-1] if idx >= len(stops)-1 else lerp_color(stops[idx], stops[idx+1], loc)
            y0 = int(i*self.H/rows); y1 = int((i+1)*self.H/rows)+1
            self.canvas.create_rectangle(0, y0, self.W, y1, fill=color, outline="", tags="bg")
        self.canvas.tag_lower("bg")

    def draw_static_stars(self):
        for _ in range(200):
            x = random.randint(0, self.W); y = random.randint(0, int(self.H*0.9))
            r = random.choice([1,1,1,2]); b = random.randint(120,255)
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                    fill=f"#{b:02x}{b:02x}{b:02x}",
                                    outline="", tags="staticstar")

    def build_envelope(self):
        EW,EH = self.env_EW,self.env_EH
        ex = self.CX-EW//2; ey = self.H+100
        self.env_body = self.canvas.create_rectangle(
            ex,ey,ex+EW,ey+EH,fill="#2a0040",outline=PINK,width=2,tags="envelope")
        for i in range(1,4):
            self.env_lines.append(self.canvas.create_line(
                ex+20,ey+40+i*25,ex+EW-20,ey+40+i*25,
                fill="#5a2060",width=1,tags="envelope"))
        self.env_heart = self.canvas.create_text(
            self.CX,ey+EH//2+10,text="❤",font=("Segoe UI",48),fill=PINK,tags="envelope")
        self.env_flap = self.canvas.create_polygon(
            ex,ey,ex+EW//2,ey+EH//2,ex+EW,ey,
            fill="#3a0055",outline=PINK,width=2,tags="envelope")

    def move_envelope(self, new_y):
        EW,EH = self.env_EW,self.env_EH; ex = self.CX-EW//2
        self.canvas.coords(self.env_body, ex,new_y,ex+EW,new_y+EH)
        for i,lid in enumerate(self.env_lines):
            self.canvas.coords(lid,ex+20,new_y+40+(i+1)*25,ex+EW-20,new_y+40+(i+1)*25)
        self.canvas.coords(self.env_heart, self.CX, new_y+EH//2+10)
        self.canvas.coords(self.env_flap,
            ex,new_y,ex+EW//2,new_y-int(EH//2*self.env_open),ex+EW,new_y)

    def delete_envelope(self):
        self.canvas.delete("envelope")

    def build_heart(self):
        self.heart_id = self.canvas.create_polygon(
            heart_polygon(self.CX,self.CY,0.01),
            fill=PINK,outline=PINK_DARK,width=2,smooth=True,tags="heart_layer")
        self.shine_id = self.canvas.create_oval(
            self.CX-2,self.CY-2,self.CX+2,self.CY+2,
            fill="",outline=WHITE,width=2,tags="heart_layer")

    def build_hint(self):
        self.canvas.create_text(
            self.W-10, self.H-10,
            text="ESC = exit fullscreen  |  F = toggle",
            font=("Segoe UI",9), fill="#443355",
            anchor="se", tags="ui_layer")

    def animate(self):
        self.star_timer += 1
        if self.star_timer % 22 == 0:
            self.stars.append(ShootingStar(self.canvas, self.W, self.H))
        self.stars = [s for s in self.stars if s.update()]

        if   self.phase == "envelope":     self._phase_envelope()
        elif self.phase == "heart_emerge": self._phase_emerge()
        elif self.phase == "lyrics":       self._phase_lyrics()

        self.canvas.tag_raise("letter_layer")
        self.canvas.tag_raise("ui_layer")
        self.root.after(16, self.animate)

    def _phase_envelope(self):
        target_y = self.CY-self.env_EH//2-20
        if self.env_y > target_y+2:
            self.env_y -= (self.env_y-target_y)*0.08+2
            self.move_envelope(int(self.env_y))
        else:
            if self.env_open < 1.0:
                self.env_open = min(1.0, self.env_open+0.04)
                self.move_envelope(int(self.env_y))
            else:
                self.phase = "heart_emerge"
                self.root.after(400, self.delete_envelope)

    def _phase_emerge(self):
        hs = self.HEART_SCALE_FACTOR
        if self.heart_scale < 1.0:
            self.heart_scale = min(1.0, self.heart_scale+0.03)
            scale = self.heart_scale*hs*14
            self.canvas.coords(self.heart_id, *heart_polygon(self.CX,self.CY,scale))
            s = self.heart_scale
            self.canvas.coords(self.shine_id,
                self.CX-28*s*hs, self.CY-42*s*hs,
                self.CX-8*s*hs,  self.CY-26*s*hs)
            if random.random() < 0.5:
                self.particles.append(Particle(self.canvas,self.CX,self.CY))
        else:
            self.phase = "lyrics"
            self.root.after(300, self.load_lyric_set)
        self.particles = [p for p in self.particles if p.update()]

    def _phase_lyrics(self):
        hs = self.HEART_SCALE_FACTOR
        self.beat_scale,self.beat_phase,self.beat_growing = self._step_beat()
        s = self.beat_scale*hs*14
        self.canvas.coords(self.heart_id, *heart_polygon(self.CX,self.CY,s))
        bs = self.beat_scale*hs
        self.canvas.coords(self.shine_id,
            self.CX-28*bs, self.CY-42*bs,
            self.CX-8*bs,  self.CY-26*bs)
        if random.random() < 0.22:
            self.particles.append(Particle(self.canvas,self.CX,self.CY))
        self.particles = [p for p in self.particles if p.update()]
        for grp in self.line_letters:
            for l in grp: l.update()

    def load_lyric_set(self):
        for grp in self.line_letters:
            for l in grp: l.delete()
        self.line_letters = [[], [], []]
        lines = LYRICS_LINES[self.lyric_idx % len(LYRICS_LINES)]
        self.lyric_idx += 1
        delay_ms = 0
        for line_idx, line_text in enumerate(lines):
            self._schedule_line(line_idx, line_text, delay_ms)
            delay_ms += (len(line_text) * LETTER_STAGGER + LETTER_FLY_SPEED) * 16
        self.root.after(delay_ms + LINE_STAY_TIME, self.load_lyric_set)

    def _schedule_line(self, line_idx, text, start_ms):
        self.root.after(start_ms,
                        lambda li=line_idx, tx=text: self._launch_line(li, tx))

    def _launch_line(self, line_idx, text):
        font_size  = LINE_FONT_SIZES[line_idx]
        land_color = LINE_COLORS[line_idx]
        land_y     = self.line_ys[line_idx]
        char_widths = [measure_char_width(self.root, ch, font_size) for ch in text]
        total_w = sum(char_widths); cur_x = self.CX-total_w//2
        landing_xs = []
        for w in char_widths:
            landing_xs.append(cur_x+w//2); cur_x += w
        for i, char in enumerate(text):
            fl = FlyingLetter(
                canvas=self.canvas, char=char,
                start_x=self.W+60+random.randint(0,50),
                start_y=self.CY+random.randint(-40,40),
                end_x=landing_xs[i], end_y=land_y,
                delay_frames=i * LETTER_STAGGER,   # ← uses timing control
                font_size=font_size,
                land_color=land_color)
            self.line_letters[line_idx].append(fl)

    def _step_beat(self):
        targets = [1.08, 1.05]
        if self.beat_growing:
            self.beat_scale += self.beat_speed*2
            if self.beat_scale >= targets[self.beat_phase]:
                self.beat_growing = False
        else:
            self.beat_scale -= self.beat_speed
            if self.beat_scale <= 1.0:
                self.beat_scale   = 1.0
                self.beat_phase   = (self.beat_phase+1)%2
                self.beat_growing = True
        return self.beat_scale, self.beat_phase, self.beat_growing


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = HeartApp(root)
    root.mainloop()