/**
 * VastuWise AI - Example Profile/Edit Form Screen
 * Demonstrates form validation and error handling
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { colors, typography, spacing } from '../theme';
import { CustomButton, CustomTextInput } from '../components';

const ProfileFormScreen: React.FC = () => {
  // Form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  
  // Error state
  const [nameError, setNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  
  // Loading state
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validation functions
  const validateName = (value: string): boolean => {
    if (!value.trim()) {
      setNameError('Name is required');
      return false;
    }
    if (value.trim().length < 2) {
      setNameError('Name must be at least 2 characters');
      return false;
    }
    setNameError('');
    return true;
  };

  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value.trim()) {
      setEmailError('Email is required');
      return false;
    }
    if (!emailRegex.test(value)) {
      setEmailError('Please enter a valid email');
      return false;
    }
    setEmailError('');
    return true;
  };

  const validatePhone = (value: string): boolean => {
    const phoneRegex = /^[0-9]{10}$/;
    if (!value.trim()) {
      setPhoneError('Phone number is required');
      return false;
    }
    if (!phoneRegex.test(value.replace(/\D/g, ''))) {
      setPhoneError('Please enter a valid 10-digit phone number');
      return false;
    }
    setPhoneError('');
    return true;
  };

  // Form submission
  const handleSubmit = async () => {
    // Validate all fields
    const isNameValid = validateName(name);
    const isEmailValid = validateEmail(email);
    const isPhoneValid = validatePhone(phone);

    if (!isNameValid || !isEmailValid || !isPhoneValid) {
      Alert.alert('Validation Error', 'Please fix the errors before submitting');
      return;
    }

    // Simulate API call
    setIsSubmitting(true);
    
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(() => resolve(undefined), 2000));
      
      console.log('Form submitted:', { name, email, phone, address });
      Alert.alert('Success', 'Profile updated successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to update profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Reset form
  const handleReset = () => {
    setName('');
    setEmail('');
    setPhone('');
    setAddress('');
    setNameError('');
    setEmailError('');
    setPhoneError('');
  };

  return (
    <View style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Edit Profile</Text>
            <Text style={styles.subtitle}>Update your personal information</Text>
          </View>

          {/* Form Section */}
          <View style={styles.formSection}>
            <CustomTextInput
              label="Full Name *"
              placeholder="Enter your full name"
              value={name}
              onChangeText={(value) => {
                setName(value);
                if (nameError) validateName(value);
              }}
              onBlur={() => validateName(name)}
              error={nameError}
              icon="👤"
              autoCapitalize="words"
            />

            <CustomTextInput
              label="Email Address *"
              placeholder="Enter your email"
              value={email}
              onChangeText={(value) => {
                setEmail(value);
                if (emailError) validateEmail(value);
              }}
              onBlur={() => validateEmail(email)}
              error={emailError}
              icon="📧"
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <CustomTextInput
              label="Phone Number *"
              placeholder="Enter 10-digit phone number"
              value={phone}
              onChangeText={(value) => {
                setPhone(value);
                if (phoneError) validatePhone(value);
              }}
              onBlur={() => validatePhone(phone)}
              error={phoneError}
              icon="📱"
              keyboardType="phone-pad"
              maxLength={10}
            />

            <CustomTextInput
              label="Address (Optional)"
              placeholder="Enter your address"
              value={address}
              onChangeText={setAddress}
              icon="🏠"
              autoCapitalize="words"
            />
          </View>

          {/* Info Box */}
          <View style={styles.infoBox}>
            <Text style={styles.infoIcon}>ℹ️</Text>
            <Text style={styles.infoText}>
              Fields marked with * are required. Your information is secure and private.
            </Text>
          </View>

          {/* Action Buttons */}
          <View style={styles.actionsSection}>
            <CustomButton
              title={isSubmitting ? 'Saving...' : 'Save Changes'}
              icon="💾"
              variant="primary"
              onPress={handleSubmit}
              loading={isSubmitting}
              disabled={isSubmitting}
            />

            <CustomButton
              title="Reset Form"
              icon="🔄"
              variant="outline"
              onPress={handleReset}
              disabled={isSubmitting}
              style={styles.resetButton}
            />
          </View>
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
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  
  // Header
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.md,
  },
  title: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  
  // Form
  formSection: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.md,
  },
  
  // Info Box
  infoBox: {
    flexDirection: 'row',
    backgroundColor: colors.primaryOpacity(0.1),
    borderRadius: 12,
    padding: spacing.md,
    marginHorizontal: spacing.lg,
    marginTop: spacing.lg,
    gap: spacing.sm,
  },
  infoIcon: {
    fontSize: 20,
  },
  infoText: {
    flex: 1,
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  
  // Actions
  actionsSection: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.xl,
  },
  resetButton: {
    marginTop: spacing.md,
  },
});

export default ProfileFormScreen;
