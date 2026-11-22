/**
 * Copies SEO-CHANGELOG.md from GitHub into a Google Doc, every hour. Free (runs in your Google account).
 *
 * Setup (once): script.google.com > New project > paste this file > set DOC_ID > Save.
 * Run `setup` once and allow the permissions it asks for. That's it.
 */
const DOC_ID = 'PASTE_YOUR_DOC_ID_HERE';   // the long ID in the Google Doc's URL, between /d/ and /edit
const LOG_URL = 'https://raw.githubusercontent.com/tekisolves/tekisolves.github.io/main/SEO-CHANGELOG.md';

function sync() {
  const res = UrlFetchApp.fetch(LOG_URL, { muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) return;   // GitHub unreachable: keep the doc as it is
  const text = res.getContentText();
  const props = PropertiesService.getScriptProperties();
  const hash = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, text));
  if (props.getProperty('hash') === hash) return;   // nothing new

  const body = DocumentApp.openById(DOC_ID).getBody();
  body.clear();
  text.split('\n').forEach(function (line) {
    if (line.startsWith('# ')) body.appendParagraph(line.slice(2)).setHeading(DocumentApp.ParagraphHeading.TITLE);
    else if (line.startsWith('## ')) body.appendParagraph(line.slice(3)).setHeading(DocumentApp.ParagraphHeading.HEADING2);
    else if (line.startsWith('- ')) body.appendListItem(line.slice(2)).setGlyphType(DocumentApp.GlyphType.BULLET);
    else if (line.trim()) body.appendParagraph(line);
  });
  props.setProperty('hash', hash);
}

function setup() {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('sync').timeBased().everyHours(1).create();
  sync();
}
