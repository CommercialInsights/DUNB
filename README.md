# Dun & Bradstreet – PR-planering

Samma upplägg som Logivity: en statisk sida (`index.html`) på GitHub Pages som läser och sparar i ett Google Sheet via ett Apps Script. Sidan är lösenordsskyddad.

**Flikar**
1. **Kalender** – planerade utspel med vinkel, status och ansvarig.
2. **Medier** – mediekartläggning i nivå T1 (prioriterade rikstäckande medier), T2 (branschmedier) och T3 (övriga medier). Kollegor kan föreslå ändrad nivå.
3. **Ärenden** – vilka medier som bearbetats, med vad, när och vad det gav.
4. **Klipp** – publiceringar med länk. Markera klipp, välj period eller utspel, så byggs ett mejlutkast som berättar vilka klipp ni fått. Kopiera det (med klickbara länkar) och klistra in i Outlook eller Gmail, eller öppna det direkt i e-postprogrammet. Mejlet finns på svenska och engelska.

Publiceringar som registreras under Ärenden kan föras över till Klipp med en knapp.

## Uppsättning

- **Kalkylark:** *DUN – PR-planering* i Mikaels Drive (id `1KJQaSfRU5DJ9jMU6A63zaP8kkfu6T5nVqsIzis4bLj0`). Flikarna `kalender`, `medier`, `arenden` och `klipp` är tabellerna.
- **Apps Script:** fristående projekt *DUN PR-planering backend*, publicerat som webbapp (kör som Mikael, åtkomst Alla). Koden finns i `apps-script/Code.gs`.
- **Lösenord:** skriptegenskapen `PASSWORD` under *Projektinställningar → Skriptegenskaper*. Byt där – ingen ny publicering behövs.
- **Sidan:** `index.html` på GitHub Pages. `SCRIPT_URL` pekar på webbappen.

När skriptet ändras: *Implementera → Hantera implementeringar → Redigera (pennan) → Version: Ny version → Implementera*, så behålls samma adress.

## Importera medielistan

`medier.csv` innehåller en färdig lista med 127 medier (39 i T1, 34 i T2, 54 i T3).

1. Öppna kalkylarket och gå till fliken `medier` (den skapas av `setup`).
2. *Arkiv → Importera → Ladda upp* och välj `medier.csv`.
3. Välj *Ersätt aktuellt kalkylark* och klicka *Importera data*.

E-postadresserna är tomma och fylls i efterhand, direkt i kalkylarket eller via *Redigera* på sidan. Rader där fältet *fokus* börjar med "Kontrollera att titeln finns kvar" är medier jag inte kunnat bekräfta att de fortfarande ges ut.

Egna medier läggs till med *+ Nytt medium* eller som nya rader i kalkylarket. Lämna `id` tom, så får raden ett automatiskt nästa gång sidan laddas. Kolumnen `prio` ska vara T1, T2 eller T3 (gamla värden A, B, C räknas om automatiskt).

## Data

Allt ligger i kalkylarket, en flik per tabell, och kan redigeras där också. Lösenordet sparas bara i webbläsarfliken tills den stängs.
