---
name: Academic Career Nexus
colors:
  surface: '#f6faff'
  surface-dim: '#d2dbe4'
  surface-bright: '#f6faff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#ebf5fe'
  surface-container: '#e6eff8'
  surface-container-high: '#e0e9f3'
  surface-container-highest: '#dae4ed'
  on-surface: '#141d23'
  on-surface-variant: '#414848'
  inverse-surface: '#283139'
  inverse-on-surface: '#e9f2fb'
  outline: '#717978'
  outline-variant: '#c1c8c7'
  surface-tint: '#426464'
  primary: '#416463'
  on-primary: '#ffffff'
  primary-container: '#5a7d7c'
  on-primary-container: '#ffffff'
  inverse-primary: '#a9cecc'
  secondary: '#436371'
  on-secondary: '#ffffff'
  secondary-container: '#c3e5f5'
  on-secondary-container: '#476775'
  tertiary: '#585d71'
  on-tertiary: '#ffffff'
  tertiary-container: '#70768b'
  on-tertiary-container: '#ffffff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c4eae8'
  primary-fixed-dim: '#a9cecc'
  on-primary-fixed: '#00201f'
  on-primary-fixed-variant: '#2a4c4c'
  secondary-fixed: '#c6e8f8'
  secondary-fixed-dim: '#aaccdc'
  on-secondary-fixed: '#001f29'
  on-secondary-fixed-variant: '#2b4b58'
  tertiary-fixed: '#dde2fa'
  tertiary-fixed-dim: '#c0c6dd'
  on-tertiary-fixed: '#151b2c'
  on-tertiary-fixed-variant: '#404659'
  background: '#f6faff'
  on-background: '#141d23'
  surface-variant: '#dae4ed'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  display-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.005em
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: 0em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system is crafted for high-performing students, emerging graduates, academic advisors, and institutional recruiters navigating career launches and internships. The aesthetic bridges scholastic credibility with modern product polish, combining clean editorial structure, clear visual hierarchy, and an encouraging, calm atmosphere.

The design movement is **Modern Scholastic Minimalism** accented with soft architectural tones. It avoids bureaucratic rigidity and playful campus tropes, favoring structured layouts, generous whitespace, sharp contrasts, and delicate periwinkle/slate accents. The emotional tone projects capability, calm competence, and focus, reducing career-search anxiety while presenting student achievements in an authoritative, hiring-ready light.

## Colors

The palette balances earthy sage-teal authority with tranquil periwinkle and crisp canvas neutrals to support dense resume content without visual fatigue.

- **Primary (`#5A7D7C`)**: Muted Teal / Sage. Anchors the primary actions, major progress trackers, verified credential indicators, and prominent callouts.
- **Secondary (`#A0C1D1`)**: Slate Blue. Serves as interactive border highlights, secondary action items, hover state boundaries, and subtle chart indicators.
- **Tertiary (`#DADFF7`)**: Soft Periwinkle / Lavender Ice. Drives tag backgrounds, chip highlights, active sidebar states, and selected resume section indicators.
- **Neutral (`#232C33`)**: Dark Gunmetal Charcoal. Provides high-contrast typography, structural icons, and deep contrast elements for readability.
- **Dividers & Subtle Borders (`#B5B2C2`)**: Lavender Gray. Governs hairline table dividers, inactive panel borders, and structural container outlines.
- **Surfaces**: Canvas default sits at `#F6F7FB`, providing a softer reading environment than pure white, while active work surfaces and cards elevate to pure `#FFFFFF`.

## Typography

Typography relies entirely on **Plus Jakarta Sans**, chosen for its crisp geometry, open counters, and high legible contrast across resume templates, multi-column metrics, and form fields.

- **Display & Headlines**: Bold, tracking-tightened letterforms create an authoritative posture for student headers, section titles, and portal dashboard greetings.
- **Body Text**: Tuned for maximum scanning speed. Work history bullets, advisor notes, and job specifications maintain a comfortable 1.5–1.6 line-height ratio in `#232C33`.
- **Labels & Microcopy**: Medium and small labels employ slight letter-spacing expansions to optimize metadata tags, graduation dates, GPA markers, and application statuses.
- **High-Density Data**: Tabular information and skill lists rely on `body-md` and `label-sm` to maintain strict visual parity between candidate profiles and standard recruiter viewports.

## Layout & Spacing

The layout philosophy uses a **12-column responsive fluid grid** with a maximum content boundary of `1280px` for portal overview dashboards and a focused `960px` canvas for the live resume editor and previewer.

- **Desktop (1024px+)**: 12 columns, 24px (`1.5rem`) gutters, 32px (`2rem`) page margin. Two- or three-pane workflows (e.g., navigation sidebar + editor canvas + real-time preview panel).
- **Tablet (768px – 1023px)**: 8 columns, 20px gutters, 24px page margins. Panels stack or transition into slide-over drawers; resume preview switches to a toggle view.
- **Mobile (< 768px)**: 4 columns, 16px (`1rem`) gutters, 16px (`1rem`) outer margins. Single-column stacked cards with bottom-docked application actions.
- **Rhythm**: Component spacing strictly adheres to 4px/8px baselines. Cards and input fields use `space-md` or `space-lg` inner padding to maintain breathing room around information-dense resume sections.

