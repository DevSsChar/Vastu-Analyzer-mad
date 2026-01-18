/**
 * VastuWise AI - Login Screen
 * Features: Google Sign-In, Email/Password authentication, Responsive design
 * Built with React Native core components
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Dimensions,
  StatusBar,
  Platform,
  Image,
  KeyboardAvoidingView,
  Alert,
  Linking,
} from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import { setToken, setUserData } from '../services/storage.service';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface LoginScreenProps {
  navigation?: any;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email.trim() || !password) {
      Alert.alert('Validation Error', 'Please enter email and password');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://10.0.2.2:3000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data: any = await response.json();

      if (response.ok) {
        // Store token and user data
        await setToken(data.token);
        await setUserData(data.user);
        
        // Navigate to Welcome screen with drawer
        if (navigation) {
          navigation.replace('Welcome');
        }
      } else {
        Alert.alert('Login Failed', data.error || 'Invalid credentials');
      }
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert('Error', 'Unable to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const googleAuthUrl = 'http://10.0.2.2:3000/api/auth/google'; // Use 10.0.2.2 for Android emulator
      await Linking.openURL(googleAuthUrl);
    } catch (error) {
      console.error('Google sign-in error:', error);
      Alert.alert('Error', 'Failed to open Google sign-in. Make sure the backend server is running.');
    }
  };

  const handleForgotPassword = () => {
    console.log('Forgot password');
    // Navigate to forgot password screen
  };

  const handleSignUp = () => {
    if (navigation) {
      navigation.navigate('SignUp');
    } else {
      console.log('Navigation not configured');
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.backgroundLight} />
      
      {/* Background Pattern */}
      <View style={styles.patternBackground} />
      
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Back Button */}
          <TouchableOpacity style={styles.backButton} onPress={() => console.log('Go back')}>
            <Text style={styles.backIcon}>←</Text>
          </TouchableOpacity>

          {/* Branding Section */}
          <View style={styles.brandingSection}>
            <View style={styles.logoContainer}>
              <Text style={styles.logoIcon}>🏛️</Text>
            </View>
            <Text style={styles.appTitle}>VastuWise AI</Text>
            <Text style={styles.appSubtitle}>Ancient Wisdom meets Modern AI</Text>
          </View>

          {/* Social Login Section */}
          <View style={styles.socialLoginSection}>
            <TouchableOpacity
              style={styles.googleButton}
              activeOpacity={0.8}
              onPress={handleGoogleSignIn}
            >
              <View style={styles.googleIconContainer}>
                <Text style={styles.googleIcon}>G</Text>
              </View>
              <Text style={styles.googleButtonText}>Sign in with Google</Text>
            </TouchableOpacity>
          </View>

          {/* Divider */}
          <View style={styles.dividerContainer}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>OR</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* Login Form */}
          <View style={styles.formSection}>
            {/* Email Field */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Email Address</Text>
              <View
                style={[
                  styles.inputContainer,
                  emailFocused && styles.inputContainerFocused,
                ]}
              >
                <TextInput
                  style={styles.input}
                  placeholder="Enter your email"
                  placeholderTextColor={colors.textSecondary}
                  value={email}
                  onChangeText={setEmail}
                  onFocus={() => setEmailFocused(true)}
                  onBlur={() => setEmailFocused(false)}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoComplete="email"
                />
              </View>
            </View>

            {/* Password Field */}
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Password</Text>
              <View
                style={[
                  styles.inputContainer,
                  passwordFocused && styles.inputContainerFocused,
                ]}
              >
                <TextInput
                  style={styles.input}
                  placeholder="Enter your password"
                  placeholderTextColor={colors.textSecondary}
                  value={password}
                  onChangeText={setPassword}
                  onFocus={() => setPasswordFocused(true)}
                  onBlur={() => setPasswordFocused(false)}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoComplete="password"
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Text style={styles.passwordToggleIcon}>
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </Text>
                </TouchableOpacity>
              </View>
              
              {/* Forgot Password Link */}
              <TouchableOpacity onPress={handleForgotPassword} style={styles.forgotPasswordContainer}>
                <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
              </TouchableOpacity>
            </View>

            {/* Login Button */}
            <TouchableOpacity
              style={[styles.loginButton, loading && styles.loginButtonDisabled]}
              activeOpacity={0.8}
              onPress={handleLogin}
              disabled={loading}
            >
              <Text style={styles.loginButtonText}>
                {loading ? 'Logging in...' : 'Login'}
              </Text>
            </TouchableOpacity>
          </View>

          {/* Footer Section */}
          <View style={styles.footerSection}>
            <Text style={styles.footerText}>
              Don't have an account?{' '}
              <Text style={styles.signUpLink} onPress={handleSignUp}>
                Sign Up
              </Text>
            </Text>
          </View>

          {/* Bottom Indicator */}
          <View style={styles.bottomIndicator} />
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundLight,
  },
  patternBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    opacity: 0.05,
    backgroundColor: colors.backgroundLight,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: spacing.xl,
    maxWidth: 430,
    width: '100%',
    alignSelf: 'center',
  },

  // Back Button
  backButton: {
    padding: spacing.md,
    marginLeft: -spacing.sm,
    marginTop: Platform.OS === 'ios' ? spacing.lg : spacing.md,
    width: 48,
  },
  backIcon: {
    fontSize: 24,
    color: colors.textPrimary,
  },

  // Branding Section
  brandingSection: {
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.xl,
  },
  logoContainer: {
    width: 64,
    height: 64,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  logoIcon: {
    fontSize: 32,
  },
  appTitle: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    letterSpacing: typography.letterSpacing.tight,
  },
  appSubtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
  },

  // Social Login
  socialLoginSection: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  googleButton: {
    width: '100%',
    height: 56,
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.gray200,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    shadowColor: colors.blackOpacity(0.1),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  googleIconContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleIcon: {
    fontSize: 14,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },
  googleButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },

  // Divider
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    gap: spacing.md,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: colors.gray300,
    opacity: 0.5,
  },
  dividerText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textSecondary,
    letterSpacing: typography.letterSpacing.wider,
  },

  // Form Section
  formSection: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
  inputGroup: {
    gap: spacing.xs,
  },
  inputLabel: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textPrimary,
    paddingHorizontal: spacing.xs,
    marginBottom: spacing.xs,
  },
  inputContainer: {
    height: 56,
    backgroundColor: colors.whiteOpacity(0.5),
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.gray300,
    paddingHorizontal: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
  inputContainerFocused: {
    borderColor: colors.primary,
    borderWidth: 2,
    backgroundColor: colors.surfaceLight,
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    padding: 0,
  },
  passwordToggle: {
    padding: spacing.sm,
    marginRight: -spacing.sm,
  },
  passwordToggleIcon: {
    fontSize: 20,
  },
  forgotPasswordContainer: {
    alignSelf: 'flex-end',
    marginTop: spacing.xs,
    paddingVertical: spacing.xs,
  },
  forgotPasswordText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
  },

  // Login Button
  loginButton: {
    width: '100%',
    height: 56,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.md,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 8,
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    letterSpacing: typography.letterSpacing.wide,
  },

  // Footer
  footerSection: {
    alignItems: 'center',
    paddingTop: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  footerText: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  signUpLink: {
    color: colors.primary,
    fontWeight: typography.fontWeight.bold,
  },

  // Bottom Indicator
  bottomIndicator: {
    width: 128,
    height: 6,
    backgroundColor: colors.blackOpacity(0.1),
    borderRadius: borderRadius.full,
    alignSelf: 'center',
    marginTop: spacing.md,
  },
});

export default LoginScreen;
