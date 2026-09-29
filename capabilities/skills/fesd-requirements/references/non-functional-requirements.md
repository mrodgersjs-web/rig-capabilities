# Non-functional requirements: guarantees with numbers

Purpose: turn performance, coverage, accessibility and scale adjectives into requirements the
design can be checked against.

When to load: after the general/functional block is written, and whenever a phrase like "fast",
"real-time", "works everywhere", or "accessible" appears in a draft.

## Step checklist

1. State requirements at two levels: what the user can do, and what the system must guarantee
   (latency, bandwidth, device range). CLAIM(LEaiGjffLEs@01:14)
2. Pin each adjective to a number: "real-time feel" becomes a latency budget (he uses roughly
   40-60 ms). CLAIM(LEaiGjffLEs@02:23)
3. Declare browser coverage as a percentage with named exclusions.
   CLAIM(3MADCVqL534@06:54)
4. Declare device breadth explicitly: adaptive design spanning tablets and phones, or the
   product's real device list (Smart TV, tablets, phones, desktops).
   CLAIM(3MADCVqL534@07:05) CLAIM(Tu-hZ6lqNtY@05:35)
5. Add offline or reduced-network behavior as a requirement, not an optimization.
   CLAIM(3MADCVqL534@07:39) CLAIM(leo1FZ6vu1I@03:38)
6. Write the bandwidth and battery constraints into the requirements where users are on phones.
   CLAIM(LEaiGjffLEs@02:29)
7. Add adaptive media quality requirements (video quality down to the lowest bandwidth, promo
   and hover-preview media tuned to viewport and connection).
   CLAIM(Tu-hZ6lqNtY@06:14) CLAIM(Tu-hZ6lqNtY@07:14)
8. Define rendering stability explicitly (downscaled chart shown before new data arrives).
   CLAIM(HR2jXy_wPg4@04:56)
9. Name accessibility as a requirement: disability access, screen readers, and the styling API.
   CLAIM(5vyKhm2NTfw@05:20) CLAIM(u6jhTo13_No@06:41)
10. State the scale plainly (thousands of rows) and the device floor (old phones and desktops).
    CLAIM(u6jhTo13_No@05:36) CLAIM(u6jhTo13_No@06:07)
11. Prioritize the non-functional list for the product: desktop-first apps can lower performance
    and network priority while still naming them. CLAIM(tsGarhpWOws@06:05)

## Decision table

| Adjective found | Replace with | Cite |
|---|---|---|
| "real-time" | latency budget in ms | CLAIM(LEaiGjffLEs@02:23) |
| "most browsers" | percentage plus named exclusions | CLAIM(3MADCVqL534@06:54) |
| "responsive" | explicit device list with the adaptive requirement | CLAIM(3MADCVqL534@07:05) CLAIM(Tu-hZ6lqNtY@05:35) |
| "works offline" | PWA or cached-mode requirement for loaded content | CLAIM(3MADCVqL534@07:39) |
| "fast on mobile" | bandwidth and battery constraints named | CLAIM(LEaiGjffLEs@02:29) |
| "scales" | row count or dataset size stated | CLAIM(u6jhTo13_No@05:36) |
| "accessible" | screen-reader requirement plus device/disability access line | CLAIM(u6jhTo13_No@06:41) CLAIM(5vyKhm2NTfw@05:20) |

## Laws for this sub-topic

- Declare browser coverage as a percentage with named exclusions (for example 95% minus IE11)
  instead of vague "most browsers". CLAIM(3MADCVqL534@06:54) single-source.
- Declare device breadth as an adaptive-design requirement spanning tablets and phones.
  CLAIM(3MADCVqL534@07:05) consensus.
- Add offline/reduced-network behavior as a functional requirement (PWA mode for already-loaded
  pins, usable on slow connections). CLAIM(3MADCVqL534@07:39) consensus.
- Cover device breadth and disability access explicitly as specific requirements, then move on.
  CLAIM(5vyKhm2NTfw@05:20) consensus.
- State requirements at two levels: what the user can do, and what the system must guarantee
  (latency, bandwidth, device range). CLAIM(LEaiGjffLEs@01:14) consensus.
- Pin "real-time feel" to a concrete latency budget (he uses roughly 40-60 ms) instead of leaving
  it as an adjective. CLAIM(LEaiGjffLEs@02:23) single-source.
- Design for low-bandwidth mobile networks and battery limits, because chat users are mostly on
  phones. CLAIM(LEaiGjffLEs@02:29) consensus.
- Define rendering stability explicitly: when the user switches time frames, show a downscaled
  chart before the new data arrives. CLAIM(HR2jXy_wPg4@04:56) single-source.
- State device breadth explicitly (Smart TV, tablets, phones, desktops) as a functional
  requirement. CLAIM(Tu-hZ6lqNtY@05:35) consensus.
- Require adaptive video quality so even the lowest bandwidth yields a watchable stream.
  CLAIM(Tu-hZ6lqNtY@06:14) single-source.
- Require promo and hover-preview media to be optimized to both viewport and connection quality.
  CLAIM(Tu-hZ6lqNtY@07:14) single-source.
- Treat mobile-first, offline usage and battery cost as requirements, not optimizations.
  CLAIM(leo1FZ6vu1I@03:38) consensus.
- Lower the performance and network priority for desktop-first apps while still naming CPU and
  network performance as requirements. CLAIM(tsGarhpWOws@06:05) single-source.
- State the scale requirement plainly: tables deal in thousands of rows and must handle large
  datasets well. CLAIM(u6jhTo13_No@05:36) single-source.
- Require performance and a wide device range, down to old phones and desktops.
  CLAIM(u6jhTo13_No@06:07) single-source.
- Require screen-reader accessibility and a CSS API for table styling as functional
  requirements. CLAIM(u6jhTo13_No@06:41) consensus.

## Worked cases

- LEaiGjffLEs "[Front-End System Design] - Chat application": the latency-budget discipline.
- Tu-hZ6lqNtY "[Front-End Product Design] - Netflix": device breadth and adaptive media.
- 3MADCVqL534 "[Front-End System Design] - Pinterest": coverage percentage and offline behavior.
- u6jhTo13_No "[Front-End System Design] - Data Table Component": scale, device floor, screen
  readers.
- leo1FZ6vu1I "[Front-End System Design] - Google Calendar": mobile-first, offline, battery as
  requirements.

## Dated / contestable

- The coverage example excludes IE11, which is end-of-support since 2022. Distiller note (not
  the author): keep the pattern, change the named exclusion. CLAIM(3MADCVqL534@06:54)
- The 40-60 ms figure is a 2020 chat-app target, not a universal standard. Distiller note (not
  the author): derive the number per product from its own feel tests. CLAIM(LEaiGjffLEs@02:23)
