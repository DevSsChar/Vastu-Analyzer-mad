# VastuWise AI - Complete UI Design Specifications

## 🎨 Global Design System

### Color Palette
```
Primary Colors:
- Primary: #db7706 (Warm Orange)
- Primary Dark: #b45309 (Deep Orange)
- Primary Light: #f59e0b (Bright Amber)

Background Colors:
- Background Light: #fffaf5 (Cream White)
- Background Dark: #231a0f (Dark Brown)

Surface Colors:
- Surface Light: #ffffff (Pure White)
- Surface Dark: #2d2419 (Dark Surface)

Text Colors:
- Text Primary: #1b150e (Near Black)
- Text Secondary: #97754e (Medium Brown)
- Text Light: #ffffff (White)

Accent Colors:
- Accent: #ca7616 (Burnt Orange)
- Accent Light: #fef3c7 (Light Cream)

Semantic Colors:
- Success: #22c55e (Green)
- Error: #ef4444 (Red)
- Warning: #f59e0b (Amber)
- Info: #3b82f6 (Blue)

Gray Scale:
- Gray 100: #f5f5f4
- Gray 200: #e7e5e4
- Gray 300: #d6d3d1
- Gray 400: #a8a29e
- Gray 500: #78716c
```

### Typography
```
Font Sizes:
- xs: 12px
- sm: 14px
- base: 16px
- lg: 18px
- xl: 20px
- 2xl: 24px
- 3xl: 30px

Font Weights:
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700
```

### Spacing Scale
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 40px
```

### Border Radius
```
sm: 4px
md: 8px
lg: 12px
xl: 16px
2xl: 24px
```

---

## 📱 Screen Specifications

### 1. Welcome Screen

**Purpose:** App landing page with branding and quick navigation

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [☰ Menu]              [Top]    │ ← Header (transparent/minimal)
│                                  │
│         ॐ Om Symbol              │ ← Large spiritual icon (80-100px)
│                                  │
│       VastuWise AI               │ ← App title (3xl, bold, #db7706)
│   Ancient Wisdom, Modern Living  │ ← Tagline (sm, #97754e)
│                                  │
│  ┌──────────────────────────┐   │
│  │ 🏠 Comprehensive Analysis│   │ ← Feature Card 1
│  │   AI-powered insights    │   │   (White bg, rounded, shadow)
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 🧭 Direction Mapping      │   │ ← Feature Card 2
│  │   Precise compass tech    │   │
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 💡 Smart Remedies         │   │ ← Feature Card 3
│  │   Actionable solutions    │   │
│  └──────────────────────────┘   │
│                                  │
│  [Start Your Free Analysis →]   │ ← CTA Button (primary orange)
│  [Sign In]                       │ ← Secondary link
└─────────────────────────────────┘
```

**Components:**
1. **Header Bar**
   - Left: Hamburger menu icon (24px, #1b150e)
   - Background: transparent gradient fade
   - Height: 60px
   - Padding: 16px horizontal

2. **Om Symbol**
   - Size: 80x80px
   - Color: #db7706 with subtle glow
   - Positioned: Center, top 120px
   - Animated: Subtle pulse/fade

3. **Title Section**
   - "VastuWise AI": 30px bold, #db7706
   - Tagline: 14px regular, #97754e
   - Margin bottom: 40px
   - Center aligned

4. **Feature Cards** (3 cards)
   - Background: #ffffff
   - Border radius: 16px
   - Padding: 20px
   - Shadow: 0 4px 12px rgba(0,0,0,0.08)
   - Gap between cards: 16px
   - Icon left: 32x32px
   - Title: 16px semibold, #1b150e
   - Subtitle: 14px regular, #97754e
   - Border left: 4px solid #db7706

5. **CTA Button**
   - Background: #db7706
   - Text: "Start Your Free Analysis", 16px bold, #ffffff
   - Border radius: 12px
   - Padding: 16px 32px
   - Shadow: 0 6px 16px rgba(219,119,6,0.3)
   - Width: Full width - 32px margin
   - Margin bottom: 12px

6. **Sign In Link**
   - Text: 14px medium, #97754e
   - Center aligned
   - Underline on press

**Interactions:**
- Menu opens slide drawer from left
- Feature cards have subtle scale on press (0.98)
- CTA button navigates to AnalyzePlan or Login (based on auth)
- Sign In navigates to Login screen

---

### 2. Login Screen

**Purpose:** User authentication with email/password and Google OAuth

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]                        │ ← Header
│                                  │
│                                  │
│         🏛️ Building Icon         │ ← Large icon (64px)
│                                  │
│       Welcome Back               │ ← Title (2xl, bold)
│   Sign in to continue            │ ← Subtitle (sm)
│                                  │
│  ┌──────────────────────────┐   │
│  │ 📧 Email                  │   │ ← Email input
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 🔒 Password         [👁️] │   │ ← Password input + toggle
│  └──────────────────────────┘   │
│                                  │
│           [Forgot Password?]     │ ← Link
│                                  │
│  [Sign In →]                     │ ← Primary button
│                                  │
│  ──────── or ────────            │ ← Divider
│                                  │
│  [🔵 Continue with Google]       │ ← Google OAuth button
│                                  │
│  Don't have an account? Sign Up  │ ← Bottom link
└─────────────────────────────────┘
```

**Components:**
1. **Header**
   - Back button: Circle (40px), white bg, left arrow icon
   - Padding: 20px top (iOS), 16px horizontal

2. **Building Icon**
   - Lucide Building2 icon, 64px
   - Color: #db7706
   - Background circle: 120px, #fef3c7
   - Center aligned, margin top 40px

3. **Title Section**
   - "Welcome Back": 24px bold, #1b150e
   - Subtitle: 14px regular, #97754e
   - Center aligned, margin bottom 32px

4. **Email Input**
   - Background: #ffffff
   - Border: 1px solid #e7e5e4
   - Border radius: 12px
   - Padding: 16px
   - Icon left: Mail icon, 20px, #97754e
   - Placeholder: "Enter your email", #a8a29e
   - Font: 16px regular
   - Focus border: 2px solid #db7706
   - Margin bottom: 16px

5. **Password Input**
   - Same as email
   - Icon: Lock icon
   - Right icon: Eye/EyeOff toggle (24px)
   - Secure text entry

6. **Forgot Password Link**
   - Text: 14px medium, #db7706
   - Right aligned
   - Margin bottom: 24px

7. **Sign In Button**
   - Background: #db7706
   - Text: "Sign In", 16px bold, #ffffff
   - Arrow icon right: 16px
   - Border radius: 12px
   - Padding: 16px
   - Shadow: 0 4px 12px rgba(219,119,6,0.3)
   - Full width
   - Margin bottom: 24px

8. **Divider**
   - Line: 1px solid #e7e5e4
   - Text: "or", 14px, #97754e, background #fffaf5
   - Margin bottom: 24px

9. **Google Button**
   - Background: #ffffff
   - Border: 1px solid #e7e5e4
   - Text: "Continue with Google", 16px semibold, #1b150e
   - Google icon left: 20px
   - Border radius: 12px
   - Padding: 16px
   - Shadow: 0 2px 8px rgba(0,0,0,0.05)
   - Margin bottom: 32px

10. **Sign Up Link**
    - Text: "Don't have an account? ", 14px, #97754e
    - "Sign Up": 14px semibold, #db7706
    - Center aligned

**Interactions:**
- Input focus shows orange border
- Password toggle eye icon
- Form validation on submit
- Google OAuth opens web view
- Error messages below inputs in red (#ef4444)

---

### 3. Sign Up Screen

**Purpose:** New user registration

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]                        │
│                                  │
│       Create Account             │ ← Title
│   Join VastuWise AI              │ ← Subtitle
│                                  │
│  ┌──────────────────────────┐   │
│  │ 👤 Full Name              │   │ ← Name input
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 📧 Email                  │   │ ← Email input
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 🔒 Password         [👁️] │   │ ← Password input
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 🔒 Confirm Password [👁️] │   │ ← Confirm password
│  └──────────────────────────┘   │
│                                  │
│  ☑️ I agree to Terms & Privacy  │ ← Checkbox
│                                  │
│  [Create Account →]              │ ← Primary button
│                                  │
│  ──────── or ────────            │
│                                  │
│  [🔵 Sign up with Google]        │ ← Google OAuth
│                                  │
│  Already have an account? Login  │ ← Bottom link
└─────────────────────────────────┘
```

