"""Bygger medier.csv för fliken 'medier' i DUN – PR-planering.
Kolumner = fälten i Code.gs: id, grupp, medium, format, fokus, prio, epost.
"""
import csv, sys

KOLLA = "Kontrollera att titeln finns kvar. "

T1 = {
  "Rikstäckande dagspress": [
    ("Dagens Nyheter (DN)", "Morgontidning, webb", "Nyheter och Ekonomiredaktionen"),
    ("Svenska Dagbladet (SvD)", "Morgontidning, webb", "Nyheter och Näringsliv"),
    ("Aftonbladet", "Kvällstidning, webb, tv", "Nyheter, ekonomi och konsument"),
    ("Expressen", "Kvällstidning, webb, tv", "Nyheter, ekonomi och konsument"),
    ("Göteborgs-Posten (GP)", "Morgontidning, webb", "Västsverige, näringsliv"),
    ("Sydsvenskan", "Morgontidning, webb", "Skåne och Öresund, näringsliv"),
  ],
  "Affärspress": [
    ("Dagens industri (Di)", "Affärstidning, webb, tv", "Näringsliv, finans, makro"),
    ("Di Digital", "Webb (Dagens industri)", "Tech, data, AI, cybersäkerhet"),
    ("Affärsvärlden", "Affärstidning, webb", "Börs, bolagsanalys"),
    ("Realtid", "Webb", "Finans, affärsjuridik, ekonomisk brottslighet"),
    ("Dagens PS", "Webb", "Näringsliv, börs, privatekonomi"),
    ("Breakit", "Webb, podd", "Tech, startups, riskkapital"),
  ],
  "Public service – radio": [
    ("Ekot (Sveriges Radio)", "Radio, webb", "Riksnyheter"),
    ("Ekonomiekot (Sveriges Radio)", "Radio, webb", "Ekonominyheter"),
    ("P1 Morgon (Sveriges Radio)", "Radio", "Morgonens nyheter och intervjuer"),
    ("Studio Ett (Sveriges Radio)", "Radio", "Fördjupning, aktuella frågor"),
    ("Kaliber (Sveriges Radio)", "Radio, podd", "Granskande journalistik"),
    ("Konflikt (Sveriges Radio)", "Radio, podd", "Säkerhetspolitik, geopolitik, sanktioner"),
  ],
  "Public service – tv": [
    ("Rapport (SVT)", "Tv, webb", "Riksnyheter"),
    ("Aktuellt (SVT)", "Tv", "Nyheter och fördjupning"),
    ("Agenda (SVT)", "Tv", "Politik och samhälle"),
    ("Uppdrag granskning (SVT)", "Tv", "Granskande journalistik"),
    ("SVT Nyheter webb", "Webb, app", "Riksnyheter, ekonomi"),
  ],
  "Kommersiell tv": [
    ("TV4 Nyheterna", "Tv, webb", "Riksnyheter, ekonomi"),
    ("Nyhetsmorgon (TV4)", "Tv", "Morgonsoffa, experter"),
    ("Kalla fakta (TV4)", "Tv", "Granskande journalistik"),
  ],
  "Nyhetsbyråer": [
    ("TT Nyhetsbyrån", "Nyhetsbyrå", "Riksnyheter, ekonomi – sprids till de flesta svenska medier"),
    ("Nyhetsbyrån Direkt", "Nyhetsbyrå", "Finans- och börsnyheter"),
    ("Finwire", "Nyhetsbyrå", "Finans- och börsnyheter"),
    ("Reuters (Stockholm)", "Internationell nyhetsbyrå", "Nordiskt näringsliv och finans"),
    ("Bloomberg (Stockholm)", "Internationell nyhetsbyrå", "Nordiskt näringsliv och finans"),
  ],
  "Nyhetsappar": [
    ("Omni Ekonomi", "Nyhetsapp", "Ekonominyheter, sammanställer från andra medier"),
  ],
  "Debattsidor": [
    ("DN Debatt", "Debattsida", "Rikstäckande debatt"),
    ("SvD Debatt", "Debattsida", "Rikstäckande debatt"),
    ("Di Debatt", "Debattsida", "Näringsliv och ekonomi"),
    ("Aftonbladet Debatt", "Debattsida", "Rikstäckande debatt"),
    ("Expressen Debatt", "Debattsida", "Rikstäckande debatt"),
    ("GP Debatt", "Debattsida", "Västsverige"),
    ("Sydsvenskan Aktuella frågor", "Debattsida", "Skåne och Öresund"),
  ],
}

