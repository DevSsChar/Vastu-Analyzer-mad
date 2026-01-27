/**
 * VastuWise AI - Custom Text Input Component
 * Reusable text input with label, validation, and focus states
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacity,
  TextInputProps,
} from 'react-native';
import { Eye, EyeOff, LucideIcon } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

interface CustomTextInputProps extends TextInputProps {
  label?: string;
  error?: string;
  icon?: React.ComponentType<any>;
  rightIcon?: React.ComponentType<any>;
  onRightIconPress?: () => void;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
  showPasswordToggle?: boolean;
}

const CustomTextInput: React.FC<CustomTextInputProps> = ({
  label,
  error,
  icon,
  rightIcon,
  onRightIconPress,
  containerStyle,
  inputStyle,
  showPasswordToggle = false,
  secureTextEntry,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  return (
    <View style={[styles.container, containerStyle]}>
      {/* Label */}
      {label && <Text style={styles.label}>{label}</Text>}

      {/* Input Container */}
      <View
        style={[
          styles.inputContainer,
          isFocused && styles.inputContainerFocused,
          error && styles.inputContainerError,
        ]}
      >
        {/* Left Icon */}
        {icon && (
          <View style={styles.leftIcon}>
            {React.createElement(icon, { size: 20, color: colors.textSecondary, strokeWidth: 2 })}
          </View>
        )}

        {/* Text Input */}
        <TextInput
          style={[styles.input, inputStyle]}
          placeholderTextColor={colors.textSecondary}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          secureTextEntry={showPasswordToggle ? !isPasswordVisible : secureTextEntry}
          {...props}
        />

        {/* Right Icon or Password Toggle */}
        {showPasswordToggle ? (
          <TouchableOpacity
            style={styles.rightIconButton}
            onPress={() => setIsPasswordVisible(!isPasswordVisible)}
          >
            {isPasswordVisible ? (
              <Eye size={20} color={colors.textSecondary} strokeWidth={2} />
            ) : (
              <EyeOff size={20} color={colors.textSecondary} strokeWidth={2} />
            )}
          </TouchableOpacity>
        ) : rightIcon ? (
          <TouchableOpacity
            style={styles.rightIconButton}
            onPress={onRightIconPress}
          >
            <View style={styles.rightIcon}>
              {React.createElement(rightIcon, { size: 20, color: colors.textSecondary, strokeWidth: 2 })}
            </View>
          </TouchableOpacity>
        ) : null}
      </View>

      {/* Error Message */}
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  label: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    paddingHorizontal: spacing.xs,
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
  inputContainerError: {
    borderColor: colors.error,
    borderWidth: 2,
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    padding: 0,
  },
  leftIcon: {
    marginRight: spacing.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rightIconButton: {
    padding: spacing.sm,
    marginRight: -spacing.sm,
  },
  rightIcon: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: typography.fontSize.xs,
    color: colors.error,
    marginTop: spacing.xs,
    paddingHorizontal: spacing.xs,
  },
});

export default CustomTextInput;