**Components:**
- Similar to Login Screen with additional fields
- Name input with User icon
- Confirm password field
- Terms checkbox (#db7706 when checked)
- Validation: Name required, email format, password min 8 chars, passwords match

---

### 4. Dashboard Screen

**Purpose:** Main hub after login with quick actions and insights

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [☰]  VastuWise        [👤][🔔] │ ← Header bar
│                                  │
│  ┌────────────────────────────┐ │
│  │ Hello, Rajesh! 👋          │ │ ← Welcome card
│  │ Your Vastu Score: 78/100   │ │   (Gradient bg: orange to light)
│  │ [View Details →]           │ │
│  └────────────────────────────┘ │
│                                  │
│  Quick Actions                   │ ← Section title
│  ┌──────────┐ ┌──────────┐     │
│  │ 📐       │ │ 🧭       │     │ ← Action cards (2 cols)
│  │ New      │ │ Direction│     │
│  │ Analysis │ │ Check    │     │
│  └──────────┘ └──────────┘     │
│                                  │
│  Recent Analyses                 │ ← Section title
│  ┌────────────────────────────┐ │
│  │ 🏠 Home Analysis - NE      │ │ ← Analysis item 1
│  │ Score: 82/100   2 days ago │ │   (White card, shadow)
│  │ [View Report →]            │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 🏢 Office - E Direction    │ │ ← Analysis item 2
│  │ Score: 75/100   1 week ago │ │
│  │ [View Report →]            │ │
│  └────────────────────────────┘ │
│                                  │
│  Vastu Tips                      │ ← Section title
│  ┌────────────────────────────┐ │
│  │ 💡 Keep entrance clutter-  │ │ ← Tip card
│  │ free for positive energy   │ │   (Light orange bg)
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**Components:**
1. **Header Bar**
   - Background: #db7706 gradient to #f59e0b
   - Height: 60px
   - Left: Menu icon (24px, white)
   - Center: "VastuWise" (18px bold, white)
   - Right: Profile icon + Bell icon (24px, white)
   - Shadow: 0 2px 8px rgba(219,119,6,0.2)

2. **Welcome Card**
   - Background: Linear gradient #db7706 to #fef3c7
   - Border radius: 16px
   - Padding: 24px
   - Name: 20px bold, #ffffff
   - Score: 16px medium, #ffffff
   - Progress bar: Full width, height 8px, rounded
     - Background: rgba(255,255,255,0.3)
     - Fill: #ffffff, width based on score
   - Button: Semi-transparent white, 14px semibold
   - Margin: 16px all sides

3. **Section Titles**
   - Font: 18px bold, #1b150e
   - Margin: 24px bottom, 16px horizontal
   - Letter spacing: -0.5px

4. **Action Cards** (Grid 2 columns)
   - Background: #ffffff
   - Border radius: 12px
   - Padding: 20px
   - Shadow: 0 4px 12px rgba(0,0,0,0.06)
   - Icon: 40px, #db7706
   - Title: 16px semibold, #1b150e
   - Gap: 16px
   - Aspect ratio: Square
   - Press effect: Scale 0.96

5. **Analysis Item Cards**
   - Background: #ffffff
   - Border radius: 12px
   - Padding: 16px
   - Shadow: 0 2px 8px rgba(0,0,0,0.05)
   - Border left: 4px solid #db7706
   - Icon: 24px
   - Title: 16px semibold, #1b150e
   - Score: 14px medium, #22c55e (if >70) or #f59e0b (if <70)
   - Time: 12px regular, #97754e
   - Arrow button: Right aligned, #db7706
   - Margin bottom: 12px

6. **Tip Card**
   - Background: #fef3c7
   - Border radius: 12px
   - Padding: 16px
   - Border: 1px solid #f59e0b
   - Icon: 20px, #db7706
   - Text: 14px regular, #1b150e

**Interactions:**
- Menu opens drawer
- Profile navigates to Profile screen
- Notifications opens notifications sheet
- Action cards navigate to respective screens
- Analysis items open detail reports
- Swipe to refresh updates data

---

### 5. Profile Form Screen

**Purpose:** User profile editing and settings

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]    Profile             │ ← Header
│                                  │
│       ┌──────────┐               │
│       │   👤     │               │ ← Avatar (large circle)
│       │  Photo   │               │   (80px, tap to edit)
│       └──────────┘               │
│                                  │
│  Personal Information            │ ← Section header
│  ┌──────────────────────────┐   │
│  │ Full Name                 │   │ ← Text input
│  │ Rajesh Kumar              │   │
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ Email                     │   │ ← Email input (disabled)
│  │ rajesh@email.com          │   │
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ Phone Number              │   │ ← Phone input
│  │ +91 98765 43210           │   │
│  └──────────────────────────┘   │
│                                  │
│  Location Details                │ ← Section header
│  ┌──────────────────────────┐   │
│  │ City                      │   │
│  │ Mumbai                    │   │
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ State                     │   │
│  │ Maharashtra               │   │
│  └──────────────────────────┘   │
│                                  │
│  [Save Changes]                  │ ← Primary button
│                                  │
│  Account Settings                │ ← Section header
│  [Change Password →]             │ ← Navigation item
│  [Notification Preferences →]    │ ← Navigation item
│  [Sign Out]                      │ ← Danger button
└─────────────────────────────────┘
```

**Components:**
1. **Avatar Section**
   - Circle: 80px diameter
   - Background: #f5f5f4
   - Border: 2px solid #db7706
   - User icon or uploaded image
   - Edit badge: Bottom right, 28px circle, #db7706, camera icon
   - Center aligned
   - Margin: 24px bottom

2. **Section Headers**
   - Font: 16px bold, #1b150e
   - Margin: 24px top, 12px bottom
   - Padding: 0 16px

3. **Text Inputs**
   - Background: #ffffff
   - Border: 1px solid #e7e5e4
   - Border radius: 12px
   - Padding: 16px
   - Label: 12px medium, #97754e (above input)
   - Value: 16px regular, #1b150e
   - Margin: 16px horizontal, 12px bottom
   - Focus border: 2px solid #db7706
   - Disabled state: Background #f5f5f4, text #a8a29e

4. **Save Button**
   - Background: #db7706
   - Text: "Save Changes", 16px bold, #ffffff
   - Border radius: 12px
   - Padding: 16px
   - Shadow: 0 4px 12px rgba(219,119,6,0.3)
   - Full width - 32px margin
   - Margin: 32px top, 24px bottom

5. **Navigation Items**
   - Background: #ffffff
   - Border: 1px solid #e7e5e4
   - Border radius: 12px
   - Padding: 16px
   - Text: 16px medium, #1b150e
   - Arrow right: 20px, #97754e
   - Margin: 12px horizontal and vertical
   - Press: Background #f5f5f4

6. **Sign Out Button**
   - Background: transparent
   - Border: 1px solid #ef4444
   - Text: "Sign Out", 16px semibold, #ef4444
   - Border radius: 12px
   - Padding: 16px
   - Full width - 32px margin

**Interactions:**
- Avatar tap opens image picker
- Inputs show keyboard with validation
- Save button shows loading spinner
- Success message toast on save
- Sign out shows confirmation alert

---

### 6. Analyze Plan Screen

**Purpose:** Upload floor plan for Vastu analysis

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]  Analyze Plan    [?]  │ ← Header
│                                  │
│  ┌────────────────────────────┐ │
│  │ 💡 VastuPro Tip      [×]   │ │ ← Dismissible tip card
│  │ Ensure North direction is  │ │   (Light yellow bg)
│  │ marked for accurate...     │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │         ☁️                 │ │ ← Upload area
│  │                            │ │   (Dashed border)
│  │  Upload Your Floor Plan    │ │
│  │  Our AI will analyze its   │ │
│  │  directional zones         │ │
│  │                            │ │
│  │  [📁 Upload Image]         │ │ ← Primary button
│  │                            │ │
│  │   📷         🖼️            │ │ ← Quick options
│  │  Camera    Gallery         │ │
│  │                            │ │
│  │  💡 Supported: PNG, JPG    │ │ ← Info text
│  └────────────────────────────┘ │
│                                  │
│  How to get best results         │ ← Section title
│                                  │
│  ┌────────────────────────────┐ │
│  │ 💡 Include room labels     │ │ ← Tip item 1
│  │ Kitchen, Master bedroom... │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 📏 Capture entire boundary │ │ ← Tip item 2
│  │ Complete shape is crucial  │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**Components:**
1. **Header**
   - Back button: Left, circle 40px
   - Title: "Analyze Plan", 20px bold, #1b150e
   - Help icon: Right, circle 40px, #1b150e background, white "?" icon

2. **Tip Card**
   - Background: #fff8e7
   - Border: 1px solid #ffe8b3
   - Border radius: 12px
   - Padding: 16px
   - Icon: Lightbulb, 20px, #db7706
   - Title: "VastuPro Tip", 14px semibold, #1b150e
   - Text: 12px regular, #97754e
   - Close button: X icon, 20px, #97754e
   - Margin: 16px

3. **Upload Card**
   - Background: #ffffff
   - Border: 2px dashed #db7706
   - Border radius: 16px
   - Padding: 32px 24px
   - Center aligned
   - Icon: Cloud, 40px, #db7706 (or uploaded image preview)
   - Title: 18px bold, #1b150e
   - Description: 14px regular, #97754e
   - Margin: 16px horizontal

4. **Upload Button**
   - Background: #fef3c7
   - Text: "Upload Image", 14px semibold, #b45309
   - Border radius: 8px
   - Padding: 12px 24px
   - Folder icon left: 18px
   - Margin: 24px vertical

5. **Quick Options** (2 buttons horizontal)
   - Camera button:
     - Icon: Camera, 32px, #db7706
     - Text: "Camera", 14px medium, #1b150e
     - Background: transparent
     - Padding: 12px
   - Gallery button: Same style
   - Gap: 32px between
   - Center aligned

6. **Supported Formats Text**
   - Icon: Lightbulb, 14px, #db7706
   - Text: "Supported: PNG, JPG, PDF", 12px regular, #97754e
   - Center aligned

7. **Section Title**
   - Font: 16px bold, #1b150e
   - Margin: 24px top, 16px bottom
   - Padding: 0 16px

8. **Tip Items**
   - Background: white
   - Border: none
   - Padding: 16px
   - Icon: Left, 20px
   - Title: 14px semibold, #1b150e
   - Text: 12px regular, #97754e
   - Gap: 12px between items
   - Margin: 0 16px

**Image Preview State:**
```
When image is uploaded:
- Show preview image (200px height)
- [Change Image] button below
- [Continue to Direction Setup →] button (primary orange)
```

**Interactions:**
- Tap upload area to pick image
- Camera/Gallery buttons request permissions then open picker
- Image shows in preview with change option
- Continue button navigates to DirectionSetup with image URI

---

### 7. Direction Setup Screen

**Purpose:** Set house entrance direction using phone compass

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]                        │ ← Header
│  Set Your House Entrance         │
│  Direction                       │
│  Go inside and face entrance     │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 🧭 Instructions            │ │ ← Info card
│  │ 1. Go inside your house    │ │   (Light purple bg)
│  │ 2. Stand facing entrance   │ │
│  │ 3. Hold phone flat         │ │
│  │ 4. Compass shows direction │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ You are currently facing:  │ │ ← Live compass card
│  │                            │ │   (White, orange border)
│  │       ┌──────┐             │ │
│  │       │  NE  │             │ │ ← Direction badge (large)
│  │       └──────┘             │ │   (Orange bg, white text)
│  │        135°                │ │ ← Degree heading
│  │                            │ │
│  │       ┌──────┐             │ │
│  │       │  N   │             │ │ ← Real-time compass
│  │    W  │  🧭  │  E          │ │   (Animated needle)
│  │       │  S   │             │ │   (120px circle)
│  │       └──────┘             │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ House Entrance Facing:     │ │ ← Confirmation card
│  │        NE                  │ │   (Purple bg)
│  │   (135° from North)        │ │
│  └────────────────────────────┘ │
│                                  │
│  [Confirm Entrance Direction →] │ ← Primary button
│                                  │
│  ┌────────────────────────────┐ │
│  │ ⚠️ Make sure you're inside │ │ ← Help box
│  │ facing outward toward door │ │   (Amber bg)
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**Components:**
1. **Header**
   - Back button: Circle 40px, white bg
   - Title: "Set Your House Entrance Direction", 16px bold, #1b150e
   - Subtitle: "Go inside and face the entrance", 14px medium, #97754e
   - Padding: 16px horizontal

2. **Info Card**
   - Background: #f3f0ff (light purple)
   - Border: 1px solid #e0d7ff
   - Border radius: 12px
   - Padding: 16px
   - Icon: Navigation, 18px, white (in purple circle 32px)
   - Title: "📍 Instructions", 14px bold, #7c3aed
   - Steps: 12px regular, #97754e, line height 18px
   - Margin: 16px

3. **Live Compass Card**
   - Background: #ffffff
   - Border: 2px solid #db7706
   - Border radius: 16px
   - Padding: 24px
   - Shadow: 0 4px 16px rgba(219,119,6,0.2)
   - Margin: 16px

4. **Direction Badge** (Inside compass card)
   - Background: #db7706
   - Padding: 12px 32px
   - Border radius: 8px
   - Text: Direction letters (e.g., "NE"), 30px bold, #ffffff
   - Letter spacing: 2px
   - Center aligned
   - Margin bottom: 8px

5. **Degree Heading**
   - Font: 18px medium, #97754e
   - Center aligned
   - Margin bottom: 16px

6. **Mini Compass** (Real-time animated)
   - Container: 120px circle
   - Background: #f3f0ff
   - Border: 3px solid #db7706
   - Cardinal markers:
     - N (top): 14px bold, #ef4444 (red for North)
     - E, S, W: 14px bold, #97754e
     - Positioned at edges (8px from border)
   - Needle:
     - Animated rotation based on magnetometer
     - North half: Red triangle (8px width, 35px height)
     - South half: Gray triangle
     - Smooth spring animation
   - Center aligned

7. **Confirmation Card**
   - Background: #f3f0ff
   - Border: 1px solid #e0d7ff
   - Border radius: 12px
   - Padding: 24px
   - Label: 14px medium, #97754e, center
   - Direction: 30px bold, #7c3aed, center
   - Degrees: 14px regular, #97754e, center
   - Margin: 16px

8. **Confirm Button**
   - Background: #db7706
   - Text: "Confirm Entrance Direction", 16px bold, #ffffff
   - Icon: Navigation, 14px, white (in circle badge)
   - Border radius: 12px
   - Padding: 16px 32px
   - Shadow: 0 4px 12px rgba(219,119,6,0.3)
   - Full width - 32px margin
   - Margin: 16px

9. **Help Box**
   - Background: #fff7ed
   - Border: 1px solid #fed7aa
   - Border radius: 8px
   - Padding: 16px
   - Icon: Alert triangle, 14px, #9a3412
   - Text: 14px regular, #9a3412, center, line height 20px
   - Margin: 16px

**Interactions:**
- Magnetometer updates 10 times/sec
- Compass needle rotates smoothly
- Direction badge updates when heading changes by >22.5°
- Confirm shows alert with final direction
- Error handling if magnetometer unavailable

---

### 8. Processing Screen (NEW)

**Purpose:** Show AI analysis progress while processing floor plan

**Layout Structure:**
```
┌─────────────────────────────────┐
│                                  │
│                                  │
│         ┌──────────┐             │
│         │   🔄     │             │ ← Animated spinner
│         │  Gears   │             │   (96px, orange)
│         └──────────┘             │
│                                  │
│      Analyzing Your Space        │ ← Main title (2xl, bold)
│                                  │
│   ━━━━━━━━━━━━━━━━━━━━━         │ ← Progress bar (75%)
│        75% Complete              │   (Orange fill, gray bg)
│                                  │
│  ┌────────────────────────────┐ │
│  │ ✓ Floor plan uploaded      │ │ ← Step 1 (complete)
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ ✓ Boundaries detected      │ │ ← Step 2 (complete)
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 🔄 Analyzing Vastu zones   │ │ ← Step 3 (in progress)
│  └────────────────────────────┘ │   (Pulsing animation)
│                                  │
│  ┌────────────────────────────┐ │
│  │ ⏳ Calculating scores      │ │ ← Step 4 (pending)
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ ⏳ Generating remedies     │ │ ← Step 5 (pending)
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 💡 Did you know?           │ │ ← Fun fact card
│  │ The Brahmasthan should be  │ │   (Rotating tips)
│  │ kept clutter-free          │ │   (Light yellow bg)
│  └────────────────────────────┘ │
│                                  │
│  Please wait, this may take     │ ← Helper text
│  30-60 seconds...                │
└─────────────────────────────────┘
```

**Components:**
1. **Animated Spinner**
   - Lottie animation or rotating gears
   - Size: 96x96px
   - Colors: #db7706 primary, #f59e0b secondary
   - Center aligned
   - Margin top: 80px

2. **Main Title**
   - Text: "Analyzing Your Space", 24px bold, #1b150e
   - Center aligned
   - Margin: 24px vertical

3. **Progress Bar**
   - Container:
     - Width: Full - 64px margin
     - Height: 8px
     - Background: #e7e5e4
     - Border radius: 4px
   - Fill:
     - Background: Linear gradient #db7706 to #f59e0b
     - Height: 8px
     - Border radius: 4px
     - Animated width transition
   - Percentage text: 16px medium, #97754e, center, margin 8px top

4. **Step Items** (5 items)
   - Complete state:
     - Background: #f0fdf4 (light green)
     - Border: 1px solid #22c55e
     - Icon: Checkmark circle, 20px, #22c55e
     - Text: 14px medium, #1b150e
     - Opacity: 0.7
   - In Progress state:
     - Background: #fef3c7 (light orange)
     - Border: 2px solid #db7706
     - Icon: Loading spinner, 20px, #db7706
     - Text: 14px semibold, #1b150e
     - Pulsing animation
   - Pending state:
     - Background: #f5f5f4
     - Border: 1px solid #e7e5e4
     - Icon: Clock, 20px, #a8a29e
     - Text: 14px regular, #97754e
   - Shared styles:
     - Border radius: 12px
     - Padding: 16px
     - Margin: 12px horizontal, 8px vertical
     - Flex row, align center

5. **Fun Fact Card**
   - Background: #fff8e7
   - Border: 1px solid #ffe8b3
   - Border radius: 12px
   - Padding: 16px
   - Icon: Lightbulb, 20px, #db7706
   - Title: "Did you know?", 14px bold, #1b150e
   - Text: 14px regular, #97754e
   - Margin: 24px horizontal, 16px vertical
   - Rotates every 5 seconds

6. **Helper Text**
   - Font: 12px regular, #97754e
   - Center aligned
   - Margin bottom: 32px

**Animations:**
- Spinner: Continuous rotation
- Progress bar: Smooth width transition
- Step items: Fade in sequentially
- Fun facts: Fade transition every 5s

**Interactions:**
- Auto-advance on completion
- Can't go back during processing
- Error state shows retry button
- Success navigates to Results screen

---

### 9. Final Result Screen (NEW)

**Purpose:** Display comprehensive Vastu analysis results with scores and issues

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]    Analysis Result    │ ← Header
│                                  │
│  ┌────────────────────────────┐ │
│  │  Vastu Score                │ │ ← Score card
│  │     ┌──────┐                │ │   (Gradient bg)
│  │     │  78  │                │ │   (Circular progress)
│  │     └──────┘                │ │
│  │      /100                   │ │
│  │   ⭐ Good                   │ │ ← Rating
│  │                             │ │
│  │  ━━━━━━━━━━━━━━━━━━━━      │ │ ← Score breakdown
│  │  Positive Zones: 65%        │ │
│  │  Neutral Zones: 20%         │ │
│  │  Doshas Found: 15%          │ │
│  └────────────────────────────┘ │
│                                  │
│  [📊 Overview] [⚠️ Issues]      │ ← Tab switcher
│                                  │
│  ────── Overview Tab ────────   │
│                                  │
│  Directional Analysis            │ ← Section title
│  ┌────────────────────────────┐ │
│  │ 🧭 Northeast (Ishaanya)    │ │ ← Zone card 1
│  │ Status: ✓ Excellent        │ │   (Green border)
│  │ Score: 92/100              │ │
│  │ Keep this area clean and   │ │
│  │ well-lit for prosperity    │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 🌅 Southeast (Agneya)      │ │ ← Zone card 2
│  │ Status: ⚠️ Needs Attention │ │   (Orange border)
│  │ Score: 68/100              │ │
│  │ Kitchen placement is good  │ │
│  │ but requires remedies      │ │
│  └────────────────────────────┘ │
│                                  │
│  ────── Issues Tab ──────────   │
│                                  │
│  Critical Issues (2)             │ ← Section title (red)
│  ┌────────────────────────────┐ │
│  │ ❌ Toilet in Northeast     │ │ ← Critical issue
│  │ Zone: NE Corner            │ │   (Red accent)
│  │ Impact: Financial loss,    │ │
│  │ health problems            │ │
│  │ [View Remedies →]          │ │
│  └────────────────────────────┘ │
│                                  │
│  Moderate Issues (3)             │ ← Section title (orange)
│  ┌────────────────────────────┐ │
│  │ ⚠️ Main door facing SW     │ │ ← Moderate issue
│  │ Zone: Southwest            │ │   (Orange accent)
│  │ Impact: Career obstacles   │ │
│  │ [View Remedies →]          │ │
│  └────────────────────────────┘ │
│                                  │
│  Recommendations (5)             │ ← Section title
│  ┌────────────────────────────┐ │
│  │ 💡 Place water fountain    │ │ ← Recommendation
│  │ in North direction         │ │   (Blue accent)
│  │ [Learn More →]             │ │
│  └────────────────────────────┘ │
│                                  │
│  [💾 Save Report] [📤 Share]    │ ← Action buttons
└─────────────────────────────────┘
```

