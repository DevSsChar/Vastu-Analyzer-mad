# VastuWise AI - Configuration & Setup Guide

## 📋 App Configuration

### 1. App Name & Package Name Configuration

#### Update App Display Name
**File:** `app.json`
```json
{
  "name": "VastuWiseAI",
  "displayName": "VastuWise AI"
}
```

#### Android Package Name
**File:** `android/app/build.gradle`
```gradle
android {
    namespace "com.vastuwiseai"  // Update this
    defaultConfig {
        applicationId "com.vastuwiseai"  // Update this
        ...
    }
}
```

**File:** `android/app/src/main/AndroidManifest.xml`
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.vastuwiseai">  <!-- Update this -->
    ...
</manifest>
```

**Move Java/Kotlin Files:**
```bash
# Old path: android/app/src/main/java/com/madapp/
# New path: android/app/src/main/java/com/vastuwiseai/
```

#### iOS Bundle Identifier
**File:** `ios/MadApp.xcodeproj/project.pbxproj`
Search for `PRODUCT_BUNDLE_IDENTIFIER` and update to:
```
PRODUCT_BUNDLE_IDENTIFIER = com.vastuwiseai;
```

**Rename Xcode Project:**
1. Open Xcode
2. Select project root in navigator
3. In Identity section, update "Bundle Identifier"

---

## 🎨 Theme Configuration

### Primary Colors
**File:** `src/theme/colors.ts`

```typescript
export const colors = {
  primary: '#db7706',        // Main brand color
  primaryDark: '#b45309',    // Darker variant
  primaryLight: '#f59e0b',   // Lighter variant
  
  // Update these to match your brand
  accent: '#ca7616',
  // ... more colors
};
```

### Typography Setup
**File:** `src/theme/typography.ts`

```typescript
export const typography = {
  fontFamily: {
    display: 'Plus Jakarta Sans',  // Update to your font
    body: 'Noto Sans',
  },
  // Font sizes, weights, etc.
};
```

### Spacing System
**File:** `src/theme/spacing.ts`

```typescript
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  // Adjust as needed
};
```

---

## 📱 Screens & Components Overview

### Welcome Screen
**File:** `src/screens/WelcomeScreen.tsx`

**Key Features:**
- Sacred symbol branding with pulse animation
- 2x2 feature cards grid
- Primary and secondary CTA buttons
- Page indicator dots
- Fully responsive layout

**Customization Points:**
```typescript
// Update features array
const features = [
  { icon: '🧭', title: 'Your Feature', description: 'Description' },
  // Add more features
];

// Update button actions
<TouchableOpacity onPress={() => navigation.navigate('Analysis')}>
```

### Login Screen
**File:** `src/screens/LoginScreen.tsx`

**Key Features:**
- Google Sign-In button
- Email/Password fields with validation
- Password visibility toggle
- Forgot password link
- Sign up navigation
- Keyboard-aware scrolling

**Customization Points:**
```typescript
// Update authentication handlers
const handleLogin = () => {
  // Add your auth logic
  console.log('Login with:', email, password);
};

const handleGoogleSignIn = () => {
  // Integrate Google Sign-In SDK
};
```

---

## 🎯 Using Reusable Components

### CustomButton
```typescript
import { CustomButton } from '../components';

<CustomButton
  title="Click Me"
  onPress={() => console.log('Pressed')}
  variant="primary"    // primary | secondary | outline
  icon="🚀"
  size="large"         // small | medium | large
  loading={false}
  disabled={false}
  fullWidth={true}
/>
```

### CustomTextInput
```typescript
import { CustomTextInput } from '../components';

<CustomTextInput
  label="Email Address"
  placeholder="Enter your email"
  value={email}
  onChangeText={setEmail}
  keyboardType="email-address"
  autoCapitalize="none"
  error={emailError}
  icon="📧"
  showPasswordToggle={false}
/>
```

### CustomCard
```typescript
import { CustomCard } from '../components';

