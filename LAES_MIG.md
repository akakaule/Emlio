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
Et platformspil i Sonic-stil med en lang scrollende bane, sprite-grafik, flere svampetyper, lydeffekter og parallax-skyer i baggrunden.

**Kontroller:**
- **Venstre/højre piletast** — løb frem og tilbage
- **Op-pil eller mellemrum** — hop (med lyd!)
- **Mellemrum** — start forfra når spillet er slut

**Regler:** Du har 3 liv. Rør du en af svampene (der findes 3 forskellige farver med forskellig fart), mister du et liv. Når alle 3 liv er væk, er spillet slut. Når du rører det gule flag i højre side af banen, har du vundet!

**Mappestruktur:**
```
spil.py            <- selve spillet
sounds/
  hop.wav          <- lyd ved spring
  auch.wav         <- lyd når man bliver ramt
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
- Tilføj flere platforme — leg med tallene i `flydende_platforme`-listen
- Tilføj flere svampe — kald `lav_svamp(...)` med nye værdier i `svampe`-listen
- Lav en helt ny svampe-farve — udvid `sprite_svampe`-ordbogen i `byg_sprites`
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