**Components:**
1. **Header**
   - Back button + "Analysis Result" title
   - Share icon right (export PDF)
   - Background: white
   - Shadow: 0 2px 4px rgba(0,0,0,0.05)

2. **Score Card**
   - Background: Linear gradient #db7706 to #f59e0b
   - Border radius: 16px
   - Padding: 32px 24px
   - Shadow: 0 8px 24px rgba(219,119,6,0.2)
   - Margin: 16px
   
   **Circular Progress:**
   - Size: 140px diameter
   - Background ring: rgba(255,255,255,0.3), 12px width
   - Progress ring: #ffffff, 12px width
   - Center text: Score "78", 48px bold, white
   - Sub text: "/100", 20px medium, white opacity 0.8
   
   **Rating Badge:**
   - Star icon + text ("Good"), 16px semibold, white
   - Margin top: 16px
   
   **Score Breakdown:**
   - Divider: 1px solid rgba(255,255,255,0.3)
   - Each item:
     - Label: 14px regular, white
     - Percentage: 14px semibold, white
     - Progress bar: 4px height, rounded
     - Margin: 8px vertical

3. **Tab Switcher**
   - Container: 
     - Background: #f5f5f4
     - Border radius: 12px
     - Padding: 4px
     - Margin: 16px
   - Tabs (2):
     - Active: Background #ffffff, shadow
     - Inactive: Background transparent
     - Text: 14px semibold
     - Icon: 20px
     - Padding: 12px 24px
     - Border radius: 8px

