// Token table transcribed from MASTER-CREATIVE-PROMPT v3.0 §3 (site-v2/docs/design-system/).
// Single source of truth: SidePanel renders it, the dev-handoff export serializes it.

export const TOKEN_SET_NAME = 'MASTER-CREATIVE-PROMPT v3.0';

export const COLOR_TOKENS: { name: string; value: string; role: string; theme: string }[] = [
  { name: '--void', value: '#FAF7F2', role: 'page background — warm ivory', theme: 'light' },
  { name: '--cream', value: '#F5F0E8', role: 'card background — warm cream', theme: 'light' },
  { name: '--warm', value: '#EDE7DC', role: 'hover/elevated — warm sand', theme: 'light' },
  { name: '--gold', value: '#B8860B', role: 'primary accent — dark goldenrod', theme: 'light' },
  { name: '--gold-h', value: '#D4A017', role: 'hover accent — brighter gold', theme: 'light' },
  { name: '--ink', value: '#14110D', role: 'primary text — warm near-black', theme: 'light' },
  { name: '--void', value: '#050810', role: 'page background — deep void', theme: 'dark' },
  { name: '--mid', value: '#111827', role: 'card background — dark blue-gray', theme: 'dark' },
  { name: '--gold', value: '#D4A017', role: 'primary accent — brighter gold', theme: 'dark' },
  { name: '--t1', value: '#F5E6C8', role: 'primary text — warm ivory', theme: 'dark' },
  { name: '--success', value: '#2D7A2D', role: 'production ROI, positive results', theme: 'functional' },
  { name: '--energy', value: '#E65C00', role: 'urgency, attention, executive', theme: 'functional' },
  { name: '--loss', value: '#C62828', role: 'waste, pilot trap, negative', theme: 'functional' },
  { name: '--trust', value: '#1A5276', role: 'trust signals, used sparingly', theme: 'functional' },
];

export const TYPE_TOKENS: [string, string][] = [
  ['Display', 'Cormorant Garamond 300 · clamp(2.5rem,7vw,5.5rem) · -0.03em'],
  ['Body / UI', 'Hanken Grotesk 300–500 · 0.9375rem · 1.47'],
  ['Data', 'JetBrains Mono 400–600 · uppercase · 0.1em–0.4em'],
  ['Radii', '12px standard · 16px large · 999px pills (max 16px)'],
  ['Shadows', 'sh-sm / sh-md / sh-lg / sh-gold (hover only)'],
];

export const ANTI_PATTERNS = [
  'Pure #000 or #FFF anywhere',
  'Blue primary (RIG is gold)',
  'Purple gradients',
  'Radius > 16px',
  'Emoji as UI elements',
  'Lorem ipsum / placeholder text',
  'Pixels not multiples of 4',
];