<CustomCard
  icon="🏠"
  title="Card Title"
  description="Card description text"
  variant="glass"      // glass | solid
  onPress={() => console.log('Card pressed')}
/>
```

---

## 📐 Layout Best Practices

### Responsive Spacing
```typescript
import { Dimensions } from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// Calculate responsive widths
const cardWidth = (SCREEN_WIDTH - spacing.md * 3) / 2;

<View style={{ width: cardWidth }}>
  {/* Content */}
</View>
```

### Flexible Layouts
```typescript
// Column layout
<View style={{ flexDirection: 'column', gap: spacing.md }}>
  {/* Stacked items */}
</View>

// Row layout
<View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
  {/* Side-by-side items */}
</View>

// Centered content
<View style={{ alignItems: 'center', justifyContent: 'center' }}>
  {/* Centered items */}
</View>
```

### Safe Areas
```typescript
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Wrap your app
<SafeAreaProvider>
  <App />
</SafeAreaProvider>

// Use safe area padding
paddingTop: Platform.OS === 'ios' ? spacing['2xl'] + 20 : spacing['2xl']
```

### Keyboard Handling
```typescript
<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  <ScrollView keyboardShouldPersistTaps="handled">
    {/* Form content */}
  </ScrollView>
</KeyboardAvoidingView>
```

---

## 🎨 Styling Guidelines

### Using Theme Colors
```typescript
import { colors } from '../theme';

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.backgroundLight,
  },
  text: {
    color: colors.textPrimary,
  },
  button: {
    backgroundColor: colors.primary,
  },
});
```

### Typography Styles
```typescript
import { typography } from '../theme';

const styles = StyleSheet.create({
  title: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
  },
  body: {
    fontSize: typography.fontSize.base,
    lineHeight: typography.lineHeight.normal,
  },
});
```

### Shadows & Elevation
```typescript
// iOS shadow
shadowColor: colors.primary,
shadowOffset: { width: 0, height: 4 },
shadowOpacity: 0.3,
shadowRadius: 8,

// Android elevation
elevation: 4,
```

---

## 🚀 Running & Building

### Development
```bash
# Install dependencies
npm install

# iOS
cd ios && pod install && cd ..
npm run ios

# Android
npm run android
```

### Debugging
```bash
# Open React Native Debugger
npm start

# View logs
npx react-native log-ios
npx react-native log-android
```

### Building for Production

#### iOS
1. Open `ios/MadApp.xcworkspace` in Xcode
2. Select "Any iOS Device"
3. Product → Archive
4. Distribute to App Store

#### Android
```bash
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

---

## 📚 Next Steps

### Add Navigation
```bash
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
```

### Add Vector Icons
```bash
npm install react-native-vector-icons
```

Replace emoji icons with:
```typescript
import Icon from 'react-native-vector-icons/MaterialIcons';

<Icon name="explore" size={28} color={colors.primary} />
```

### State Management
```bash
# Redux
npm install @reduxjs/toolkit react-redux

# Or Context API (built-in)
# Create contexts in src/context/
```

### API Integration
```bash
npm install axios
# Or use fetch API (built-in)
```

---

## 🎓 Learning Checklist

- [x] App Name & Package configuration
- [x] Theme setup (colors, typography, spacing)
- [x] Login Screen with email/password
- [x] Welcome Screen with features grid
- [x] Reusable Button component
- [x] Reusable Input component
- [x] Reusable Card component
- [x] Responsive layouts
- [x] Proper spacing & alignment
- [x] Material Design principles
- [ ] Navigation implementation
- [ ] API integration
- [ ] State management
- [ ] Form validation
- [ ] Error handling

---

## 📞 Support & Resources

- [React Native Docs](https://reactnative.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/)
- [React Navigation](https://reactnavigation.org/)
- [Material Design](https://material.io/design)

---

Built with ❤️ using React Native & TypeScript