T2 = {
  "Finans och sparande": [
    ("Placera", "Webb (Avanza)", "Börs, privatsparande"),
    ("EFN", "Webb-tv", "Ekonominyheter, börs"),
    ("Börsvärlden", "Webb", "Börs, bolag"),
    ("Privata Affärer", "Magasin, webb", "Privatekonomi, sparande"),
  ],
  "Juridik och compliance": [
    ("Dagens Juridik", "Webb", "Affärsjuridik, advokatbranschen, regelverk"),
    ("Advokaten", "Tidskrift (Advokatsamfundet)", "Advokater, regelefterlevnad, penningtvätt"),
    ("Infotorg Juridik", "Webb", "Juridiska nyheter"),
    ("Svensk Juristtidning (SvJT)", "Facktidskrift", "Jurister, rättsutveckling"),
  ],
  "Ekonomi, redovisning och revision": [
    ("Balans (FAR)", "Facktidskrift", KOLLA + "Revisorer, redovisningskonsulter"),
    ("Resultat (Srf konsulterna)", "Facktidskrift", KOLLA + "Redovisnings- och lönekonsulter"),
  ],
  "Inköp, handel och logistik": [
    ("Market", "Webb", "Detaljhandel"),
    ("Ehandel.se", "Webb", "E-handel"),
    ("Supply Chain Effect", "Magasin, webb", KOLLA + "Inköp, supply chain"),
    ("Intelligent Logistik", "Magasin, webb", KOLLA + "Logistik, lager, transport"),
    ("Transportnet", "Webb", "Transport och logistik"),
    ("Trailer", "Magasin, webb", "Åkerier, transportbranschen"),
  ],
  "Tech, data och säkerhet": [
    ("Ny Teknik", "Tidning, webb", "Teknik, industri, innovation"),
    ("Computer Sweden", "Webb", KOLLA + "IT-chefer, IT-branschen"),
    ("Voister", "Webb, magasin", "Kundservice, CRM, kunddata"),
    ("Aktuell Säkerhet", "Magasin, webb", "Säkerhet, cyber, risk"),
  ],
  "Marknad och försäljning": [
    ("Dagens Media", "Webb", "Media- och marknadsföringsbranschen"),
    ("Resumé", "Webb", "Kommunikation och marknadsföring"),
  ],
  "Industri och export": [
    ("Elektroniktidningen", "Webb", "Elektronik, komponenter, halvledare"),
    ("Industrinyheter", "Webb", "Tillverkningsindustri"),
  ],
  "Fastighet och bygg": [
    ("Fastighetsvärlden", "Webb", "Fastighetsbranschen"),
    ("Fastighetsnytt", "Webb", "Fastighetsbranschen"),
    ("Byggvärlden", "Webb", "Byggbranschen"),
    ("Byggindustrin", "Tidning, webb", "Byggbranschen"),
  ],
  "Småföretag": [
    ("Driva Eget", "Magasin, webb", "Småföretagare"),
    ("Företagaren", "Tidning (Företagarna)", "Småföretagare, medlemmar i Företagarna"),
  ],
  "Offentlig sektor": [
    ("Dagens Samhälle", "Tidning, webb", "Kommuner, regioner, myndigheter"),
    ("Upphandling24", "Webb", "Offentlig upphandling"),
    ("Nyhetsbyrån Siren", "Nyhetsbyrå", "Offentlig sektor, politik"),
  ],
  "Hållbarhet och ESG": [
    ("Aktuell Hållbarhet", "Magasin, webb", "Hållbarhet, ESG, rapportering"),
  ],
}

