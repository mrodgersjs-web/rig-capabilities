# Great example - web-imagery-3d

The configurator hero for a fictional hardware client "Halcyon Audio", a single WebGL
scene showing the product shell in three finishes.

What makes it excellent:

1. It earns its cost with a written reason. The page states why a still cannot do the job:
   the buyer is choosing between three anodised finishes and the whole purchase decision
   turns on how light moves across the surface. A PNG of one finish cannot carry that, and
   the alternative quoted was a three-video shoot per finish.

2. The fallback ladder is implemented and tested, not described. A 2400x1600 WebP poster
   of the scene paints first and is the real first paint. The renderer initialises on
   intersection, over the poster, and never blocks it. On prefers-reduced-motion, on
   navigator.deviceMemory below 4, on hardwareConcurrency at or below 2, and on any WebGL
   context-creation failure, the renderer is never constructed and the poster stays.

3. The payload is built for the network it ships on. One .glb at 412KB with Draco mesh
   compression and KTX2 textures at 1024px, 78k triangles, versus a quoted 4.1MB for the
   uncompressed export. Whole-page imagery weight is 1.1MB against a 2MB budget.

4. It holds a frame floor and degrades when it cannot. 60fps on a mid-tier laptop, 30fps
   on a mid-tier phone, measured before sign-off. Below the floor the scene rotates once
   and settles on the poster rather than continuing to burn GPU for no information.

5. Motion changes information. The rotation exists to reveal the finish, it stops at a
   three-quarter view, and it does not loop.

The result to beat: a visitor with JavaScript disabled sees a complete, convincing hero,
and a visitor on a phone with reduced-motion set never downloads the model at all.
