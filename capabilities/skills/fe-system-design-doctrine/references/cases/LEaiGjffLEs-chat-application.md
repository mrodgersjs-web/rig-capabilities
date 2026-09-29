# Case: [Front-End System Design] - Chat application

Source: https://www.youtube.com/watch?v=LEaiGjffLEs (video id LEaiGjffLEs). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video LEaiGjffLEs against the local transcript.

- published 2020-12-17 / duration 2684s (~45 min) / problem type: product-design (front-end system design of a chat application)

## Author's framework as used
1. Lay out the overall plan first: general requirements, then functional requirements, then component architecture and hierarchy, then API and data protocol, then data entities and client-side storage, then performance, then accessibility. CLAIM(LEaiGjffLEs@00:27)
2. Collect general requirements (what the user can do at all) before scoping anything technical. CLAIM(LEaiGjffLEs@01:14)
3. Translate each functional requirement into a measurable target (e.g. a latency number that still feels "instant"). CLAIM(LEaiGjffLEs@02:23)
4. Sketch the UI prototype first (contact, contact list, chat window, attachments, message actions), then derive the full component hierarchy from it. CLAIM(LEaiGjffLEs@03:27)
5. Compare candidate data protocols in a written pros/cons table (long polling vs WebSockets vs SSE) before choosing. CLAIM(LEaiGjffLEs@07:25)
6. Decide the protocol by matching each option against the stated requirements, then combine two transports if one alone is one-way. CLAIM(LEaiGjffLEs@18:18)
7. Design the API surface and the data entities next, then the client store shape and the fetch/subscribe flow. CLAIM(LEaiGjffLEs@21:31)
8. Split performance work into three buckets, network, rendering, JavaScript, and work the simplest win in each first. CLAIM(LEaiGjffLEs@28:30)
9. Close with accessibility, even if the interviewer only probes one area. CLAIM(LEaiGjffLEs@41:24)

## Worked design
- Requirements: send/receive messages; attach media (video, audio, image, location, contact file); view a contact list; share messages, CLAIM(LEaiGjffLEs@01:14). Functional bar: near-instant delivery (~40-60 ms), usable on weak networks, frugal with device resources and battery, works across a wide device range, CLAIM(LEaiGjffLEs@02:23).
- Components: root Chat App containing ContactList (search box + list of Contact cards with avatar/name) and ChatView (message list, message with attachments, message actions, attachment dropdown, text input), CLAIM(LEaiGjffLEs@05:45).
- Data model: Contact {id, name}; Message {id, content, attachments[], userId, recipientId}; Attachment {id, messageId, source, type, content(URL)}, CLAIM(LEaiGjffLEs@23:09).
- API: subscribe to message updates, get contacts, attach media (userId + messageId + binary), send message, each with explicit parameters, CLAIM(LEaiGjffLEs@21:31).
- Client store: contacts normalized by id; flat map of contact id to message array and contact id to attachment array; chat view reads the list from the store and passes attachments down per message, CLAIM(LEaiGjffLEs@26:30).
- Realtime: SSE stream for incoming messages plus plain HTTP POST for outgoing, chosen over polling and WebSockets, CLAIM(LEaiGjffLEs@20:38).
- Perf: compression, Brotli-class formats, HTTP/2 multiplexing, code splitting, WebP/PNG, critical-resource inlining, deferred analytics, skeleton screens, node recycling in the message list, service-worker caching for offline history, CLAIM(LEaiGjffLEs@28:56).
- A11y: rem-based sizing, keyboard shortcuts, color-blind-friendly themes, live-region announcements, semantic markup and correct image dimensions, CLAIM(LEaiGjffLEs@41:44).

## Trade-offs he names
- Long polling vs WebSockets vs SSE: polling is simple and HTTP-native but wasteful and slow on mobile cell handoffs; WebSockets are duplex and lowest-latency but expensive per connection, HTTP/2-incompatible, hard to load balance, and firewall-fragile; SSE keeps HTTP/2 benefits, minimal payloads, cheap resources, easy failover, but is one-way with a quirky text-only API -> pick SSE for the receive path. CLAIM(LEaiGjffLEs@18:18)
- Sending messages: over the SSE channel is impossible (one-way) -> send via a simple HTTP request, accepting some per-request overhead because a user receives far more messages than they send. CLAIM(LEaiGjffLEs@20:04)
- Single bundle vs code splitting: bundling everything into one file fights HTTP/2 multiplexing -> split into cacheable chunks (e.g. vendor code separate from chat code). CLAIM(LEaiGjffLEs@29:30)
- SSR vs CSR for chat: extra server rendering infrastructure is not worth it -> stay client-rendered. CLAIM(LEaiGjffLEs@38:50)
- Web Workers: worth naming in a perf discussion but not needed here since chat has no heavy client computation. CLAIM(LEaiGjffLEs@39:25)
- One-size images vs device-aware image service: pass the image URL through a resizing service so phones get smaller assets, then cache at the CDN. CLAIM(LEaiGjffLEs@33:14)

## Anti-patterns he warns about
- Polling with full HTTP requests every interval: resends headers and tokens and wastes the user's data budget. CLAIM(LEaiGjffLEs@10:22)
- Keeping a persistent socket per tab: connection cost multiplies and drains battery. CLAIM(LEaiGjffLEs@11:35)
- Choosing WebSockets and then reimplementing HTTP/2 features (multiplexing, asset splitting) by hand. CLAIM(LEaiGjffLEs@13:30)
- Ignoring proxy servers and connection timeouts, which force constant reconnects. CLAIM(LEaiGjffLEs@09:41)
- Long CSS selectors and JS-triggered reflows: both degrade rendering performance. CLAIM(LEaiGjffLEs@35:43)
- Inserting or moving message DOM nodes instead of recycling a fixed node set. CLAIM(LEaiGjffLEs@37:34)
- Fixed pixel sizing that ignores user zoom preferences. CLAIM(LEaiGjffLEs@41:44)

## Dated / contestable
- The "40-60 ms is instant" latency figure is his chosen budget, not a measured standard; modern chat stacks often aim lower for delivery but the perceptual claim is still reasonable. CLAIM(LEaiGjffLEs@02:23)
- The 2020 framing "WebSockets are incompatible with HTTP/2" is contested: HTTP/2 still carries WebSocket connections via extended CONNECT in later stacks, though the load-balancing and proxy costs he names remain real. CLAIM(LEaiGjffLEs@12:21)
- Brotli is referred to by a garbled name ("Broadly") in the transcript; the 10-20% gain claim is directionally right but format-dependent. CLAIM(LEaiGjffLEs@29:17)
- SSE-as-primary plus POST for sends remains valid, but GraphQL subscriptions and managed realtime services were already common alternatives by 2020 and are not discussed.
