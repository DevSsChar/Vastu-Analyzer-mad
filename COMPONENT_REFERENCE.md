# 🎨 Visual Component Reference Guide

## Quick Component Usage Examples

### 🔘 CustomButton

#### Primary Button
```typescript
<CustomButton
  title="Analyze My Home"
  icon="📊"
  variant="primary"
  onPress={() => console.log('Primary action')}
/>
```
**Visual:** Orange background (#db7706), white text, shadow

#### Secondary Button
```typescript
<CustomButton
  title="View Reports"
  icon="📄"
  variant="secondary"
  onPress={() => console.log('Secondary action')}
/>
```
**Visual:** White background, gray border, darker text

#### Outline Button
```typescript
<CustomButton
  title="Learn More"
  variant="outline"
  onPress={() => console.log('Outline action')}
/>
```
**Visual:** Transparent background, orange border

#### Button States
```typescript
// Loading state
<CustomButton title="Loading..." loading={true} />

// Disabled state
<CustomButton title="Disabled" disabled={true} />

// Different sizes
<CustomButton title="Small" size="small" />
<CustomButton title="Medium" size="medium" />
<CustomButton title="Large" size="large" />
```

---

### 📝 CustomTextInput

#### Basic Input
```typescript
const [email, setEmail] = useState('');

<CustomTextInput
  label="Email Address"
  placeholder="Enter your email"
  value={email}
  onChangeText={setEmail}
  keyboardType="email-address"
/>
```

#### With Icon
```typescript
<CustomTextInput
  label="Search"
  icon="🔍"
  placeholder="Search..."
  value={searchQuery}
  onChangeText={setSearchQuery}
/>
```

#### Password Input with Toggle
```typescript
<CustomTextInput
  label="Password"
  placeholder="Enter password"
  value={password}
  onChangeText={setPassword}
  showPasswordToggle={true}
/>
```

#### With Validation Error
```typescript
const [email, setEmail] = useState('');
const [error, setError] = useState('');

<CustomTextInput
  label="Email"
  value={email}
  onChangeText={setEmail}
  error={error ? "Invalid email format" : ""}
/>
```

---

### 🃏 CustomCard

#### Glass Card (Default)
```typescript
<CustomCard
  icon="🏠"
  title="Dosha Detection"
  description="Identify energy defects"
  variant="glass"
  onPress={() => console.log('Card pressed')}
/>
```
**Visual:** Translucent white background, subtle border

#### Solid Card
```typescript
<CustomCard
  icon="⭐"
  title="Vastu Score"
  description="85/100"
  variant="solid"
/>
```
**Visual:** Solid white background, clear border

#### Grid Layout (2x2)
```typescript
<View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 16 }}>
  {features.map((feature, index) => (
    <CustomCard
      key={index}
      icon={feature.icon}
      title={feature.title}
      description={feature.description}
      style={{ width: (screenWidth - 48) / 2 }}
    />
  ))}
</View>
```

---

### 🎯 CustomDrawer

#### Basic Usage
```typescript
import CustomDrawer from '../components/CustomDrawer';
import { useNavigation } from '@react-navigation/native';

export const WelcomeScreen = () => {
  const [drawerVisible, setDrawerVisible] = useState(false);
  const navigation = useNavigation();

  return (
    <View>
      {/* Menu Button */}
      <TouchableOpacity 
        style={styles.menuButton}
        onPress={() => setDrawerVisible(true)}
      >
        <Text style={styles.menuIcon}>☰</Text>
      </TouchableOpacity>

      {/* Drawer Component */}
      <CustomDrawer
        visible={drawerVisible}
        userData={{
          name: "John Doe",
          email: "john@example.com",
          profilePicture: null,
        }}
        onClose={() => setDrawerVisible(false)}
        onNavigate={(screen) => {
          setDrawerVisible(false);
          navigation.navigate(screen);
        }}
        onLogout={() => {
          setDrawerVisible(false);
          // Handle logout
          navigation.navigate('Login');
        }}
      />
    </View>
  );
};
```

#### Drawer Features
- **Animated Slide**: 300ms open, 250ms close transition
- **User Profile**: Avatar (first letter), name, email display
- **Menu Items**: Customizable navigation options
- **Logout Button**: With confirmation dialog
- **Overlay Tap**: Close drawer by tapping overlay

#### Styling Drawer
```typescript
// The drawer uses Modal and Animated.View internally
// Animation is handled automatically with smooth transitions

// Drawer overlay background (semi-transparent)
overlayOpacity: 0.5

// Drawer width: 80% of screen
// Slide distance: 0 to -250 (depends on screen width)
```

#### Menu Items
```typescript
// Default menu items in CustomDrawer:
const menuItems = [
  { label: 'Home', icon: '🏠', screen: 'Welcome' },
  { label: 'Dashboard', icon: '📊', screen: 'Dashboard' },
  { label: 'Profile', icon: '👤', screen: 'Profile' },
  { label: 'Learn Vastu', icon: '📚', screen: 'Learn' },
  { label: 'Settings', icon: '⚙️', screen: 'Settings' },
];
```

---

## 📐 Layout Patterns

### Centered Content
```typescript
<View style={{
  flex: 1,
  alignItems: 'center',
  justifyContent: 'center',
}}>
  <Text>Centered Content</Text>
</View>
```

### Vertical Stack
```typescript
<View style={{
  flexDirection: 'column',
  gap: 16,
  padding: 24,
}}>
  <CustomButton title="First" variant="primary" />
  <CustomButton title="Second" variant="outline" />
  <CustomButton title="Third" variant="secondary" />
</View>
```

### Horizontal Row
```typescript
<View style={{
  flexDirection: 'row',
  justifyContent: 'space-between',
  padding: 24,
}}>
  <CustomCard icon="🏠" title="Card 1" style={{ flex: 1 }} />
  <View style={{ width: 16 }} />
  <CustomCard icon="⭐" title="Card 2" style={{ flex: 1 }} />
</View>
```

### 2x2 Grid
```typescript
<View style={{
  flexDirection: 'row',
  flexWrap: 'wrap',
  gap: 16,
  padding: 24,
}}>
  <CustomCard icon="🧭" title="Card 1" style={{ width: '47%' }} />
  <CustomCard icon="⚡" title="Card 2" style={{ width: '47%' }} />
  <CustomCard icon="🏠" title="Card 3" style={{ width: '47%' }} />
  <CustomCard icon="🌸" title="Card 4" style={{ width: '47%' }} />
</View>
```

---

## 🎨 Theme Usage

### Colors
```typescript
import { colors } from '../theme';

// Backgrounds
backgroundColor: colors.backgroundLight    // #fffaf5
backgroundColor: colors.surfaceLight       // #ffffff

// Text
color: colors.textPrimary                  // #1b150e
color: colors.textSecondary                // #97754e
color: colors.textLight                    // #ffffff

// Primary
backgroundColor: colors.primary            // #db7706
borderColor: colors.primary

// With opacity
backgroundColor: colors.primaryOpacity(0.1)  // rgba(219, 119, 6, 0.1)
```

### Typography
```typescript
import { typography } from '../theme';

// Font sizes
fontSize: typography.fontSize.xs           // 12
fontSize: typography.fontSize.sm           // 14
fontSize: typography.fontSize.base         // 16
fontSize: typography.fontSize.lg           // 18
fontSize: typography.fontSize.xl           // 20
fontSize: typography.fontSize['2xl']       // 24
fontSize: typography.fontSize['3xl']       // 30

// Font weights
fontWeight: typography.fontWeight.regular  // '400'
fontWeight: typography.fontWeight.medium   // '500'
fontWeight: typography.fontWeight.semibold // '600'
fontWeight: typography.fontWeight.bold     // '700'
fontWeight: typography.fontWeight.extrabold// '800'
```

### Spacing
```typescript
import { spacing, borderRadius } from '../theme';

// Padding/Margin
padding: spacing.xs                        // 4
padding: spacing.sm                        // 8
padding: spacing.md                        // 16
padding: spacing.lg                        // 24
padding: spacing.xl                        // 32
padding: spacing['2xl']                    // 48

// Border Radius
borderRadius: borderRadius.sm              // 8
borderRadius: borderRadius.md              // 12
borderRadius: borderRadius.lg              // 16
borderRadius: borderRadius.xl              // 24
borderRadius: borderRadius.full            // 9999
```

---

## 🔍 Common Patterns

### Form with Validation
```typescript
const [email, setEmail] = useState('');
const [emailError, setEmailError] = useState('');

const validateEmail = (value: string) => {
  if (!value) {
    setEmailError('Email is required');
    return false;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    setEmailError('Invalid email format');
    return false;
  }
  setEmailError('');
  return true;
};

<CustomTextInput
  label="Email"
  value={email}
  onChangeText={(val) => {
    setEmail(val);
    if (emailError) validateEmail(val);
  }}
  onBlur={() => validateEmail(email)}
  error={emailError}
/>
```

### Loading State
```typescript
const [loading, setLoading] = useState(false);

const handleSubmit = async () => {
  setLoading(true);
  try {
    await apiCall();
  } finally {
    setLoading(false);
  }
};

<CustomButton
  title="Submit"
  loading={loading}
  onPress={handleSubmit}
/>
```

### Responsive Width
```typescript
import { Dimensions } from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const cardWidth = (SCREEN_WIDTH - spacing.lg * 2 - spacing.md) / 2;

<CustomCard style={{ width: cardWidth }} />
```

### Keyboard-Aware Form
```typescript
<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  <ScrollView keyboardShouldPersistTaps="handled">
    <CustomTextInput label="Field 1" />
    <CustomTextInput label="Field 2" />
    <CustomButton title="Submit" />
  </ScrollView>
</KeyboardAvoidingView>
```

---

## 🎯 Quick Tips

### DO ✅
- Use theme values for consistency
- Add loading states to async actions
- Validate inputs before submission
- Use KeyboardAvoidingView for forms
- Make buttons full-width on mobile
- Add proper spacing between elements
- Use TouchableOpacity for pressable items

### DON'T ❌
- Hardcode colors (use theme)
- Hardcode spacing (use spacing system)
- Forget to handle keyboard
- Ignore validation errors
- Use fixed widths (use flexible layouts)
- Forget loading/disabled states

---

## 📱 Screen Templates

### Full Screen with ScrollView
```typescript
<View style={{ flex: 1, backgroundColor: colors.backgroundLight }}>
  <ScrollView contentContainerStyle={{ paddingBottom: 32 }}>
    <View style={{ padding: 24 }}>
      {/* Content here */}
    </View>
  </ScrollView>
</View>
```

### Header + Content + Footer
```typescript
<View style={{ flex: 1 }}>
  {/* Header */}
  <View style={{ padding: 24 }}>
    <Text style={{ fontSize: 30, fontWeight: 'bold' }}>Title</Text>
  </View>
  
  {/* Content */}
  <ScrollView style={{ flex: 1 }}>
    {/* Content */}
  </ScrollView>
  
  {/* Footer */}
  <View style={{ padding: 24 }}>
    <CustomButton title="Action" variant="primary" />
  </View>
</View>
```

---

**Quick Reference Complete! Use these patterns to build consistent, professional React Native UIs.**
