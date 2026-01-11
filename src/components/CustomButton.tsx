/**
 * VastuWise AI - Custom Button Component
 * Reusable button with primary, secondary, and outline variants
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  View,
} from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

interface CustomButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  icon?: string;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

const CustomButton: React.FC<CustomButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  icon,
  loading = false,
  disabled = false,
  fullWidth = true,
  size = 'large',
  style,
  textStyle,
}) => {
  const getButtonStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      ...styles.button,
      ...(fullWidth && styles.fullWidth),
    };

    // Size variations
    if (size === 'small') baseStyle.height = 40;
    if (size === 'medium') baseStyle.height = 48;
    if (size === 'large') baseStyle.height = 56;

    // Variant styles
    if (variant === 'primary') {
      return { ...baseStyle, ...styles.primaryButton };
    } else if (variant === 'secondary') {
      return { ...baseStyle, ...styles.secondaryButton };
    } else {
      return { ...baseStyle, ...styles.outlineButton };
    }
  };

  const getTextStyle = (): TextStyle => {
    const baseTextStyle: TextStyle = { ...styles.buttonText };

    if (variant === 'primary') {
      return { ...baseTextStyle, ...styles.primaryButtonText };
    } else if (variant === 'secondary') {
      return { ...baseTextStyle, ...styles.secondaryButtonText };
    } else {
      return { ...baseTextStyle, ...styles.outlineButtonText };
    }
  };

  return (
    <TouchableOpacity
      style={[
        getButtonStyle(),
        disabled && styles.disabledButton,
        style,
      ]}
      onPress={onPress}
      activeOpacity={0.8}
      disabled={disabled || loading}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'primary' ? colors.textLight : colors.primary}
        />
      ) : (
        <View style={styles.buttonContent}>
          {icon && <Text style={styles.buttonIcon}>{icon}</Text>}
          <Text style={[getTextStyle(), textStyle]}>{title}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  fullWidth: {
    width: '100%',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  buttonIcon: {
    fontSize: 20,
  },
  buttonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    letterSpacing: typography.letterSpacing.wide,
  },

  // Primary Button
  primaryButton: {
    backgroundColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  primaryButtonText: {
    color: colors.textLight,
  },

  // Secondary Button
  secondaryButton: {
    backgroundColor: colors.surfaceLight,
    borderWidth: 1,
    borderColor: colors.gray200,
    shadowColor: colors.blackOpacity(0.1),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  secondaryButtonText: {
    color: colors.textPrimary,
  },

  // Outline Button
  outlineButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: colors.primaryOpacity(0.3),
  },
  outlineButtonText: {
    color: colors.textPrimary,
  },

  // Disabled State
  disabledButton: {
    opacity: 0.5,
  },
});

export default CustomButton;