4. **Section Titles**
   - Font: 18px bold, #1b150e
   - Margin: 24px top, 16px bottom
   - Padding: 0 16px
   - Color variants:
     - Critical: #ef4444
     - Moderate: #f59e0b
     - Normal: #1b150e

5. **Zone Cards** (Overview tab)
   - Background: #ffffff
   - Border radius: 12px
   - Padding: 20px
   - Border left: 4px solid (status color)
   - Shadow: 0 2px 8px rgba(0,0,0,0.05)
   - Margin: 12px horizontal, 8px vertical
   
   **Status indicator:**
   - Excellent: ✓ Green (#22c55e)
   - Good: ✓ Blue (#3b82f6)
   - Needs Attention: ⚠️ Orange (#f59e0b)
   - Critical: ❌ Red (#ef4444)
   
   **Content:**
   - Direction: 16px bold, #1b150e, with icon
   - Status: 14px semibold, status color
   - Score: 14px medium, #97754e
   - Description: 14px regular, #97754e, line height 20px

6. **Issue Cards** (Issues tab)
   - Similar to zone cards
   - Border left: 4px solid (severity color)
   - Icon: Left, 32px circle, severity color background
   - Title: 16px bold, #1b150e
   - Zone label: 12px medium, #97754e
   - Impact: 14px regular, #97754e
   - Button: "View Remedies →", 14px semibold, severity color
   - Margin: 12px horizontal, 8px vertical

7. **Recommendation Cards**
   - Background: #f0f9ff (light blue)
   - Border: 1px solid #bae6fd
   - Border radius: 12px
   - Padding: 16px
   - Icon: Lightbulb, 24px, #3b82f6
   - Text: 14px medium, #1b150e
   - Button: "Learn More →", 14px semibold, #3b82f6
   - Margin: 12px horizontal, 8px vertical

8. **Action Buttons** (Bottom)
   - Container: 
     - Background: white
     - Border top: 1px solid #e7e5e4
     - Padding: 16px
     - Fixed bottom
   
   - Save button:
     - Background: transparent
     - Border: 1px solid #db7706
     - Text: 16px semibold, #db7706
     - Icon: Save, 20px
     - Flex: 1
   
   - Share button:
     - Background: #db7706
     - Text: 16px semibold, white
     - Icon: Share, 20px
     - Flex: 1
   
   - Shared: Border radius 12px, padding 16px, margin 8px

**Interactions:**
- Tab switching with fade animation
- Cards expand on tap for full details
- "View Remedies" navigates to remedy details
- Score card animates on mount
- Save creates PDF report
- Share opens native share sheet
- Pull to refresh updates data

---

### 10. ChatBot Screen (NEW)

**Purpose:** AI assistant for Vastu queries and guidance

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [← Back]  Vastu Assistant  [⋮] │ ← Header
│                                  │
│  ┌────────────────────────────┐ │
│  │ 🤖 VastuBot               │ │ ← Bot intro card
│  │ Ask me anything about     │ │   (Light bg, dismissible)
│  │ Vastu Shastra!            │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────┐             │ ← Bot message (left)
│  │ Hello! How can │             │   (White bubble)
│  │ I help you     │             │
│  │ today?         │             │
│  └────────────────┘             │
│      12:30 PM                    │ ← Timestamp
│                                  │
│             ┌────────────────┐  │ ← User message (right)
│             │ What's best    │  │   (Orange bubble)
│             │ for kitchen?   │  │
│             └────────────────┘  │
│                  12:31 PM        │
│                                  │
│  ┌────────────────┐             │ ← Bot message
│  │ The kitchen is │             │
│  │ ideally in SE  │             │
│  │ (Agneya)...    │             │
│  └────────────────┘             │
│      12:31 PM                    │
│                                  │
│  Suggested Topics:               │ ← Quick replies
│  ┌──────────┐ ┌──────────┐     │   (Chips/pills)
│  │ Bedroom  │ │ Entrance │     │
│  └──────────┘ └──────────┘     │
│                                  │
│  ──────────────────────────────  │ ← Input bar (bottom)
│  [📎] Type your question... [▶] │
└─────────────────────────────────┘
```

**Components:**
1. **Header**
   - Background: #db7706 gradient
   - Height: 60px
   - Back button: White circle, left
   - Title: "Vastu Assistant", 18px bold, white
   - Menu icon: 3 dots, right, white
   - Shadow: 0 2px 8px rgba(219,119,6,0.2)

2. **Bot Intro Card** (First launch only)
   - Background: #fef3c7
   - Border: 1px solid #fde68a
   - Border radius: 12px
   - Padding: 16px
   - Icon: Robot emoji, 32px
   - Title: "VastuBot", 16px bold, #1b150e
   - Text: 14px regular, #97754e
   - Close button: X, top right
   - Margin: 16px

3. **Chat Container**
   - Background: #fffaf5
   - Padding: 16px
   - Scroll to bottom on new message

4. **Bot Messages** (Left aligned)
   - Bubble:
     - Background: #ffffff
     - Border radius: 16px (top-right, bottom-left, bottom-right), 4px (top-left)
     - Padding: 12px 16px
     - Max width: 80%
     - Shadow: 0 2px 4px rgba(0,0,0,0.05)
   - Avatar: 
     - Circle 32px, left
     - Background: #db7706
     - Robot icon, white
     - Margin right: 8px
   - Text: 14px regular, #1b150e, line height 20px
   - Timestamp: 12px regular, #97754e, below bubble
   - Links: Underlined, #3b82f6
   - Margin bottom: 16px

5. **User Messages** (Right aligned)
   - Bubble:
     - Background: #db7706
     - Border radius: 16px (top-left, bottom-left, bottom-right), 4px (top-right)
     - Padding: 12px 16px
     - Max width: 80%
   - Text: 14px regular, #ffffff, line height 20px
   - Timestamp: 12px regular, #97754e, below bubble
   - Margin bottom: 16px

6. **Typing Indicator**
   - Three dots animation
   - Same style as bot message
   - Pulsing animation: opacity 0.3 to 1

7. **Quick Reply Chips**
   - Container: Horizontal scroll
   - Background: #ffffff
   - Border: 1px solid #db7706
   - Border radius: 20px
   - Padding: 8px 16px
   - Text: 14px medium, #db7706
   - Gap: 8px
   - Margin: 16px horizontal, 8px vertical

8. **Suggested Topics** (When chat empty)
   - Section title: 14px semibold, #97754e
   - Grid: 2 columns
   - Topic cards:
     - Background: white
     - Border: 1px solid #e7e5e4
     - Border radius: 12px
     - Padding: 16px
     - Icon: 24px
     - Text: 14px medium, #1b150e
     - Press: Scale 0.96

9. **Input Bar** (Fixed bottom)
   - Background: #ffffff
   - Border top: 1px solid #e7e5e4
   - Padding: 12px 16px
   - Shadow: 0 -2px 8px rgba(0,0,0,0.05)
   
   **Attachment button:**
   - Icon: Paperclip, 24px, #97754e
   - Circle 40px, transparent
   - Left aligned
   
   **Text input:**
   - Background: #f5f5f4
   - Border radius: 20px
   - Padding: 12px 16px
   - Placeholder: "Type your question...", #a8a29e
   - Font: 14px regular, #1b150e
   - Flex: 1
   - Margin: 0 8px
   
   **Send button:**
   - Background: #db7706
   - Circle: 40px
   - Icon: Arrow right / Send, 20px, white
   - Disabled: Opacity 0.5 when empty
   - Right aligned

**Special Message Types:**
- **Card message** (for structured info):
  - Background: #fef3c7
  - Border: 1px solid #fde68a
  - Title, description, action button
  - Border radius: 12px
  - Embedded in chat flow

- **Image message**:
  - Rounded corners
  - Max width: 80%
  - Tap to expand

- **Error message**:
  - Background: #fef2f2
  - Border: 1px solid #fecaca
  - Red icon
  - Retry button

**Interactions:**
- Messages fade in from bottom
- Auto-scroll to latest message
- Send on return key
- Voice input button (optional)
- Copy message on long press
- Quick replies send immediately
- Typing indicator shows when bot processing

---

### 11. History Screen (NEW)

**Purpose:** View all past Vastu analyses with search and filter

**Layout Structure:**
```
┌─────────────────────────────────┐
│  [☰]  History           [🔍][⋮] │ ← Header
│                                  │
│  ┌────────────────────────────┐ │
│  │ 🔍 Search analyses...      │ │ ← Search bar
│  └────────────────────────────┘ │
│                                  │
│  [All] [Home] [Office] [Other]  │ ← Filter chips
│                                  │
│  This Month                      │ ← Section header
│  ┌────────────────────────────┐ │
│  │ ┌──────┐                   │ │ ← Analysis card 1
│  │ │ 🏠   │ Home Analysis     │ │   (White, shadow)
│  │ │      │ NE Entrance       │ │
│  │ └──────┘ Score: 82/100     │ │
│  │          ⭐⭐⭐⭐           │ │
│  │          2 days ago    [›] │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ ┌──────┐                   │ │ ← Analysis card 2
│  │ │ 🏢   │ Office Analysis   │ │
│  │ │      │ E Entrance        │ │
│  │ └──────┘ Score: 75/100     │ │
│  │          ⭐⭐⭐             │ │
│  │          5 days ago    [›] │ │
│  └────────────────────────────┘ │
│                                  │
│  Last Month                      │ ← Section header
│  ┌────────────────────────────┐ │
│  │ ┌──────┐                   │ │
│  │ │ 🏠   │ Apartment          │ │
│  │ │      │ SW Entrance       │ │
│  │ └──────┘ Score: 68/100     │ │
│  │          ⭐⭐⭐             │ │
│  │          3 weeks ago   [›] │ │
│  └────────────────────────────┘ │
│                                  │
│  [Load More...]                  │ ← Pagination
└─────────────────────────────────┘
```

**Components:**
1. **Header**
   - Background: #db7706
   - Height: 60px
   - Menu icon: Left, hamburger, white
   - Title: "History", 18px bold, white
   - Search icon: Right, magnifying glass, white
   - More icon: Right, 3 dots, white
   - Shadow: 0 2px 8px rgba(219,119,6,0.2)

2. **Search Bar**
   - Background: #ffffff
   - Border: 1px solid #e7e5e4
   - Border radius: 12px
   - Padding: 12px 16px
   - Icon: Magnifying glass, 20px, #97754e, left
   - Placeholder: "Search analyses...", #a8a29e
   - Font: 14px regular
   - Margin: 16px
   - Shadow: 0 2px 4px rgba(0,0,0,0.05)

3. **Filter Chips** (Horizontal scroll)
   - Container: Padding 0 16px, margin bottom 16px
   - Chip:
     - Active state:
       - Background: #db7706
       - Text: 14px semibold, #ffffff
       - Border radius: 20px
       - Padding: 8px 16px
     - Inactive state:
       - Background: transparent
       - Border: 1px solid #e7e5e4
       - Text: 14px medium, #97754e
   - Gap: 8px

4. **Section Headers**
   - Text: "This Month", "Last Month", etc.
   - Font: 16px bold, #1b150e
   - Background: #fffaf5
   - Padding: 12px 16px
   - Sticky on scroll

5. **Analysis Cards**
   - Background: #ffffff
   - Border radius: 12px
   - Padding: 16px
   - Shadow: 0 2px 8px rgba(0,0,0,0.05)
   - Margin: 12px horizontal, 8px vertical
   - Border left: 4px solid (score color)
   
   **Thumbnail:**
   - Size: 64x64px
   - Border radius: 8px
   - Background: #f5f5f4
   - Icon: 32px, centered
   - Left aligned
   - Margin right: 16px
   
   **Content:**
   - Title: 16px semibold, #1b150e
   - Subtitle: 14px regular, #97754e (entrance direction)
   - Score: 16px bold, score color
   - Stars: Visual rating (1-5 stars)
   - Time: 12px regular, #97754e
   
   **Chevron:**
   - Icon: Right arrow, 20px, #97754e
   - Right aligned
   - Vertical center

6. **Empty State** (No results)
   - Icon: Search with X, 64px, #a8a29e
   - Title: "No analyses found", 18px semibold, #1b150e
   - Text: "Try adjusting your search", 14px, #97754e
   - Center aligned
   - Padding: 64px vertical

7. **Load More Button**
   - Background: transparent
   - Border: 1px solid #e7e5e4
   - Border radius: 12px
   - Padding: 16px
   - Text: "Load More...", 14px semibold, #97754e
   - Width: Full - 32px margin
   - Margin: 24px 16px

**Swipe Actions** (on cards):
- Swipe left reveals:
  - Share button: Blue, 48px wide
  - Delete button: Red, 48px wide

**Interactions:**
- Pull to refresh
- Search filters in real-time
- Filter chips toggle active state
- Card tap navigates to result detail
- Delete shows confirmation alert
- Share opens native share sheet
- Infinite scroll loads more

---

## 🎯 Design Principles

### Consistency
- Use color palette consistently across all screens
- Maintain 16px base unit for spacing
- Apply border radius consistently (12px for cards, 8px for inputs)
- Shadow elevations: sm (2px), md (4px), lg (8px)

### Accessibility
- Minimum text size: 12px
- Contrast ratio: 4.5:1 for text
- Touch targets: Minimum 44x44px
- Color not sole indicator (use icons + text)

### Motion
- Duration: 200ms for micro, 300ms for standard, 400ms for complex
- Easing: ease-out for entrances, ease-in for exits
- Spring animations for natural feel (tension: 65, friction: 11)

### Responsive
- Max content width: 480px (centered on tablets)
- Padding: 16px horizontal minimum
- Safe area insets for iOS notch/home indicator
- Keyboard avoidance on input focus

---

## 📦 Component Library

### Buttons
- **Primary**: Orange bg, white text, 12px radius, shadow
- **Secondary**: White bg, orange border, orange text
- **Tertiary**: Transparent, orange text, no border
- **Danger**: Red border, red text (sign out)

### Cards
- **Elevated**: White bg, 12px radius, shadow 0 2px 8px
- **Flat**: White bg, 1px border gray, 12px radius
- **Colored**: Tinted bg (light version of color), colored border

### Inputs
- **Text**: White bg, gray border, 12px radius, 16px padding
- **Focus**: Orange 2px border, shadow glow
- **Error**: Red border, red text below
- **Disabled**: Gray bg, gray text

### Icons
- **Size**: 20px for inline, 24px for buttons, 32px for features
- **Color**: Inherit from context or #97754e for secondary
- **Style**: Lucide React Native (consistent stroke width)

---

This specification provides everything needed for Stitch AI to redesign your VastuWise AI app while maintaining the warm orange/amber color theme and adding the new screens (Processing, Results, ChatBot, History).
