# Antara Android Design System

Calm, gentle, welcoming, non-clinical. A private space for reflection, not a productivity dashboard.
Home (`activity_main.xml`) and Reflection (`activity_chat.xml`) are the reference screens.

## Foundations

| Token | Light | Use |
|---|---|---|
| `@color/background` | `#F6F5EF` | Warm off-white screen background |
| `@color/surface` | `#FFFFFF` | Cards, inputs on focus, bot bubbles |
| `@color/panel_sage` | `#E6ECDF` | Soft sage panels (reminders, highlighted question) |
| `@color/panel_warm` | `#EFEBE1` | Occasional warm panel (one per screen at most) |
| `@color/primary` | `#567A5F` | Muted green primary actions, today markers |
| `@color/primary_soft` | `#E4EBDF` | Selected chips, circle motifs |
| `@color/text_primary` | `#1F3A2B` | Dark forest-green headings and body |
| `@color/text_secondary` | `#66776B` | Gray-green supporting text |
| `@color/text_muted` | `#93A096` | Captions, hints |
| `@color/label` | `#5E7062` | Small uppercase labels |
| `@color/border` | `#E5E7DE` | Subtle 1dp borders |
| `@color/sos_soft` / `sos_text` | | Support pill only. Never alarming red. |
| `@color/crisis_*` | | Crisis message card only |

Dark mode equivalents live in `values-night/colors.xml`. Never hard-code hex colors in layouts or Java.

**Typography:** Nunito (bundled in `res/font`). The theme sets `@font/nunito` app-wide.

| Style | Size / weight | Use |
|---|---|---|
| `Antara.Text.Display` | 26sp ExtraBold | One screen heading |
| `Antara.Text.Title` | 20sp Bold | Card / section heading |
| `Antara.Text.Subtitle` | 16sp Bold | Small heading, list row title |
| `Antara.Text.Body` | 15sp Regular, secondary | Supporting text |
| `Antara.Text.BodyStrong` | 15sp Regular, primary | Readable body in primary ink |
| `Antara.Text.Small` | 13sp | Secondary detail |
| `Antara.Text.Caption` | 12sp muted | Footnotes, reassurance lines |
| `Antara.Text.Label` | 12sp ExtraBold caps | Small uppercase label. Sparingly: max one per section |
| `Antara.Text.FieldLabel` | 14sp SemiBold | Form field labels |
| `Antara.Text.Accent` | 13sp Bold primary | Quiet inline accent / link |

**Spacing:** side margins `@dimen/screen_margin` (20dp). `@dimen/space_section` (24dp) between major sections, `@dimen/space_group` (12dp) within related groups, `@dimen/card_padding` (20dp) inside cards.

**Corners:** cards 20dp (`radius_card`), inputs and primary buttons 12dp (`radius_input`), secondary actions are pills (`radius_pill`).

**Elevation:** none. Cards use a 1dp `@color/border` stroke instead of shadows. Do not use `CardView` elevation.

## Components

| Component | How |
|---|---|
| White card | `<LinearLayout style="@style/Antara.Card">` |
| Sage panel | `style="@style/Antara.Panel.Sage"` |
| Warm panel | `style="@style/Antara.Panel.Warm"` |
| Primary button | `<Button style="@style/Antara.Button.Primary">` (full width, 52dp, 12dp corners) |
| Secondary button | `Antara.Button.Secondary` (full width outline) or `Antara.Button.Pill` (compact pill) |
| Soft pill | `Antara.Button.Pill.Soft` |
| Support / SOS pill | `Antara.Button.Pill.Support` |
| Text button | `Antara.Button.Text` |
| Quick-reply / option chip | `TextView style="@style/Antara.Chip"`; selected state uses `@drawable/bg_option_selected` |
| Text input | `<EditText style="@style/Antara.Input">` |
| Dropdown | `<Spinner style="@style/Antara.Spinner">` with `R.layout.item_spinner_selected` / `item_spinner_dropdown` |
| Switch | `<com.google.android.material.switchmaterial.SwitchMaterial style="@style/Antara.Switch">` |
| Progress | `<ProgressBar style="@style/Antara.Progress">` |
| Back button | `<ImageButton style="@style/Antara.IconButton" android:src="@drawable/ic_arrow_back" android:contentDescription="@string/cd_back">` |
| Divider | `<View style="@style/Antara.Divider">` |
| Emotion tag | `TextView` with `@drawable/bg_emotion_bubble`, 12sp SemiBold `primary_dark` |
| Dialogs | `androidx.appcompat.app.AlertDialog.Builder` (themed automatically) |

**Motifs:** `motif_breath` (concentric breathing circle), `motif_ring` (small ring in sage circle), `motif_ring_filled`, `bg_circle_soft`. Prefer these over icons. No emojis anywhere, no bright gradients, no heavy shadows.

## Screen scaffold

```xml
<ScrollView style="@style/Antara.Screen.Scroll" android:background="@color/background">
  <LinearLayout android:orientation="vertical" ...>
    <!-- Top bar: back button + optional label, 24dp below -->
    <!-- Label (optional) + Display heading + Body intro -->
    <!-- Sections separated by 24dp; items inside a group 12dp apart -->
    <!-- Caption footer with a reassuring line -->
  </LinearLayout>
</ScrollView>
```

## Writing

Reassuring, concise, nonjudgmental. Sentence case for headings and buttons ("Begin my reflection").
Avoid pressure ("don't break your streak"), heavy gamification, exclamation-heavy copy, and unsupported
health or privacy claims (no "100% secure", "clinically proven", percentages from studies).
What we can truthfully say: reflections are stored on this device in a local database; Antara is not a
substitute for professional care; helplines listed are external services.

## Working vs placeholder

Only present controls as working when they are wired up. If something is decorative or not yet built,
make it visually quiet and label it honestly (for example "Coming later"). The breathing motif is decorative.
