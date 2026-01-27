/**
 * VastuWise AI - Example Profile/Edit Form Screen
 * Demonstrates form validation and error handling
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { User, Mail, Smartphone, Home, Info, Save, RotateCcw, ArrowLeft } from 'lucide-react-native';
import { colors, typography, spacing } from '../theme';
import { CustomButton, CustomTextInput } from '../components';
import { getToken, setUserData as saveUserData } from '../services/storage.service';
import { API_BASE_URL } from '../config/api.config';
import { TouchableOpacity } from 'react-native';

// API Response Interfaces
interface UserData {
  id: string;
  email: string;
  name: string;
  phoneNumber?: string;
  address?: string;
  profilePicture?: string;
  dateOfBirth?: string;
  createdAt?: string;
  updatedAt?: string;
}

interface GetProfileResponse {
  user: UserData;
}

interface UpdateProfileResponse {
  message: string;
  user: UserData;
}

interface ErrorResponse {
  error: string;
  errors?: Array<{ msg: string; param: string }>;
}

interface ProfileFormScreenProps {
  navigation?: any;
}

const ProfileFormScreen: React.FC<ProfileFormScreenProps> = ({ navigation }) => {
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
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user profile on component mount
  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      setIsLoading(true);
      const token = await getToken();
      
      if (!token) {
        Alert.alert('Error', 'You must be logged in to view profile');
        if (navigation) {
          navigation.navigate('Login');
        }
        return;
      }

      const response = await fetch(`${API_BASE_URL}/user/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json() as GetProfileResponse | ErrorResponse;

      if (response.ok && 'user' in data) {
        setName(data.user.name || '');
        setEmail(data.user.email || '');
        setPhone(data.user.phoneNumber || '');
        setAddress(data.user.address || '');
      } else {
        const errorData = data as ErrorResponse;
        Alert.alert('Error', errorData.error || 'Failed to load profile');
      }
    } catch (error) {
      console.error('Fetch profile error:', error);
      Alert.alert('Error', 'Unable to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

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
    const isPhoneValid = validatePhone(phone);

    if (!isNameValid || !isPhoneValid) {
      Alert.alert('Validation Error', 'Please fix the errors before submitting');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const token = await getToken();
      
      if (!token) {
        Alert.alert('Error', 'You must be logged in to update profile');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/user/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          phoneNumber: phone.trim(),
          address: address.trim() || null,
        }),
      });

      const data = await response.json() as UpdateProfileResponse | ErrorResponse;

      if (response.ok && 'user' in data) {
        // Update local storage with new user data
        await saveUserData(data.user);
        Alert.alert('Success', 'Profile updated successfully!');
        
        // Navigate back or to dashboard
        if (navigation) {
          navigation.goBack();
        }
      } else {
        const errorData = data as ErrorResponse;
        Alert.alert('Error', errorData.error || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Update profile error:', error);
      Alert.alert('Error', 'Unable to connect to server. Please try again.');
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

  if (isLoading) {
    return (
      <View style={[styles.container, styles.loadingContainer]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }

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
          {/* Back Button */}
          {navigation && (
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <ArrowLeft size={24} color={colors.textPrimary} strokeWidth={2} />
            </TouchableOpacity>
          )}

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
              icon={User}
              autoCapitalize="words"
            />

            <CustomTextInput
              label="Email Address"
              placeholder="Enter your email"
              value={email}
              onChangeText={setEmail}
              icon={Mail}
              keyboardType="email-address"
              autoCapitalize="none"
              editable={false}
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
              icon={Smartphone}
              keyboardType="phone-pad"
              maxLength={10}
            />

            <CustomTextInput
              label="Address (Optional)"
              placeholder="Enter your address"
              value={address}
              onChangeText={setAddress}
              icon={Home}
              autoCapitalize="words"
            />
          </View>

          {/* Info Box */}
          <View style={styles.infoBox}>
            <Info size={20} color={colors.primary} strokeWidth={2} style={{ marginRight: spacing.sm }} />
            <Text style={styles.infoText}>
              Fields marked with * are required. Your information is secure and private.
            </Text>
          </View>

          {/* Action Buttons */}
          <View style={styles.actionsSection}>
            <CustomButton
              title={isSubmitting ? 'Saving...' : 'Save Changes'}
              icon={Save}
              variant="primary"
              onPress={handleSubmit}
              loading={isSubmitting}
              disabled={isSubmitting}
            />

            <CustomButton
              title="Reset Form"
              icon={RotateCcw}
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
  loadingContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  backButton: {
    padding: spacing.md,
    marginLeft: spacing.sm,
    marginTop: Platform.OS === 'ios' ? spacing.lg : spacing.md,
    width: 48,
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
