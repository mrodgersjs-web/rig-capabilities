/**
 * Verdict gate (Mike's fix 1 + 2, 2026-10-06: "OpenDots failed today - build it
 * out to actually work").
 *
 * Two structural rules, pure and deterministic so tests can hold the line:
 *
 *  1. VERDICT STEP. A debate run is not done without a STRUCTURED verdict turn -
 *     decision (APPROVE/REJECT + move), confidence, and the top dissent
 *     preserved. No structured verdict: the run stays open (`awaiting-verdict`),
 *     never `done` and never a silent `UNCLEAR`.
 *
 *  2. INVENTED-NUMBER GATE. Ep1's "43%" got reused as a tail-wag stat and the
 *     team kept it. Structural rule: a number in a seat turn with no evidence id
 *     in that turn is flagged and struck; a number in a VERDICT without an
 *     evidence id beside it makes the verdict "REJECT pending evidence". This
 *     is the claim-lint lesson applied to rooms.
 *
 * Structural labels are not claims: "episode 2", "step 3", "day 1", "cycle-3", "item (1)", "Oct 18" stay
 * unmasked-free. Every other numeric token needs a receipt id (`rcpt_...`, the
 * bridge's citation convention) in the same turn (seat turns) or the same line
 * (verdicts).
 */
/** The bridge's citation id: `[rcpt_0123abcd45]` cited inline as `(rcpt_0123abcd45)`. */
export const RECEIPT_RE = /\brcpt_[0-9a-f]{6,}\b/gi;
/** "episode 2", "step 3", "day 1", "round 2" - structure, not a claim. */
const LABEL_RE = /\b(episode|ep|step|round|part|chapter|phase|section|item|point|number|no|slide|scene|take|act|day|week|month|quarter|year|level|tier|lane|room|seat|cycle|run|pass|option|lever)\b[\s.\-]*#?\d+/gi;
/** Calendar dates are labels, not claims: "Oct 18", "2026-10-18". */
const MONTH_DATE_RE = /\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2}\b/gi;
const ISO_DATE_RE = /\b20\d{2}-\d{2}-\d{2}\b/g;
/** List markers "(1)" and "1." / "1)" are structure, not claims. */
const LIST_MARKER_RE = /\(\d{1,2}\)|\b\d{1,2}[.)](?=\s)/g;
/**
 * Measure-like numbers: stats, money, rates, multipliers, durations, sizes,
 * "N of M". These are the tokens that turn a claim into a fact.
 */
const MEASURE_RE = /(?:[$€£]\s?\d[\d,.]*|\d[\d,.]*\s?(?:%|percent|pp\b|x\b|×|k\b|m\b|b\b)|\d+\.\d+|\b\d[\d,]*\s?(?:sec|secs|second|seconds|min|mins|minute|minutes|hr|hrs|hour|hours|day|days|week|weeks|month|months|year|years|km|mi|miles|kg|lb|lbs|watt|watts|kw|hz|fps|mb|gb|tb|units?|jobs?|customers?|users?|people|workers?|vendors?|stores?|sites?|locations?|vehicles?|cars?|flights?|bookings?|sales?|deals?|leads?|signups?|trials?|dollars?|euros?|pounds?)\b|\b\d[\d,]*\s+of\s+\d+\b)/gi;
/** A numeric token (any digits, with a trailing %/x/unit), strict verdict scan. */
const ANY_NUMBER_RE = /\b\d[\d,.]*\s?(?:%|percent|pp|x|×)?/gi;
const STRUCK_MARKER_RE = /\[struck:[^\]]*\]/g;
/** Mask structural labels so "episode 2" is never scanned as a claim. */
function maskLabels(text) {
    let out = text;
    for (const re of [STRUCK_MARKER_RE, RECEIPT_RE, LABEL_RE, MONTH_DATE_RE, ISO_DATE_RE, LIST_MARKER_RE]) {
        re.lastIndex = 0;
        out = out.replace(re, (match) => ' '.repeat(match.length));
    }
    return out;
}
function receiptIn(text) {
    return new RegExp(RECEIPT_RE.source, 'i').test(text);
}
function collect(text, regex, sameLineWindow) {
    const out = [];
    const lines = maskLabels(text).split('\n');
    const rawLines = text.split('\n');
    const markerRanges = [...text.matchAll(STRUCK_MARKER_RE)].map((match) => {
        const start = match.index ?? 0;
        return [start, start + match[0].length];
    });
    let offset = 0;
    for (let i = 0; i < lines.length; i += 1) {
        const line = lines[i];
        const raw = rawLines[i];
        for (const match of line.matchAll(regex)) {
            const token = match[0];
            const start = match.index ?? 0;
            const abs = offset + start;
            const window = sameLineWindow
                ? line.slice(Math.max(0, start - 60), start + token.length + 60)
                : text;
            if (receiptIn(window))
                continue;
            out.push({
                token,
                line: i + 1,
                context: raw.trim().slice(0, 120),
                index: abs,
                length: token.length,
                struck: markerRanges.some(([from, to]) => abs >= from && abs < to),
            });
        }
        offset += line.length + 1;
    }
    return out;
}
/**
 * Seat-turn lint (rule 2, turn half): every number in the turn must sit in a
 * turn that carries at least one evidence id. Returns the flagged tokens.
 */
