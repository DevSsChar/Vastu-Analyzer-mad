/**
 * VastuWise AI - Welcome/Onboarding Screen
 * Features: Sacred symbol branding, feature cards grid, call-to-action buttons
 * Responsive mobile layout using React Native components
 */

import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  StatusBar,
  Platform,
} from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import CustomDrawer from '../components/CustomDrawer';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface WelcomeScreenProps {
  navigation?: any;
}

// Feature Card Component
interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description }) => {
  return (
    <View style={styles.featureCard}>
      <View style={styles.iconContainer}>
        <Text style={styles.iconText}>{icon}</Text>
      </View>
      <View style={styles.cardContent}>
        <Text style={styles.cardTitle}>{title}</Text>
        <Text style={styles.cardDescription}>{description}</Text>
      </View>
    </View>
  );
};

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ navigation }) => {
  const [drawerVisible, setDrawerVisible] = React.useState(false);
  
  const features = [
    {
      icon: '🧭',
      title: 'Directional Analysis',
      description: 'Align with nature\'s energy',
    },
    {
      icon: '⚡',
      title: 'Vastu Score',
      description: 'Check compliance level',
    },
    {
      icon: '🏠',
      title: 'Dosha Detection',
      description: 'Identify energy defects',
    },
    {
      icon: '🌸',
      title: 'Vedic Remedies',
      description: 'Ancient balancing fixes',
    },
  ];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.backgroundLight} />
      
      {/* Background Pattern Overlay */}
      <View style={styles.patternOverlay} pointerEvents="none" />
      
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        bounces={true}
      >
        {/* Header Section - Branding & Sacred Symbol */}
        <View style={styles.headerSection}>
          {/* Sacred Symbol with Pulse Animation */}
          <View style={styles.symbolContainer}>
            <View style={styles.symbolPulse} />
            <View style={styles.symbolCircle}>
              <Text style={styles.symbolIcon}>🕉️</Text>
              {/* Decorative AI nodes */}
              <View style={[styles.aiNode, styles.aiNodeTopRight]} />
              <View style={[styles.aiNode, styles.aiNodeBottomLeft]} />
            </View>
          </View>
          
          <Text style={styles.appTitle}>VastuWise AI</Text>
          <Text style={styles.appSubtitle}>वास्तु शास्त्र विश्लेषण</Text>
        </View>

        {/* Features Grid Section */}
        <View style={styles.featuresSection}>
          <View style={styles.featuresGrid}>
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </View>
          
          {/* Inspirational Quote */}
          <View style={styles.quoteContainer}>
            <Text style={styles.quoteText}>
              "Transform your living space into a sanctuary of peace and prosperity."
            </Text>
          </View>
        </View>

        {/* Bottom CTA Section */}
        <View style={styles.ctaSection}>
          {/* Primary Action Button */}
          <TouchableOpacity
            style={styles.primaryButton}
            activeOpacity={0.8}
            onPress={() => console.log('Analyze Home')}
          >
            <Text style={styles.primaryButtonIcon}>📊</Text>
            <Text style={styles.primaryButtonText}>Analyze My Home</Text>
          </TouchableOpacity>

          {/* Secondary Action Button */}
          <TouchableOpacity
            style={styles.secondaryButton}
            activeOpacity={0.7}
            onPress={() => console.log('Learn About Vastu')}
          >
            <Text style={styles.secondaryButtonText}>Learn About Vastu</Text>
          </TouchableOpacity>

          {/* Page Indicator */}
          <View style={styles.pageIndicator}>
            <View style={[styles.indicatorDot, styles.indicatorActive]} />
            <View style={styles.indicatorDot} />
            <View style={styles.indicatorDot} />
          </View>
        </View>
      </ScrollView>

      {/* Menu Button - Outside ScrollView */}
      <TouchableOpacity
        style={styles.menuButton}
        onPress={() => {
          console.log('Menu button pressed');
          setDrawerVisible(true);
        }}
        activeOpacity={0.7}
      >
        <Text style={styles.menuIcon}>☰</Text>
      </TouchableOpacity>

      {/* Custom Drawer */}
      <CustomDrawer
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        navigation={navigation}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundLight,
  },
  menuButton: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 50 : 20,
    left: 20,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    shadowColor: colors.blackOpacity(0.2),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 10,
  },
  menuIcon: {
    fontSize: 24,
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.bold,
  },
  patternOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    opacity: 0.05,
    backgroundColor: colors.backgroundLight,
    zIndex: -1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: spacing.xl,
  },
  
  // Header Section Styles
  headerSection: {
    alignItems: 'center',
    paddingTop: Platform.OS === 'ios' ? spacing['2xl'] + 20 : spacing['2xl'],
    paddingBottom: spacing.lg,
    paddingHorizontal: spacing.lg,
  },
  symbolContainer: {
    position: 'relative',
    marginBottom: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  symbolPulse: {
    position: 'absolute',
    width: 112,
    height: 112,
    borderRadius: 56,
    backgroundColor: colors.primaryOpacity(0.2),
  },
  symbolCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 12,
    borderWidth: 2,
    borderColor: colors.primaryOpacity(0.2),
  },
  symbolIcon: {
    fontSize: 40,
  },
  aiNode: {
    position: 'absolute',
    borderRadius: 999,
    backgroundColor: colors.primary,
  },
  aiNodeTopRight: {
    width: 12,
    height: 12,
    top: -4,
    right: -4,
    borderWidth: 2,
    borderColor: colors.surfaceLight,
  },
  aiNodeBottomLeft: {
    width: 8,
    height: 8,
    bottom: -4,
    left: -4,
    borderWidth: 2,
    borderColor: colors.surfaceLight,
  },
  appTitle: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.extrabold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    letterSpacing: typography.letterSpacing.tight,
  },
  appSubtitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.medium,
    color: colors.primary,
    letterSpacing: typography.letterSpacing.wide,
    opacity: 0.9,
  },
  
  // Features Section Styles
  featuresSection: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.lg,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    maxWidth: 450,
    alignSelf: 'center',
    width: '100%',
  },
  featureCard: {
    width: (SCREEN_WIDTH - spacing.md * 3) / 2,
    backgroundColor: colors.whiteOpacity(0.7),
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
    alignItems: 'center',
    shadowColor: colors.blackOpacity(0.1),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 1,
    borderColor: colors.whiteOpacity(0.8),
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
  iconText: {
    fontSize: 24,
  },
  cardContent: {
    alignItems: 'center',
  },
  cardTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    textAlign: 'center',
  },
  cardDescription: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 16,
  },
  quoteContainer: {
    marginTop: spacing.xl,
    paddingHorizontal: spacing.lg,
    alignItems: 'center',
  },
  quoteText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontStyle: 'italic',
    textAlign: 'center',
    lineHeight: 20,
  },
  
  // CTA Section Styles
  ctaSection: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    gap: spacing.md,
    alignItems: 'center',
    maxWidth: 450,
    alignSelf: 'center',
    width: '100%',
  },
  primaryButton: {
    width: '100%',
    height: 56,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  primaryButtonIcon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
  primaryButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    letterSpacing: typography.letterSpacing.wide,
  },
  secondaryButton: {
    width: '100%',
    height: 56,
    backgroundColor: 'transparent',
    borderRadius: borderRadius.lg,
    borderWidth: 2,
    borderColor: colors.primaryOpacity(0.3),
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textPrimary,
  },
  pageIndicator: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  indicatorDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.gray300,
  },
  indicatorActive: {
    width: 24,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.primary,
  },
});

export default WelcomeScreen;