## Elevation & Depth

Visual hierarchy leverages crisp structural borders combined with tinted ambient elevation to emulate high-end architectural stationery.

- **Tonal Layering**: Depth is created primarily through color separation: `#F6F7FB` (Base Canvas) sits beneath `#FFFFFF` (Card Panels and Document Sheets).
- **Outlines Over Heavy Shadows**: Containers favor a clean 1px border using `#B5B2C2` at 40–60% opacity for default states, transitioning to `#A0C1D1` on hover or keyboard focus.
- **Ambient Elevation Scale**:
  - *Level 0 (Flat)*: Embedded form inputs, static tables, and nested sub-sections. No shadow; framed by subtle `#B5B2C2` borders.
  - *Level 1 (Default Cards & Tiles)*: `0 2px 8px -2px rgba(35, 44, 51, 0.05), 0 1px 3px -1px rgba(35, 44, 51, 0.03)`. Used for resume modules, job listing summaries, and metric cards.
  - *Level 2 (Hover & Floating Elements)*: `0 8px 24px -4px rgba(35, 44, 51, 0.08), 0 4px 8px -2px rgba(35, 44, 51, 0.04)`. Used for hovered interactive cards, active resume paper previews, and sticky action toolbars.
  - *Level 3 (Modals & Popovers)*: `0 16px 36px -6px rgba(35, 44, 51, 0.12), 0 6px 12px -2px rgba(35, 44, 51, 0.06)`. Applied to full profile review dialogs, skill selection popovers, and recruiter message sheets.

## Shapes

The design system maintains strict geometric intentionality. Corner curvature varies deliberately by component scale to preserve structured clarity:

- **Large Structural Containers & Cards**: Set to `10px–12px` (`rounded-lg` / `rounded-xl`). This delivers a balanced modern card silhouette without feeling overly playful or toy-like.
- **Interactive Controls (Inputs, Buttons, Dropdowns)**: Standardized at `6px–8px` (`rounded` / `rounded-md`), grounding interactive tools with sharp, tactile efficiency.
- **Chips, Badges, & Tags**: Fully rounded pill shapes (`rounded-full` / `9999px`) to create clear differentiation between actionable buttons and passive categorical indicators.
- **Resume Document Preview Sheet**: Exact `10px` radius on outer canvas wrappers, reinforcing the metaphor of a crisp, bound sheet of academic paper.

## Components

### Buttons
- **Primary**: Background `#5A7D7C`, text `#FFFFFF`, border-radius `8px`, height `40px` (desktop) / `44px` (mobile). Hover state deepens to `#4A6766` with Level 1 shadow. Active state scales subtly (`0.98`).
- **Secondary**: Background transparent, border `1.5px solid #A0C1D1`, text `#232C33`, border-radius `8px`. Hover fills with `#DADFF7` at 25% opacity with text shifting to `#5A7D7C`.
- **Tertiary / Ghost**: Text `#5A7D7C`, background transparent, borderless. Hover triggers `#F6F7FB` fill.
- **Destructive**: Outline or soft tint in warning vermilion, reserving teal strictly for constructive actions.

### Chips & Badges
- **Skill / Major Chips**: Fill `#DADFF7` with text `#232C33`, radius `9999px`, padding `4px 12px`, typography `label-sm`. When interactive (e.g., removable skill), includes an `#5A7D7C` dismissal icon.
- **Status Badges**: Application statuses ("Interviewing", "Draft", "Reviewed") use 50% opacity periwinkle or muted teal fills with a solid 6px indicator dot and bold `label-sm` text.

### Input Fields & Selects
- Height `40px`, border-radius `6px`, background `#FFFFFF`, border `1px solid #B5B2C2`.
- Text typed in `#232C33` with placeholder copy in `#B5B2C2`.
- Focus state: Border shifts to `#A0C1D1` with a `0 0 0 3px rgba(160, 193, 209, 0.25)` focus ring; never use raw browser focus rings.

### Checkboxes & Radio Buttons
- Width and height `18px`, border `1.5px solid #B5B2C2`, radius `4px` (checkbox) or `50%` (radio).
- Checked state: Fill `#5A7D7C` with white checkmark glyph or center dot. Focus introduces slate-blue outer halo.

### Cards & Resume Blocks
- Surface pure `#FFFFFF`, radius `10px–12px`, border `1px solid rgba(181, 178, 194, 0.35)`, outer elevation Level 1.
- Internal card headers feature a bottom 1px divider in `#B5B2C2` (25% opacity) to separate section titles from bullet-point editors.
- Draggable / reorderable resume section cards show a vertical grab-handle on hover tinted with `#A0C1D1`.

### Specialized Domain Components
- **Resume Score / Completeness Gauge**: Radial meter or segmented linear progress bar in `#5A7D7C` against a `#DADFF7` track, complemented by `label-md` percentage indicators.
- **Recruiter Feedback Card**: Callout panel with a 3px solid left accent border in `#5A7D7C`, background `#F6F7FB`, nested within student work dashboards for actionable advisor critiques.
- **Document Paper Canvas**: A bordered, pure white 8.5x11 aspect ratio preview sheet anchored with a Level 2 ambient shadow against the `#F6F7FB` workspace.