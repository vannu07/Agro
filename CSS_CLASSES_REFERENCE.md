# Krishi Mitr - CSS Classes Reference Guide

Complete reference for all available CSS classes in your design system.

---

## 📚 Table of Contents

1. [Typography Classes](#typography-classes)
2. [Button Classes](#button-classes)
3. [Card Classes](#card-classes)
4. [Layout Classes](#layout-classes)
5. [Form Classes](#form-classes)
6. [Component Classes](#component-classes)
7. [Animation Classes](#animation-classes)
8. [Utility Classes](#utility-classes)
9. [Spacing Classes](#spacing-classes)

---

## Typography Classes

### Heading Classes
```html
<h1>Heading 1 - 3rem / 48px</h1>
<h2>Heading 2 - 2.25rem / 36px</h2>
<h3>Heading 3 - 1.875rem / 30px</h3>
<h4>Heading 4 - 1.5rem / 24px</h4>
<h5>Heading 5 - 1.25rem / 20px</h5>
<h6>Heading 6 - 1.125rem / 18px</h6>
```

### Text Classes
```html
<p>Normal paragraph text</p>
<p class="text-muted">Muted gray text</p>
<p class="text-center">Center aligned text</p>
<p class="text-success">Success green text</p>
<p class="text-error">Error red text</p>
```

### Font Weights
```html
<!-- Applied via CSS -->
font-weight: var(--font-weight-light);     /* 300 */
font-weight: var(--font-weight-normal);    /* 400 */
font-weight: var(--font-weight-medium);    /* 500 */
font-weight: var(--font-weight-semibold);  /* 600 */
font-weight: var(--font-weight-bold);      /* 700 */
```

---

## Button Classes

### Button Types
```html
<!-- Primary Button -->
<button class="btn btn-primary">Primary Button</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Secondary Button</button>

<!-- Accent Button -->
<button class="btn btn-accent">Accent Button</button>

<!-- Outline Button -->
<button class="btn btn-outline">Outline Button</button>
```

### Button Sizes
```html
<!-- Small Button -->
<button class="btn btn-primary btn-sm">Small Button</button>

<!-- Regular Button (default) -->
<button class="btn btn-primary">Regular Button</button>

<!-- Large Button -->
<button class="btn btn-primary btn-lg">Large Button</button>
```

### Button States
```html
<!-- Hover (automatic on hover) -->
<button class="btn btn-primary">Hover me</button>

<!-- Active -->
<button class="btn btn-primary active">Active Button</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled Button</button>

<!-- Loading -->
<button class="btn btn-primary" disabled>
  <span class="spinner"></span> Loading...
</button>
```

### Button with Icon
```html
<button class="btn btn-primary">
  <span>📊</span> Button with icon
</button>
```

---

## Card Classes

### Basic Card
```html
<div class="card">
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</div>
```

### Card Variants
```html
<!-- Standard Card -->
<div class="card">Content</div>

<!-- Glass Card (Frosted glass effect) -->
<div class="card card-glass">Content</div>

<!-- Gradient Card (Green gradient) -->
<div class="card card-gradient">Content</div>

<!-- Hover Card -->
<div class="card">
  Automatically lifts on hover with shadow
</div>
```

### Card Combinations
```html
<div class="card card-glass">
  <h3>Glassmorphism Card</h3>
  <p>Modern frosted glass effect</p>
</div>

<div class="card card-gradient">
  <h3 style="color: white;">Gradient Card</h3>
  <p style="color: white;">White text on gradient</p>
</div>
```

---

## Layout Classes

### Container
```html
<div class="container">
  <!-- Centered max-width 1200px container -->
  <!-- Responsive padding on mobile -->
</div>
```

### Sections
```html
<!-- Standard Section -->
<section class="section">
  <!-- padding-top: var(--space-4xl) -->
  <!-- padding-bottom: var(--space-4xl) -->
</section>

<!-- Small Section -->
<section class="section-small">
  <!-- Smaller padding: var(--space-2xl) -->
</section>
```

### Flexbox Utilities
```html
<!-- Flex Container -->
<div class="flex">Items arranged in flexbox</div>

<!-- Flex Center -->
<div class="flex-center">Perfectly centered content</div>

<!-- Gap Utilities -->
<div class="flex gap-sm">Items with small gap</div>
<div class="flex gap-md">Items with medium gap</div>
<div class="flex gap-lg">Items with large gap</div>
<div class="flex gap-xl">Items with extra large gap</div>
```

### Text Alignment
```html
<div class="text-center">Center aligned text</div>
<div class="text-left">Left aligned text</div>
<div class="text-right">Right aligned text</div>
```

---

## Form Classes

### Form Groups
```html
<div class="form-group">
  <label class="form-label">Input Label</label>
  <input type="text" class="form-control" placeholder="Enter text...">
</div>
```

### Input States
```html
<!-- Default -->
<input type="text" class="form-control">

<!-- Focus (automatic on focus) -->
<input type="text" class="form-control" placeholder="Click me">

<!-- Error -->
<input type="text" class="form-control error">
<div class="form-error">Error message goes here</div>

<!-- Success -->
<input type="text" class="form-control">
<div class="form-success">Success message goes here</div>

<!-- Disabled -->
<input type="text" class="form-control" disabled>
```

### Input Types
```html
<input type="text" class="form-control">
<input type="email" class="form-control">
<input type="password" class="form-control">
<textarea class="form-control" rows="4"></textarea>
<select class="form-control">
  <option>Option 1</option>
  <option>Option 2</option>
</select>
```

---

## Component Classes

### Navbar Component
```html
<nav class="navbar-elite">
  <!-- Automatically adds glassmorphism on scroll -->
</nav>

<!-- Scrolled state (applied automatically) -->
<nav class="navbar-elite scrolled">
  <!-- Glass background with blur effect -->
</nav>
```

### Hero Section
```html
<section class="hero-section">
  <div class="container">
    <div class="hero-content">
      <h1 class="hero-title">Title</h1>
      <p class="hero-subtitle">Subtitle</p>
      <div class="hero-buttons">
        <a href="#" class="btn btn-primary">Button 1</a>
        <a href="#" class="btn btn-outline">Button 2</a>
      </div>
    </div>
  </div>
</section>
```

### Feature Grid
```html
<div class="feature-grid">
  <div class="feature-card">
    <div class="feature-icon">🌾</div>
    <h3 class="feature-title">Feature 1</h3>
    <p class="feature-description">Description goes here</p>
  </div>
  <!-- Repeat for more cards -->
</div>
```

### Agent Cards
```html
<a href="#" class="agent-card">
  <div class="agent-icon">🌾</div>
  <h3 class="agent-name">Agent Name</h3>
  <p class="agent-description">Agent description (2-3 lines)</p>
</a>
```

### Result Cards
```html
<div class="result-card">
  <h2 class="result-title">Result Title</h2>
  <div class="result-value">Value/Score</div>
  
  <div class="result-details">
    <div class="detail-item">
      <div class="detail-label">Label</div>
      <div class="detail-value">Value</div>
    </div>
    <!-- Repeat for more details -->
  </div>
</div>
```

### Footer
```html
<footer>
  <div class="container">
    <div class="footer-content">
      <div class="footer-section">
        <h3>Section Title</h3>
        <a href="#" class="footer-link">Link</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>Copyright notice</p>
    </div>
  </div>
</footer>
```

### Badges
```html
<!-- Success Badge (Green) -->
<span class="badge badge-success">Success</span>

<!-- Warning Badge (Amber) -->
<span class="badge badge-warning">Warning</span>

<!-- Error Badge (Red) -->
<span class="badge badge-error">Error</span>
```

---

## Animation Classes

### Entrance Animations
```html
<!-- Fade In -->
<div class="animate-fade-in">Content</div>

<!-- Fade In Up -->
<div class="animate-fade-in-up">Content</div>

<!-- Fade In Down -->
<div class="animate-fade-in-down">Content</div>

<!-- Fade In Left -->
<div class="animate-fade-in-left">Content</div>

<!-- Fade In Right -->
<div class="animate-fade-in-right">Content</div>

<!-- Scale (Zoom) -->
<div class="animate-scale">Content</div>
```

### Exit Animations
```html
<!-- Slide Up -->
<div class="animate-slide-up">Content</div>

<!-- Slide Down -->
<div class="animate-slide-down">Content</div>

<!-- Slide In From Left -->
<div class="animate-slide-in-left">Content</div>

<!-- Slide In From Right -->
<div class="animate-slide-in-right">Content</div>
```

### Attention Animations
```html
<!-- Bounce -->
<div class="animate-bounce">Bouncing content</div>

<!-- Pulse -->
<div class="animate-pulse">Pulsing content</div>

<!-- Heartbeat -->
<div class="animate-heartbeat">Content</div>

<!-- Glow -->
<div class="animate-glow">Glowing content</div>

<!-- Float -->
<div class="animate-float">Floating content</div>

<!-- Wobble -->
<div class="animate-wobble">Wobbling content</div>

<!-- Shake -->
<div class="animate-shake">Shaking content</div>
```

### Stagger Animations (for lists)
```html
<!-- Each child animates with delay -->
<div class="animate-stagger">
  <div>Item 1 (delay 0s)</div>
  <div>Item 2 (delay 0.1s)</div>
  <div>Item 3 (delay 0.2s)</div>
  <div>Item 4 (delay 0.3s)</div>
  <div>Item 5 (delay 0.4s)</div>
  <div>Item 6 (delay 0.5s)</div>
</div>
```

### Loading Animations
```html
<!-- Spinner -->
<div class="spinner"></div>

<!-- Loading Bar -->
<div class="loading-bar"></div>

<!-- Pulse (breathing effect) -->
<div class="animate-pulse">Loading...</div>
```

### Special Effects
```html
<!-- Typing Animation -->
<p class="typing">This text types out...</p>

<!-- Ripple Effect on Click -->
<button class="btn btn-primary ripple">Click me</button>

<!-- Shimmer Effect -->
<div style="background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); animation: shimmer 2s infinite;"></div>
```

---

## Utility Classes

### Color Utilities
```html
<!-- Text Colors -->
<p class="text-muted">Muted gray text</p>
<p class="text-success">Success green text</p>
<p class="text-error">Error red text</p>

<!-- Background Colors -->
<!-- Applied with inline styles or custom CSS -->
<div style="background: var(--primary-emerald-light); padding: 1rem;">
  Light emerald background
</div>
```

### Text Utilities
```html
<p class="text-center">Centered text</p>
<p class="text-muted">Muted/gray text</p>
<p class="text-success">Success text</p>
<p class="text-error">Error text</p>

<!-- Text Balance (for better line breaks) -->
<h1 style="text-balance">Heading that breaks nicely</h1>
```

### Display Utilities
```html
<!-- Flexbox -->
<div class="flex">Flex container</div>
<div class="flex-center">Centered flex container</div>

<!-- Alignment -->
<div class="text-center">Center aligned</div>
<div class="text-left">Left aligned</div>
<div class="text-right">Right aligned</div>
```

---

## Spacing Classes

### Margin Top
```html
<div class="mt-xs">Extra small margin top</div>
<div class="mt-sm">Small margin top</div>
<div class="mt-md">Medium margin top</div>
<div class="mt-lg">Large margin top</div>
<div class="mt-xl">Extra large margin top</div>
```

### Margin Bottom
```html
<div class="mb-xs">Extra small margin bottom</div>
<div class="mb-sm">Small margin bottom</div>
<div class="mb-md">Medium margin bottom</div>
<div class="mb-lg">Large margin bottom</div>
<div class="mb-xl">Extra large margin bottom</div>
```

### Gap (for flex containers)
```html
<div class="flex gap-sm">Small gap between items</div>
<div class="flex gap-md">Medium gap between items</div>
<div class="flex gap-lg">Large gap between items</div>
<div class="flex gap-xl">Extra large gap between items</div>
```

### Spacing Scale Values
```
xs  = 0.25rem  (4px)
sm  = 0.5rem   (8px)
md  = 1rem     (16px)
lg  = 1.5rem   (24px)
xl  = 2rem     (32px)
2xl = 2.5rem   (40px)
3xl = 3rem     (48px)
4xl = 4rem     (64px)
5xl = 5rem     (80px)
```

---

## CSS Variables Reference

### Colors
```css
--primary-emerald: #10B981
--primary-emerald-light: #A7F3D0
--primary-emerald-dark: #047857

--accent-amber: #FBBF24
--accent-amber-light: #FEF3C7
--accent-amber-dark: #D97706

--neutral-white: #FFFFFF
--neutral-cream: #FAFAF9
--neutral-light-gray: #F3F4F6
--neutral-gray: #6B7280
--neutral-dark-gray: #374151
--neutral-charcoal: #1F2937
--neutral-black: #111827

--color-success: #10B981
--color-warning: #FBBF24
--color-error: #EF4444
--color-info: #3B82F6
```

### Typography
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
--font-display: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

--text-xs: 0.75rem
--text-sm: 0.875rem
--text-base: 1rem
--text-lg: 1.125rem
--text-xl: 1.25rem
--text-2xl: 1.5rem
--text-3xl: 1.875rem
--text-4xl: 2.25rem
--text-5xl: 3rem

--font-weight-light: 300
--font-weight-normal: 400
--font-weight-medium: 500
--font-weight-semibold: 600
--font-weight-bold: 700

--line-height-tight: 1.2
--line-height-normal: 1.5
--line-height-relaxed: 1.75
```

### Spacing
```css
--space-xs: 0.25rem
--space-sm: 0.5rem
--space-md: 1rem
--space-lg: 1.5rem
--space-xl: 2rem
--space-2xl: 2.5rem
--space-3xl: 3rem
--space-4xl: 4rem
--space-5xl: 5rem
```

### Border Radius
```css
--radius-sm: 0.375rem
--radius-md: 0.5rem
--radius-lg: 0.75rem
--radius-xl: 1rem
--radius-2xl: 1.5rem
--radius-full: 9999px
```

### Effects
```css
--glass-bg: rgba(255, 255, 255, 0.8)
--glass-blur: blur(12px)
--glass-border: rgba(255, 255, 255, 0.2)
--glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.1)

--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1)
--shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.15)

--gradient-emerald: linear-gradient(135deg, #10B981 0%, #059669 100%)
--gradient-amber: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)
```

### Transitions
```css
--trans-base: 300ms ease
--trans-smooth: 300ms cubic-bezier(0.4, 0, 0.2, 1)
--trans-bounce: 300ms cubic-bezier(0.34, 1.56, 0.64, 1)
```

---

## Common Class Combinations

### Success Card with Animation
```html
<div class="card animate-fade-in-up">
  <div class="badge badge-success">Success</div>
  <h3>Completed</h3>
  <p>Operation was successful</p>
</div>
```

### Feature Grid with Stagger
```html
<div class="feature-grid animate-stagger">
  <div class="feature-card">...</div>
  <div class="feature-card">...</div>
  <div class="feature-card">...</div>
</div>
```

### Button with Loading State
```html
<button class="btn btn-primary">
  <span class="spinner"></span>
  Loading...
</button>
```

### Glassmorphic Container
```html
<div class="card card-glass animate-fade-in">
  <h3>Modern Glass Effect</h3>
  <p>Content with frosted glass background</p>
</div>
```

### Animated Result Display
```html
<div class="result-card animate-fade-in-up">
  <h2 class="result-title">Your Result</h2>
  <div class="result-value">92%</div>
  <div class="result-details">
    <!-- Detail items -->
  </div>
</div>
```

---

## Quick Reference

| Class | Purpose | Example |
|-------|---------|---------|
| `.btn` | Button base | `<button class="btn">` |
| `.btn-primary` | Primary action | `<button class="btn btn-primary">` |
| `.card` | Card container | `<div class="card">` |
| `.card-glass` | Glass effect | `<div class="card card-glass">` |
| `.animate-fade-in-up` | Fade and slide up | `<div class="animate-fade-in-up">` |
| `.feature-grid` | Feature layout | `<div class="feature-grid">` |
| `.hero-section` | Hero container | `<section class="hero-section">` |
| `.form-group` | Form field | `<div class="form-group">` |
| `.badge` | Small label | `<span class="badge">` |
| `.section` | Content section | `<section class="section">` |

---

## Tips for Using Classes

1. **Always use semantic HTML** - Use `<button>` not `<div>` for buttons
2. **Combine classes** - Stack multiple classes: `btn btn-primary btn-lg`
3. **Use CSS variables** - Reference variables for consistency
4. **Stack animations** - Combine entrance animations with stagger for lists
5. **Respect hierarchy** - Use proper heading levels (h1-h6)
6. **Test responsiveness** - Check on mobile, tablet, and desktop
7. **Use flexbox utilities** - For layout and alignment
8. **Apply animations on load** - Use Intersection Observer for scroll effects

---

This reference covers all available CSS classes in your design system. For more information, see FRONTEND_GUIDE.md and FRONTEND_SHOWCASE.md!
