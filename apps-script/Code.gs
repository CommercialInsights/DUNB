/**
 * Dun & Bradstreet – PR-planering
 * Backend för index.html. Läser och skriver i kalkylarket "DUN – PR-planering" (SHEET_ID nedan).
 *
 * Varje flik i kalkylarket är en tabell. Rad 1 är rubriker (fältnamnen nedan).
 * Sidan skickar POST med { action, table, item/items/id, password } och får
 * alltid tillbaka hela datamängden: { ok, kalender, medier, arenden, klipp }.
 *
 * Lösenordet sätts under Projektinställningar → Skriptegenskaper → PASSWORD.
 */

const SHEET_ID = '1KJQaSfRU5DJ9jMU6A63zaP8kkfu6T5nVqsIzis4bLj0';
const ss_ = () => SpreadsheetApp.openById(SHEET_ID);

const TABLES = {
  kalender: ['id', 'forberedelse', 'publicering', 'aktivitet', 'vinkel', 'status', 'ansvarig', 'kommentar'],
  medier:   ['id', 'grupp', 'medium', 'format', 'fokus', 'prio', 'epost', 'forslag', 'forslagKommentar', 'foreslagenAv'],
  arenden:  ['id', 'datum', 'medium', 'kanal', 'amne', 'ansvarig', 'status', 'nastaSteg', 'nastaDatum', 'kommentar',
             'pubDatum', 'pubTyp', 'pubRubrik', 'pubLank'],
  klipp:    ['id', 'datum', 'medium', 'rubrik', 'lank', 'typ', 'amne', 'talesperson', 'rackvidd', 'kommentar', 'arende']
};

// ---------- Webbapp ----------

function doGet() {
  return ContentService.createTextOutput('DUN PR-planering: backend är igång.');
}

function doPost(e) {
  let req;
  try {
    req = JSON.parse(e.postData.contents);
  } catch (err) {
    return json_({ ok: false, error: 'bad_request', message: 'Ogiltig förfrågan' });
  }

  const pw = PropertiesService.getScriptProperties().getProperty('PASSWORD');
  if (!pw) return json_({ ok: false, error: 'setup', message: 'Lösenord är inte satt i skriptegenskaperna.' });
  if (String(req.password || '') !== pw) {
    Utilities.sleep(800); // bromsar gissningar
    return json_({ ok: false, error: 'auth', message: 'Fel lösenord' });
  }

  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const table = req.table;
    if (req.action !== 'list' && !TABLES[table]) throw new Error('Okänd tabell: ' + table);

    switch (req.action) {
      case 'list': break;
      case 'save': saveItem_(table, req.item || {}); break;
      case 'saveMany': (req.items || []).forEach(it => saveItem_(table, it)); break;
      case 'delete': deleteItem_(table, req.id); break;
      default: throw new Error('Okänd åtgärd: ' + req.action);
    }
    return json_(Object.assign({ ok: true }, readEverything_()));
  } catch (err) {
    return json_({ ok: false, error: 'server', message: String(err.message || err) });
  } finally {
    try { lock.releaseLock(); } catch (e) {}
  }
}

// ---------- Tabeller ----------

function sheet_(name) {
  const ss = ss_();
  let sh = ss.getSheetByName(name);
  const fields = TABLES[name];
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, sh.getMaxRows(), Math.max(fields.length, sh.getMaxColumns())).setNumberFormat('@');
  }
  // Se till att alla rubriker finns (nya fält läggs till längst till höger)
  const lastCol = Math.max(sh.getLastColumn(), 1);
  const head = sh.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
  const missing = fields.filter(f => head.indexOf(f) === -1);
  if (missing.length || !head[0]) {
    const start = head[0] ? lastCol + 1 : 1;
    sh.getRange(1, start, 1, missing.length).setValues([missing]).setFontWeight('bold');
    sh.getRange(1, start, sh.getMaxRows(), missing.length).setNumberFormat('@');
    sh.setFrozenRows(1);
  }
  return sh;
}

function headers_(sh) {
  return sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(String);
}

function cell_(v) {
  if (v instanceof Date) return Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  return v == null ? '' : String(v);
}

