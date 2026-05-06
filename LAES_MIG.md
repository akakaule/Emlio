# Velkommen til programmering!

## Sådan kommer du i gang

### 1. Installer Python
Hent Python fra https://www.python.org/downloads/
**Vigtigt:** Sæt flueben i "Add Python to PATH" under installation.

### 2. Installer Thonny (anbefales for begyndere)
Hent Thonny fra https://thonny.org
Det er en editor lavet til folk der lige er startet — den viser dine variabler mens programmet kører.

### 3. Kør et program
- Åbn Thonny
- Tryk "Open" og vælg `hilsen.py`
- Tryk på den grønne **Run**-knap (eller F5)

Skriv i det hvide felt nederst når programmet spørger dig om noget.

## Programmerne

### `hilsen.py`
Spørger om dit navn og hilser på dig. Det første program du nogensinde laver!

### `talgaet.py`
Computeren tænker på et tal mellem 1 og 100, og du skal gætte det. Den fortæller dig om dit gæt er for højt eller for lavt.

### `spil.py` — dit første rigtige spil!
Et platformspil i Sonic-stil med **3 baner**, C64-pixeleret grafik, flere monstertyper, lydeffekter, parallax-skyer i baggrunden, valg mellem to sværhedsgrader, robotstemme ved game over og fejringsmelodi når man vinder.

**Banerne:**
- **Bane 1: Skoven** — kun svampe, scroller mod højre
- **Bane 2: Spøgelses-grotten** — svævende spøgelser i Pacman-stil, plus enkelte svampe
- **Bane 3: Skildpadde-bossen** — boss-arena uden scrolling, hop oven på den onde skildpadde for at give skade (3 hits på LET, 5 hits på SVÆR)

**Kontroller:**

I startmenuen:
- **L** — start på LET sværhedsgrad (3 langsomme svampe)
- **S** — start på SVÆR sværhedsgrad (7 hurtige svampe)

Mens man spiller:
- **Venstre/højre piletast** — løb frem og tilbage
- **Op-pil eller mellemrum** — hop (med lyd!)

Når spillet er slut:
- **Mellemrum** — spil samme sværhedsgrad igen
- **M** — tilbage til menuen for at vælge ny sværhedsgrad

**Regler:** Du har 3 liv. Rør du en af svampene fra siden eller nedefra, mister du et liv. **Lander du oven på en svamp, dør den** — men kommer tilbage igen efter 5 sekunder. Når alle 3 liv er væk, er spillet slut. Når du rører det gule flag i højre side af banen, har du vundet!

**Mappestruktur:**
```
spil.py            <- selve spillet
sounds/
  hop.wav          <- lyd ved spring og stomp
  auch.wav         <- lyd når man bliver ramt
  gameover.wav     <- robotstemme der siger "Game over"
  vinder.wav       <- fejringsmelodi når man besejrer bossen
```

**Sådan kører du det:**

Spillet bruger biblioteket Pygame Zero som skal installeres én gang:
```cmd
py -m pip install pgzero
```
Derefter kan du køre spillet:
```cmd
py spil.py
```

## Idéer til at bygge videre

### Bygg `hilsen.py` større
- Spørg også om alder, og fortæl hvor gammel man er om 10 år
- Spørg om yndlingsfarve og brug det i hilsenen
- Lav en regnemaskine: spørg om to tal og læg dem sammen

### Gør `talgaet.py` sjovere
- Lad spilleren vælge sværhedsgrad (1-10, 1-100, 1-1000)
- Sæt en grænse på antal forsøg — så taber man hvis man gætter for mange gange
- Byt om: **du** tænker på et tal, og computeren gætter
- Lad to spillere konkurrere om at finde tallet på færrest forsøg

### Gør `spil.py` sejere
- Tilføj flere platforme i en bane — leg med tallene i `lav_bane_1` eller `lav_bane_2`
- Tilføj flere monstre — kald `lav_svamp(...)` eller `lav_spoegelse(...)` med nye værdier
- Tilføj en helt **bane 4** — kopier `lav_bane_2` og giv den et nyt navn, og hæv grænsen i `start_naeste_bane`
- Lav en ny svampe-farve — udvid `farver`-ordbogen i `byg_sprites`
- Skift hvor pixeleret det er — sæt `PIXEL_SIZE` til 2 (mindre chunky), 6 (meget chunky) eller 1 (slet ingen pixelering)
- Lad monstre respawne hurtigere/langsommere — skift `RESPAWN_FRAMES` (300 = 5 sek)
- Gør bossen sværere — øg HP i `lav_boss` eller hæv hans `vx` (fart)
- Tilføj en ny lyd — generer en ny `.wav` med `wave`-modulet og brug `sounds.dinlyd.play()`
- Lad spøgelser bevæge sig anderledes — `bob_speed` styrer hvor hurtigt de svinger op/ned
- Lav et **point-tæller** der tæller opad mens man spiller
- Tilføj en mønt (gul cirkel) man kan samle op for at få ekstra liv
- Gør banen længere — øg `WORLD_WIDTH` og tilføj flere platforme/svampe
- Tilføj musik der spiller i baggrunden (læg `.ogg`-fil i `music/` og brug `music.play("filnavn")`)
- Erstat de programmerede sprites med rigtige PNG-billeder via Pygame Zero's `Actor`-klasse

## Hvad er det næste?

Når du har leget med `spil.py` og forstået *spil-løkken* (`update` og `draw` der køres mange gange i sekundet), er du klar til at:
- Tilføje flere baner — én pr. fil, eller én stor liste af platforme
- Lave **scrollende** baner der er bredere end skærmen
- Bruge billeder i stedet for firkanter (Pygame Zero har en `Actor`-klasse til netop det)
- Lave et helt andet slags spil: rumskib, snake, pong, brick breaker

God fornøjelse!