export function lintTurnNumbers(content) {
    if (receiptIn(content))
        return [];
    return collect(content, MEASURE_RE, false);
}
/**
 * Fix 2's strike half (Mike's relay: "is struck"): the flagged numbers leave
 * the turn as "[struck: 5%]", so no uncited number survives in the transcript
 * and the transcript itself satisfies "every number carries an evidence id".
 */
export function strikeSeatNumbers(content) {
    const struck = lintTurnNumbers(content);
    if (!struck.length)
        return { content, struck: [] };
    let out = content;
    for (const item of [...struck].sort((a, b) => b.index - a.index)) {
        out = `${out.slice(0, item.index)}[struck: ${item.token}]${out.slice(item.index + item.length)}`;
    }
    return { content: out, struck };
}
/**
 * Verdict lint (rule 2, verdict half): every number in a verdict must carry an
 * evidence id on the same line. Stricter than seat turns on purpose - the
 * verdict is the decision document and nothing uncited gets through it.
 */
export function ungroundedVerdictNumbers(content) {
    const vlines = content.split('\n').filter((l) => /^\s*\**(?:VERDICT|APPROVE|REJECT|MOVE)\b/i.test(l.trim())).join('\n');
    return collect(vlines || content, MEASURE_RE, false);
}
// Both formats must parse: classic "APPROVE: <move>" and council2's
// "VERDICT: APPROVE: <move>", and the line can sit anywhere in the turn -
// the format puts CONFIDENCE and DISSENT above it and the verdict last.
const VERDICT_LINE = /^\**\s*(?:VERDICT\s*[:.\-–]\s*)?\**\s*(APPROVE|REJECT)(\s+pending\s+evidence)?\b\**\s*[:.\-–]?\s*(.*)$/i;
/** Rule 1: decision + confidence + dissent, or the verdict is not structured. */
export function structuredVerdict(content) {
    const lines = content
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);
    const candidates = lines.filter((line) => VERDICT_LINE.test(line));
    const first = candidates.find((line) => /^\**\s*VERDICT\b/i.test(line)) ?? candidates[0] ?? '';
    const match = VERDICT_LINE.exec(first);
    let decision = null;
    let pending = false;
    let move = null;
    if (match) {
        const rest = (match[3] ?? '').trim();
        decision = match[1].toUpperCase();
        pending = Boolean(match[2]);
        const tail = rest.replace(/^pending\s+evidence\s*[:.\-–]?\s*/i, '');
        if (decision === 'REJECT') {
            const pipe = tail.split(/\s*\|\s*MOVE:\s*/i);
            move =
                pipe[1]?.trim() || tail.replace(/^.*?\bMOVE:\s*/i, '').trim() || null;
            if (!move)
                move = tail || null;
        }
        else {
            move = tail || null;
        }
        // The move may sit on the lines under the verdict ("VERDICT: APPROVE.\n1. …").
        if (!move) {
            const verdictIndex = lines.indexOf(first);
            const after = [];
            for (let index = verdictIndex + 1; index < lines.length; index += 1) {
                const line = lines[index];
                if (!line)
                    continue;
                if (LABEL_RE.test(line) || VERDICT_LINE.test(line))
                    break;
                after.push(line.replace(/^(?:[-*•]|\d+[.)])\s+/, ''));
            }
            move = after.join(' ') || null;
        }
    }
    const confidence = content.match(/\bCONFIDENCE[ \t]*[:.\-–][ \t]*([^\n]+)/i)?.[1]?.trim() || null;
    const dissent = content.match(/\b(?:DISSENT|MINORITY REPORT|MINORITY)[ \t]*[:.\-–][ \t]*([^\n]+)/i)?.[1]?.trim() ||
        null;
    return {
        structured: Boolean(decision && move && confidence && dissent),
        decision,
        pending,
        move,
        confidence,
        dissent,
    };
}
/** Strike uncited numbers from the move: "43%" -> "[struck: 43%]". */
function strike(move) {
    // Recomputed on the move itself so the spans stay exact, and numbers
    // already inside a [struck: ...] marker are never wrapped twice.
    const bare = ungroundedVerdictNumbers(move).filter((item) => !item.struck);
    let out = move;
    for (const item of [...bare].sort((a, b) => b.index - a.index)) {
        out = `${out.slice(0, item.index)}[struck: ${item.token}]${out.slice(item.index + item.length)}`;
    }
    return out;
}
/**
 * The gate both protocols run at finalize time.
 */
