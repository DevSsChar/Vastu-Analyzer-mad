/**
 * VastuWise AI - Custom Card Component
 * Reusable card with glass morphism effect
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ViewStyle,
  TouchableOpacity,
} from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

interface CustomCardProps {
  icon?: string;
  title: string;
  description?: string;
  onPress?: () => void;
  style?: ViewStyle;
  variant?: 'glass' | 'solid';
  children?: React.ReactNode;
}

const CustomCard: React.FC<CustomCardProps> = ({
  icon,
  title,
  description,
  onPress,
  style,
  variant = 'glass',
  children,
}) => {
  const CardWrapper = onPress ? TouchableOpacity : View;

  return (
    <CardWrapper
      style={[
        styles.card,
        variant === 'glass' ? styles.glassCard : styles.solidCard,
        style,
      ]}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      {icon && (
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>{icon}</Text>
        </View>
      )}
      
      <View style={styles.content}>
        <Text style={styles.title}>{title}</Text>
        {description && <Text style={styles.description}>{description}</Text>}
      </View>
      
      {children}
    </CardWrapper>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    alignItems: 'center',
    shadowColor: colors.blackOpacity(0.1),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  glassCard: {
    backgroundColor: colors.whiteOpacity(0.7),
    borderWidth: 1,
    borderColor: colors.whiteOpacity(0.8),
  },
  solidCard: {
    backgroundColor: colors.surfaceLight,
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primaryOpacity(0.1),
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  icon: {
    fontSize: 24,
  },
  content: {
    alignItems: 'center',
  },
  title: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    textAlign: 'center',
  },
  description: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 16,
  },
});

export default CustomCard;