REGIONAL = [
  ("Helsingborgs Dagblad (HD)", "Nordvästra Skåne"),
  ("Kristianstadsbladet", "Nordöstra Skåne"),
  ("Ystads Allehanda", "Sydöstra Skåne"),
  ("Trelleborgs Allehanda", "Trelleborg"),
  ("Skånska Dagbladet", "Skåne"),
  ("Norra Skåne", "Norra Skåne"),
  ("Blekinge Läns Tidning (BLT)", "Blekinge"),
  ("Smålandsposten", "Kronoberg"),
  ("Barometern", "Kalmar"),
  ("Jönköpings-Posten (JP)", "Jönköping"),
  ("Hallandsposten", "Halland"),
  ("Hallands Nyheter", "Halland"),
  ("Borås Tidning", "Sjuhärad"),
  ("Bohusläningen", "Bohuslän"),
  ("TTELA", "Trollhättan, Vänersborg"),
  ("Skaraborgs Allehanda (SLA)", "Skaraborg"),
  ("Nya Lidköpings-Tidningen (NLT)", "Lidköping"),
  ("Corren (Östgöta Correspondenten)", "Linköping, Östergötland"),
  ("Norrköpings Tidningar (NT)", "Norrköping"),
  ("Upsala Nya Tidning (UNT)", "Uppsala"),
  ("Enköpings-Posten", "Enköping"),
  ("Eskilstuna-Kuriren", "Eskilstuna, Sörmland"),
  ("Södermanlands Nyheter", "Nyköping, Sörmland"),
  ("Katrineholms-Kuriren", "Katrineholm"),
  ("Vestmanlands Läns Tidning (VLT)", "Västmanland"),
  ("Nerikes Allehanda (NA)", "Örebro"),
  ("Nya Wermlands-Tidningen (NWT)", "Värmland"),
  ("Värmlands Folkblad (VF)", "Värmland"),
  ("Dalarnas Tidningar", "Dalarna"),
  ("Gefle Dagblad", "Gävle"),
  ("Arbetarbladet", "Gävleborg"),
  ("Hudiksvalls Tidning", "Hälsingland"),
  ("Sundsvalls Tidning (ST)", "Sundsvall, Medelpad"),
  ("Allehanda", "Örnsköldsvik, Ångermanland"),
  ("Östersunds-Posten (ÖP)", "Jämtland"),
  ("Länstidningen Östersund (LT)", "Jämtland"),
  ("Västerbottens-Kuriren (VK)", "Umeå, Västerbotten"),
  ("Norran", "Skellefteå"),
  ("Piteå-Tidningen", "Piteå"),
  ("Norrbottens-Kuriren (NK)", "Luleå, Norrbotten"),
  ("Norrländska Socialdemokraten (NSD)", "Norrbotten"),
  ("Gotlands Allehanda", "Gotland"),
  ("Vimmerby Tidning", "Vimmerby"),
  ("Mitt i", "Lokaltidningar i Stockholmsområdet"),
]

T3 = {
  "Regional dagspress": [(n, "Dagstidning, webb", f"{r}, lokalt näringsliv") for n, r in REGIONAL],
  "Regional public service": [
    ("P4 (Sveriges Radio), lokala kanaler", "Radio, webb", "25 lokala kanaler – regionala vinklar"),
    ("SVT regionala nyheter", "Tv, webb", "Regionala redaktioner – regionala vinklar"),
  ],
  "Magasin och opinion": [
    ("Fokus", "Veckomagasin, webb", "Samhälle, politik, fördjupning"),
    ("Kvartal", "Webb, podd", "Samhälle, säkerhetspolitik, fördjupning"),
    ("Dagens ETC", "Dagstidning, webb", "Samhälle, politik"),
  ],
  "Engelskspråkiga medier i Sverige": [
    ("The Local Sweden", "Webb", "Nyheter på engelska för internationella läsare"),
    ("Radio Sweden (Sveriges Radio)", "Radio, webb", "Sveriges Radios nyheter på engelska"),
  ],
  "Poddar": [
    ("Ekonomiekot Extra (Sveriges Radio)", "Podd, radio", "Ekonomisk fördjupning"),
    ("Börspodden", "Podd", "Börs och sparande"),
    ("Fill or Kill", "Podd", "Börs och sparande"),
  ],
}

rows, n = [], {"T1": 0, "T2": 0, "T3": 0}
for tier, groups in (("T1", T1), ("T2", T2), ("T3", T3)):
    for grupp, items in groups.items():
        for medium, fmt, fokus in items:
            n[tier] += 1
            rows.append({"id": f"{tier.lower()}-{n[tier]:03d}", "grupp": grupp, "medium": medium,
                         "format": fmt, "fokus": fokus, "prio": tier, "epost": ""})

names = [r["medium"] for r in rows]
dup = {x for x in names if names.count(x) > 1}
assert not dup, dup

out = sys.argv[1] if len(sys.argv) > 1 else "medier.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "grupp", "medium", "format", "fokus", "prio", "epost"])
    w.writeheader(); w.writerows(rows)
print(out, len(rows), n)
