# Agent SkillGuard design contract

Status: public-package visual authority

## Product idea

Agent SkillGuard is a quiet checkpoint, not a police badge. The visual system should feel exact, local, and calm: an electric-cyan scan signal passing through a deep-navy and signal-blue inspection frame that survives both light and dark repository surfaces.

## Mark

The primary mark is an open technical hexagonal frame with an inward-facing bracket pair. A single electric-cyan scan line crosses the center and terminates in a small verified dot. The deep-navy frame and signal-blue brackets remain legible at 16, 24, and 32 pixels on light and dark backgrounds. It does not rely on text, gradients, shadows, locks, padlocks, robots, mascots, weapons, or cybersecurity clichés.

## Tokens

- Deep navy: `#06235D`
- Signal blue: `#0183E0`
- Electric cyan: `#09CEFC`
- Cloud white: `#F8FAFC`
- Slate: `#64748B`
- Warning: `#F5B942`
- Critical: `#F06464`
- Primary type: Inter, ui-sans-serif, system-ui, sans-serif
- Mono type: IBM Plex Mono, ui-monospace, monospace
- Corner radius: 14px cards, 10px controls
- Border: 1px solid with no glow

## Plugin page composition

- Icon: centered mark with at least 14% clear space.
- Logo: mark only; no text inside the raster asset.
- Screenshot: left column shows one command and the `review_required` result; right column shows four compact findings with severity and uncertainty. No terminal chrome that implies a real external system.
- Social preview: mark at left; text “Scan before you install.” at right; one small JSON finding card.

## Accessibility

State is never color-only. Severity includes text or a symbol. Minimum body contrast is 4.5:1. The mark keeps a clear monochrome silhouette. Motion is not required.

## Asset authority

- Canonical source: `plugins/agent-skillguard/assets/Agent SkillGuard Transparent Master 220826.png`.
- Route and immutable hash: `plugins/agent-skillguard/assets/Logo Generation Manifest 140826.json`.
- Public-safe source custody: `plugins/agent-skillguard/assets/Agent SkillGuard Agent Smith Palette Source Receipt 210826.md`.
- Delivery PNGs are deterministic resize or layout derivatives that place the source without local geometry creation. The master, icon, and logo derivatives retain genuine alpha; screenshot and social-preview derivatives use their documented product-surface backgrounds.
- The candidate carries no production SVG reconstruction.

## Do

- Use flat geometry, generous negative space, a deep-navy/signal-blue inspection frame, and one electric-cyan scan signal.
- Show paths, line numbers, fingerprints, and uncertainty in product screenshots.
- Keep the product calm and review-oriented.

## Do not

- Claim safety certification, malware detection, or malicious intent.
- Use skulls, sirens, glossy shields, neon grids, or hacker imagery.
- Place secret-looking strings in public-facing mockups.