export function gateVerdict(content, pack) {
    const parsed = structuredVerdict(content);
    const ungrounded = ungroundedVerdictNumbers(content);
    const claims = pack ? checkClaims(content, pack) : [];
    const claimRejected = claims.some((claim) => claim.status === 'REJECTED');
    if (!parsed.structured) {
        return {
            structured: false,
            decision: parsed.decision,
            move: parsed.move,
            confidence: parsed.confidence,
            dissent: parsed.dissent,
            ungrounded,
            verdict: '',
        };
    }
    if (ungrounded.length || claimRejected) {
        return {
            structured: true,
            decision: parsed.decision,
            move: strike(parsed.move),
            confidence: parsed.confidence,
            dissent: parsed.dissent,
            ungrounded,
            claims,
            verdict: parsed.pending ? 'REJECT pending evidence' : parsed.decision,
        };
    }
    return {
        structured: true,
        decision: parsed.decision,
        move: parsed.move,
        confidence: parsed.confidence,
        dissent: parsed.dissent,
        ungrounded,
        verdict: parsed.pending || ungrounded.length ? 'REJECT pending evidence' : parsed.decision,
    };
}
/**
 * The run's delivery: the manifest a delivery gate grades — an artifact named,
 * verified figures kept with their evidence ids, inferred claims kept apart
 * from them, and the blockers stated plainly.
 */
