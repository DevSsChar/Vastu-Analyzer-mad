/**
 * VastuWise AI - Landing Screen
 * Initial welcome screen with features and CTA
 */

import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
} from 'react-native';
import { Menu, User, Home, Compass, Lightbulb, ArrowRight, ChevronRight } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import { getToken } from '../services/storage.service';

interface LandingScreenProps {
  navigation?: any;
}

const LandingScreen: React.FC<LandingScreenProps> = ({ navigation }) => {
  const handleGetStarted = async () => {
    try {
      const token = await getToken();
      if (token) {
        // User is already logged in, go to Dashboard
        navigation?.navigate('Dashboard');
      } else {
        // User is not logged in, go to Login
        navigation?.navigate('Login');
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      navigation?.navigate('Login');
    }
  };

  const features = [
    {
      id: '1',
      icon: 'home',
      title: 'Comprehensive Analysis',
      description: 'Scan your floor plan instantly',
    },
    {
      id: '2',
      icon: 'compass',
      title: 'Direction Mapping',
      description: 'Accurate cardinal alignment',
    },
    {
      id: '3',
      icon: 'lightbulb',
      title: 'Smart Remedies',
      description: 'AI-suggested corrections',
    },
  ];

  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'home':
        return <Home size={28} color={colors.primary} />;
      case 'compass':
        return <Compass size={28} color={colors.primary} />;
      case 'lightbulb':
        return <Lightbulb size={28} color={colors.primary} />;
      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#fffaf5" translucent={false} />

      {/* Header */}
      {/* <View style={styles.header}>
        <TouchableOpacity style={styles.headerButton} activeOpacity={0.7}>
          <Menu size={28} color={colors.textPrimary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.headerButton} activeOpacity={0.7}>
          <User size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View> */}

      {/* Main Content */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Hero Section */}
        <View style={styles.hero}>
          {/* Om Symbol */}
          <View style={styles.logoContainer}>
            <Text style={styles.omSymbol}>ॐ</Text>
          </View>

          {/* Headline */}
          <Text style={styles.headline}>VastuWise AI</Text>

          {/* Tagline */}
          <Text style={styles.tagline}>Ancient Wisdom, Modern Living</Text>
        </View>

        {/* Feature Cards */}
        <View style={styles.featuresContainer}>
          {features.map((feature) => (
            <TouchableOpacity
              key={feature.id}
              style={styles.featureCard}
              activeOpacity={0.7}
            >
              <View style={styles.featureIconContainer}>
                {renderIcon(feature.icon)}
              </View>
              <View style={styles.featureContent}>
                <Text style={styles.featureTitle}>{feature.title}</Text>
                <Text style={styles.featureDescription}>{feature.description}</Text>
              </View>
              <ChevronRight size={24} color="#D1D5DB" />
            </TouchableOpacity>
          ))}
        </View>

        {/* CTA Section */}
        <View style={styles.ctaContainer}>
          <TouchableOpacity
            style={styles.ctaButton}
            onPress={handleGetStarted}
            activeOpacity={0.8}
          >
            <Text style={styles.ctaButtonText}>Start Your Free Analysis</Text>
            <ArrowRight size={20} color={colors.textLight} />
          </TouchableOpacity>

          <Text style={styles.ctaSubtext}>
            Unlock peace and prosperity in your home today.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fffaf5',
    paddingTop: StatusBar.currentHeight || 0,   
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },
  headerButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.xl,
  },
  hero: {
    alignItems: 'center',
    marginBottom: spacing.xl * 1.5,
  },
  logoContainer: {
    marginBottom: spacing.md,
  },
  omSymbol: {
    fontSize: 100,
    color: colors.primary,
    opacity: 0.9,
    textShadowColor: 'rgba(0, 0, 0, 0.05)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  headline: {
    fontSize: 36,
    fontWeight: typography.fontWeight.extrabold,
    color: colors.primary,
    textAlign: 'center',
    letterSpacing: -0.5,
    marginBottom: spacing.sm,
  },
  tagline: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.medium,
    color: 'rgba(24, 21, 17, 0.7)',
    textAlign: 'center',
    letterSpacing: 0.3,
  },
  featuresContainer: {
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  featureCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    borderLeftWidth: 6,
    borderLeftColor: colors.primary,
    shadowColor: colors.blackOpacity(0.05),
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 2,
    elevation: 1,
  },
  featureIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primaryOpacity(0.1),
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    lineHeight: 24,
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: typography.fontSize.sm,
    color: 'rgba(24, 21, 17, 0.6)',
  },
  ctaContainer: {
    marginTop: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  ctaButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.xl,
    gap: spacing.sm,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
  },
  ctaButtonText: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },
  ctaSubtext: {
    fontSize: typography.fontSize.xs,
    color: 'rgba(24, 21, 17, 0.4)',
    textAlign: 'center',
    marginTop: spacing.md,
  },
});

export default LandingScreen;