function readTable_(name) {
  const sh = sheet_(name);
  const last = sh.getLastRow();
  if (last < 2) return [];
  const head = headers_(sh);
  const rows = sh.getRange(2, 1, last - 1, head.length).getValues();
  // Rader som klistrats in direkt i kalkylarket utan id får ett, så att de kan redigeras från sidan
  const idCol = head.indexOf('id');
  let changed = false;
  rows.forEach(r => {
    if (idCol !== -1 && !String(r[idCol]).trim() && r.some(v => v !== '' && v != null)) {
      r[idCol] = Utilities.getUuid().slice(0, 8); changed = true;
    }
  });
  if (changed) sh.getRange(2, idCol + 1, rows.length, 1).setNumberFormat('@').setValues(rows.map(r => [r[idCol]]));
  return rows
    .filter(r => r.some(v => v !== '' && v != null))
    .map(r => {
      const o = {};
      head.forEach((h, i) => { if (h) o[h] = cell_(r[i]); });
      return o;
    });
}

function readEverything_() {
  const out = {};
  Object.keys(TABLES).forEach(t => { out[t] = readTable_(t); });
  return out;
}

function findRow_(sh, id) {
  if (!id) return -1;
  const last = sh.getLastRow();
  if (last < 2) return -1;
  const head = headers_(sh);
  const col = head.indexOf('id') + 1;
  const ids = sh.getRange(2, col, last - 1, 1).getValues().map(r => String(r[0]));
  const i = ids.indexOf(String(id));
  return i === -1 ? -1 : i + 2;
}

function saveItem_(name, item) {
  const sh = sheet_(name);
  const head = headers_(sh);
  if (!item.id) item.id = Utilities.getUuid().slice(0, 8);
  let row = findRow_(sh, item.id);
  if (row === -1) row = sh.getLastRow() + 1;
  const current = row <= sh.getLastRow() ? sh.getRange(row, 1, 1, head.length).getValues()[0] : head.map(() => '');
  const values = head.map((h, i) => (h in item ? String(item[h] == null ? '' : item[h]) : current[i]));
  sh.getRange(row, 1, 1, head.length).setNumberFormat('@').setValues([values]);
  return item.id;
}

function deleteItem_(name, id) {
  const sh = sheet_(name);
  const row = findRow_(sh, id);
  if (row !== -1) sh.deleteRow(row);
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// ---------- Installation ----------

/**
 * Kör en gång från redigeraren: skapar flikarna och lägger in en första
 * aktivitet i kalendern. Medielistan lämnas tom.
 */
function setup() {
  const ss = ss_();
  // Har kalkylarket skapats från medier.csv heter fliken något annat – döp om den till "medier"
  if (!ss.getSheetByName('medier')) {
    const withMedia = ss.getSheets().find(sh => sh.getLastColumn() > 2 &&
      sh.getRange(1, 1, 1, 3).getValues()[0].join(',') === 'id,grupp,medium');
    if (withMedia) withMedia.setName('medier');
  }
  Object.keys(TABLES).forEach(sheet_);
  ['Blad1', 'Sheet1'].forEach(n => {
    const sh = ss.getSheetByName(n);
    if (sh && sh.getLastRow() === 0 && ss.getSheets().length > 1) ss.deleteSheet(sh);
  });

  if (readTable_('kalender').length === 0) {
    saveItem_('kalender', {
      publicering: '2026-10-22 (tor)',
      forberedelse: '2026-10-21',
      aktivitet: 'EU:s största sanktionslistning hittills – rapid response med Theodora Papadimitropoulou',
      vinkel: 'EU:s svarta lista växte med en tredjedel. En kund eller leverantör som var godkänd i september kan ha en ' +
              'sanktionerad ägare i dag – och förbudet gäller även indirekta kopplingar. Hur långt ner i ägar- och ' +
              'leverantörskedjan behöver svenska bolag kontrollera?',
      status: 'Pågår',
      ansvarig: 'Christine Bard',
      kommentar: 'Pitch till svensk näringslivspress. Kalla det "sanktionslistning", inte "22:a paketet".'
    });
  }
  const pw = PropertiesService.getScriptProperties().getProperty('PASSWORD');
  Logger.log(pw ? 'Klart. Lösenord är satt.' : 'Klart. Sätt PASSWORD under Projektinställningar → Skriptegenskaper.');
}