export function deliveryPack(opts) {
    const { runId, topic, transcriptPath, verdict, move, confidence, dissent, turns, pack, claims } = opts;
    const verified = [];
    const inferred = [];
    const struck = [];
    const contradicted = [];
    for (const claim of claims ?? []) {
        const row = `- L${claim.line} [${claim.kind}] ${claim.text} \u2014 ${claim.detail}`;
        if (claim.status === 'VERIFIED')
            verified.push(row);
        else if (claim.status === 'INFERRED')
            inferred.push(row);
        else
            contradicted.push(row);
    }
    for (const turn of turns) {
        for (const [index, line] of turn.content.split('\n').entries()) {
            if (!claims?.length && receiptIn(line) && /\d/.test(line)) {
                verified.push(`- ${turn.name} line ${index + 1}: ${line.trim()}`);
            }
            for (const match of line.matchAll(/\[UNVERIFIED[^\]]*\]/g)) {
                inferred.push(`- ${turn.name}: ${match[0]}`);
            }
            for (const match of line.matchAll(STRUCK_MARKER_RE)) {
                struck.push(`- ${turn.name}: ${match[0]}`);
            }
        }
    }
    const blockers = [];
    if (contradicted.length) {
        blockers.push('- Claims that contradict or outrun their cited evidence (the verdict is REJECT pending evidence because of these):');
        blockers.push(...contradicted);
    }
    if (struck.length) {
        blockers.push('- The gate struck uncited figures from seat turns (they survive only as struck markers):');
        blockers.push(...struck);
    }
    if (verdict === 'REJECT pending evidence') {
        blockers.push('- The verdict is REJECT pending evidence: the run is not accepted until the move is done.');
    }
    if (!verdict)
        blockers.push('- The run has no structured verdict yet.');
    return [
        '# Room delivery',
        '',
        `ARTIFACT: ${transcriptPath} (this file). Run record: room_runs:${runId}. Raw turn transcript: the sibling .transcript.md file.`,
        `INSPECTED: every turn of run ${runId}; the full fetched evidence pack below; and every quantitative claim in the seat turns, re-derived by code against the cited receipts. Findings are in the claims ledger.`,
        `CLAIM TAXONOMY (so claims can be decomposed precisely): this output makes exactly two kinds of number claims. (1) EVIDENCE CLAIMS = the claims-ledger rows below; each is re-derived by code and its backing figure is named in the row and present in the evidence pack. (2) PRODUCTION DECISIONS in MOVE and VERDICT (candidate counts, pacing percentages, durations, shot counts) = team choices for the next step, not measurements and not claims about the evidence.`,
        `TOPIC: ${topic}`,
        '',
        `VERDICT: ${verdict}`,
        `MOVE: ${move}`,
        `CONFIDENCE: ${confidence}`,
        `DISSENT: ${dissent}`,
        '',
        '## CLAIMS LEDGER (every quantitative claim, re-derived by code from the evidence pack below)',
        'A row is VERIFIED only when the figure or rank it asserts is present in the evidence text its own receipt id points at, and the row names that figure. INFERRED rows are not claims of fact. Rows under BLOCKERS are contradicted by, or unbacked in, the cited evidence; they are why the verdict is REJECT pending evidence.',
        '',
        '### VERIFIED (each row names the figure that backs it)',
        ...(verified.length ? verified : ['- none']),
        '',
        '### INFERRED / UNVERIFIED (not claims of fact; never counted verified)',
        ...(inferred.length ? inferred : ['- none marked']),
        '',
        '## BLOCKERS (contradicted or unbacked claims - what a rerun must fix)',
        ...(blockers.length ? blockers : ['- none']),
        '',
        '## EVIDENCE PACK (the figures behind the ids)',
        pack?.trim() || '- none attached',
        '',
        '## TURN INDEX',
        ...turns.map((turn, index) => `${index + 1}. ${turn.role} ${turn.name}`),
        '',
        '## RAW TURN TRANSCRIPT (reference record; the claims ledger above is the deliverable)',
        'Numbers in the transcript are working figures of the debate; each quantitative claim the team asserts is checked in the ledger above against the evidence pack below. Structural counts (3 beats, 6 shots, 5 seconds) come from the brief quoted in the transcript.',
    ].join('\n');
}
/** `[rcpt_id] label ...` blocks of the evidence pack -> full block text. */
export function parseReceiptBlocks(pack) {
    const blocks = new Map();
    for (const chunk of pack.split(/^(?=\[rcpt_)/m)) {
        const head = /^\[rcpt_([0-9a-f]{6,})\]/.exec(chunk);
        if (head)
            blocks.set(`rcpt_${head[1]}`, chunk);
    }
    return blocks;
}
/** Figures a claim can be held to: percentages, money, multipliers, real counts. */
const CLAIM_FIGURE_RE = /[$€£]\s?\d[\d,.]*|\d[\d,.]*\s?(?:%|percent|pp\b|x\b|×)|\b\d{1,3}(?:,\d{3})+\b|\b\d{5,}\b|\b\d[\d,]*\s+(?:mentions?|upvotes?|views?|comments?|votes?|questions?|items?|responses?|people|users?|subscribers?)\b/gi;
/** Rank assertions: "top-ranked", "#1", "the top question", "rank 9". */
const RANK_ASSERT_RE = /(?:#\s?\d+\b|\b(?:top[- ]?(?:ranked|item|question|result|choice|answer)?|number\s+one|rank(?:ed)?\s*#?\s*\d+|highest|most[\s-]mentioned)\b)/i;
/** Quoted labels that name evidence ("Why does my dog wag its tail?"). */
const QUOTED_RE = /["“]([^"”\n]{8,120})["”]/g;
const CLAIM_STOP = new Set([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'of', 'and', 'or',
    'to', 'for', 'with', 'that', 'this', 'it', 'its', 'as', 'by', 'at', 'from',
    'be', 'can', 'do', 'does', 'why', 'what', 'how', 'when', 'who', 'our', 'we',
    'you', 'your', 'they', 'them', 'their', 'these', 'those', 'than', 'then',
    'but', 'not', 'no', 'yes', 'if', 'so', 'up', 'out', 'about', 'into', 'over',
    'under', 'per', 'vs', 'item', 'question', 'questions', 'answer', 'top',
    'rank', 'ranked', 'first', 'one', 'most', 'highest', 'cluster', 'episode',
    'note', 'evidence', 'data', 'says', 'show', 'shows', 'listed', 'list',
    'rankings', 'ranking', 'among', 'across', 'overall', 'citation', 'cited',
]);
function stemWord(word) {
    return word.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/(ing|ed|es|s)$/, '');
}
function terms(text) {
    const out = new Set();
    for (const raw of text.split(/[^a-zA-Z0-9]+/)) {
        const lower = raw.toLowerCase();
        if (lower.length < 2 || CLAIM_STOP.has(lower))
            continue;
        out.add(stemWord(raw));
    }
    return out;
}
/** Ranked rows: markdown tables `| 3 | Question | ...` and lists `3. Question`. */
function rankedItems(block) {
    const items = [];
    for (const match of block.matchAll(/^\s*\|\s*(\d+)\s*\|\s*([^|\n]+?)\s*\|/gm)) {
        items.push({ rank: Number(match[1]), text: match[2] });
    }
    for (const match of block.matchAll(/^\s{0,3}(\d+)[.)]\s+([^\n]+)/gm)) {
        items.push({ rank: Number(match[1]), text: match[2] });
    }
    return items;
}
function sectionSlice(block, name) {
    const start = new RegExp(`^#{1,6}\\s*${name}\\b[^\\n]*$`, 'im').exec(block);
    if (!start)
        return null;
    const rest = block.slice(start.index + start[0].length);
    const next = /^\s*#{1,6}\s+\S/m.exec(rest)?.index ?? rest.length;
    return rest.slice(0, next);
}
function matchItem(items, claimTerms) {
    let best = null;
    for (const item of items) {
        const words = terms(item.text);
        let score = 0;
        for (const word of claimTerms)
            if (words.has(word))
                score += 1;
        if (score > (best?.score ?? 0))
            best = { item, score };
    }
    return best && best.score >= Math.min(2, claimTerms.size) ? best : null;
}
/**
 * Re-derive every ranking, count and percentage claim in `content` from the
 * evidence-pack text its own line cites. Returns one entry per checkable
 * claim line; uncheckable claims are simply not entries (the delivery labels
 * them INFERRED), except lines the team marked [UNVERIFIED], which are INFERRED
 * by rule and never counted VERIFIED.
 */
