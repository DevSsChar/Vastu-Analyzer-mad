/**
 * VastuWise AI - Bottom Navigation Component
 * Reusable bottom navigation bar with elevated scan button
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Home as HomeIcon, Camera, BookOpen } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

interface BottomNavProps {
  navigation: any;
  activeScreen?: string;
}

const BottomNav: React.FC<BottomNavProps> = ({ navigation, activeScreen = 'Dashboard' }) => {
  const handleNewAnalysis = () => {
    navigation.navigate('AnalyzePlan');
  };

  const handleNavigation = (screen: string) => {
    if (screen === 'Learn') {
      console.log('Learn section coming soon');
    } else {
      navigation.navigate(screen);
    }
  };

  return (
    <View style={styles.bottomNav}>
      <TouchableOpacity
        style={styles.navItem}
        onPress={() => handleNavigation('Dashboard')}
        activeOpacity={0.7}
      >
        <HomeIcon 
          size={24} 
          color={activeScreen === 'Dashboard' ? colors.primary : colors.textSecondary} 
          strokeWidth={2} 
        />
        <Text style={[styles.navLabel, { color: activeScreen === 'Dashboard' ? colors.primary : colors.textSecondary }]}>
          Home
        </Text>
      </TouchableOpacity>

      <View style={styles.navItemCenter}>
        <TouchableOpacity
          style={styles.scanButton}
          onPress={handleNewAnalysis}
          activeOpacity={0.8}
        >
          <Camera size={28} color={colors.textLight} strokeWidth={2.5} />
        </TouchableOpacity>
        <Text style={[styles.navLabel, { color: colors.textSecondary, marginTop: spacing.xl }]}>
          Scan
        </Text>
      </View>

      <TouchableOpacity
        style={styles.navItem}
        onPress={() => handleNavigation('Learn')}
        activeOpacity={0.7}
      >
        <BookOpen 
          size={24} 
          color={activeScreen === 'Learn' ? colors.primary : colors.textSecondary} 
          strokeWidth={2} 
        />
        <Text style={[styles.navLabel, { color: activeScreen === 'Learn' ? colors.primary : colors.textSecondary }]}>
          Learn
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: colors.backgroundLight,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    borderTopLeftRadius: borderRadius['xl'],
    borderTopRightRadius: borderRadius['xl'],
    height: 72,
    paddingBottom: spacing.md,
    elevation: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    alignItems: 'flex-end',
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: spacing.sm,
    gap: spacing.xs,
  },
  navItemCenter: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingTop: spacing.xs,
  },
  scanButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: -32,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 12,
    borderWidth: 4,
    borderColor: colors.backgroundLight,
  },
  navLabel: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold,
  },
});

export default BottomNav;