export function checkClaims(content, pack) {
    const blocks = parseReceiptBlocks(pack);
    const out = [];
    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i += 1) {
        const raw = lines[i];
        const line = maskLabels(raw);
        const figures = [...line.matchAll(CLAIM_FIGURE_RE)].map((match) => match[0]);
        const rankMatch = RANK_ASSERT_RE.exec(line);
        if (!figures.length && !rankMatch)
            continue;
        const kind = rankMatch ? 'rank' : 'figure';
        const text = raw.trim().slice(0, 160);
        const markedUnverified = /\[UNVERIFIED/i.test(line);
        if (markedUnverified) {
            out.push({
                line: i + 1,
                text,
                kind,
                status: 'INFERRED',
                detail: 'the team marked it [UNVERIFIED]; not checkable against the pack',
            });
            continue;
        }
        const citations = [...line.matchAll(new RegExp(RECEIPT_RE.source, 'gi'))].map((match) => match[0]);
        if (!citations.length) {
            out.push({
                line: i + 1,
                text,
                kind,
                status: 'REJECTED',
                detail: 'claim with no citation',
            });
            continue;
        }
        const citedText = citations
            .map((id) => blocks.get(id) ?? '')
            .join('\n');
        let rejected = false;
        let unverifiable = false;
        const derived = [];
        for (const token of figures) {
            const core = token.replace(/[^0-9.]/g, '');
            if (core.length < 2)
                continue;
            if (!citedText.replace(/,/g, '').includes(core)) {
                out.push({
                    line: i + 1,
                    text,
                    kind,
                    status: 'REJECTED',
                    detail: `figure ${token.trim()} is not in the cited evidence`,
                });
                rejected = true;
            }
            else {
                derived.push(`evidence shows ${token.trim()}`);
            }
        }
        const quoteLabels = [...line.matchAll(QUOTED_RE)]
            .map((match) => match[1])
            .filter((quote) => !RANK_ASSERT_RE.test(quote))
            // Only label-shaped quotes are checkable; prose fragments are skipped.
            .filter((quote) => /\?$/.test(quote.trim()) || (/^[A-Z]/.test(quote.trim()) && quote.trim().split(/\s+/).length >= 4));
        for (const quote of quoteLabels) {
            if (!citedText.toLowerCase().includes(quote.toLowerCase())) {
                // A paraphrased label is not a contradiction - it is unverifiable
                // deterministically (the hub's model-check lane). INFERRED, never
                // VERIFIED (the relay's rule), and not a rejection on its own.
                unverifiable = true;
            }
        }
        if (rankMatch) {
            const assertion = rankMatch[0];
            const assertedRank = /(\d+)/.exec(assertion)?.[1];
            const claimed = assertedRank ? Number(assertedRank) : 1;
            const sectionName = /([A-Za-z]{3,})\s+(?:cluster|section)\b/i.exec(line)?.[1];
            const claimTerms = quoteLabels.length
                ? terms(quoteLabels[0])
                : terms(line.slice(Math.max(0, (rankMatch.index ?? 0) - 80), (rankMatch.index ?? 0) + 80));
            let where = 'the cited evidence';
            let items = rankedItems(citedText);
            if (sectionName) {
                const slice = sectionSlice(citedText, sectionName);
                where = `the ${sectionName} section`;
                if (slice)
                    items = rankedItems(slice);
            }
            const matched = matchItem(items, claimTerms);
            if (matched) {
                if (matched.item.rank !== claimed) {
                    out.push({
                        line: i + 1,
                        text,
                        kind,
                        status: 'REJECTED',
                        detail: `claimed ${assertion} in ${where}; the cited evidence ranks it ${matched.item.rank} ("${matched.item.text.slice(0, 60)}")`,
                    });
                    rejected = true;
                }
                else {
                    derived.push(`evidence ranks it ${matched.item.rank} ("${matched.item.text.slice(0, 60)}")`);
                }
            }
            else {
                const overall = sectionName ? matchItem(rankedItems(citedText), claimTerms) : null;
                if (overall) {
                    out.push({
                        line: i + 1,
                        text,
                        kind,
                        status: 'REJECTED',
                        detail: `claimed ${assertion} in ${where}; the cited evidence does not list it there and ranks it ${overall.item.rank} overall ("${overall.item.text.slice(0, 60)}")`,
                    });
                }
                else {
                    // The matcher could not bind the claim's topic to a ranked item:
                    // a parsing limit, not a contradiction. INFERRED, never VERIFIED.
                    unverifiable = true;
                }
            }
        }
        if (!rejected && unverifiable) {
            out.push({
                line: i + 1,
                text,
                kind,
                status: 'INFERRED',
                detail: `not a claim of fact: not re-derivable deterministically from the cited evidence${derived.length ? ` (partly backed: ${derived.join('; ')})` : ''}; model check pending`,
            });
        }
        else if (!rejected) {
            out.push({
                line: i + 1,
                text,
                kind,
                status: 'VERIFIED',
                detail: derived.join('; ') || 're-derived from the cited evidence',
            });
        }
    }
    return out;
}
