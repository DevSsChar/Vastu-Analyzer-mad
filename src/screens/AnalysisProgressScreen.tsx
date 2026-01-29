/**
 * VastuWise AI - Analysis Progress Screen
 * Real-time analysis progress with animated circular progress
 * Features: Progress tracking, task status, rotating Vastu facts
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Platform,
  Animated,
  StatusBar,
} from 'react-native';
import { ArrowLeft, Bot, Check, Lightbulb } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import BottomNav from '../components/BottomNav';

interface AnalysisProgressScreenProps {
  navigation?: any;
}

interface AnalysisStep {
  id: string;
  title: string;
  subtitle: string;
  status: 'completed' | 'in-progress' | 'pending';
  progress?: number;
}

const VASTU_FACTS = [
  {
    title: "DID YOU KNOW?",
    fact: "The northeast corner (Ishanya) represents water and divinity. It should always be kept light and open."
  },
  {
    title: "DID YOU KNOW?",
    fact: "Sleeping with your head towards the south or east promotes better health and peaceful sleep according to Vastu principles."
  },
  {
    title: "DID YOU KNOW?",
    fact: "The kitchen should ideally be in the southeast (Agneya) corner, governed by the fire element for positive energy flow."
  },
  {
    title: "DID YOU KNOW?",
    fact: "Mirrors should never be placed directly opposite to the main entrance as they reflect positive energy away from the home."
  },
  {
    title: "DID YOU KNOW?",
    fact: "Water bodies or fountains in the north or northeast direction bring prosperity and financial growth to the household."
  },
  {
    title: "DID YOU KNOW?",
    fact: "The center of the home (Brahmasthan) should be kept open and clutter-free to allow energy to flow freely throughout the space."
  },
  {
    title: "DID YOU KNOW?",
    fact: "Heavy furniture and storage should be placed in the south or west directions to balance the energy of the space."
  },
  {
    title: "DID YOU KNOW?",
    fact: "Vastu Shastra is over 5,000 years old and translates to 'science of architecture' in Sanskrit."
  },
  {
    title: "DID YOU KNOW?",
    fact: "Plants in the east direction of your home promote health and vitality, while plants in the north attract wealth."
  },
  {
    title: "DID YOU KNOW?",
    fact: "The main entrance facing east welcomes the morning sun and brings positive energy, health, and growth to residents."
  }
];

const AnalysisProgressScreen: React.FC<AnalysisProgressScreenProps> = ({ navigation }) => {
  const [progress] = useState(new Animated.Value(0));
  const [currentFactIndex, setCurrentFactIndex] = useState(0);
  const [steps] = useState<AnalysisStep[]>([
    {
      id: '1',
      title: 'Detecting Rooms & Spaces',
      subtitle: 'Found: 2 Bedrooms, 1 Kitchen, 1 Living',
      status: 'completed',
    },
    {
      id: '2',
      title: 'Analyzing Directional Alignment',
      subtitle: 'North-East axis verified successfully',
      status: 'completed',
    },
    {
      id: '3',
      title: 'Calculating Vastu Score',
      subtitle: 'Processing geometric ratios...',
      status: 'in-progress',
      progress: 65,
    },
    {
      id: '4',
      title: 'Generating Recommendations',
      subtitle: 'Est. completion: ~20 seconds',
      status: 'pending',
    },
  ]);

  useEffect(() => {
    // Animate progress to 73%
    Animated.timing(progress, {
      toValue: 73,
      duration: 2000,
      useNativeDriver: false,
    }).start();

    // Auto-rotate facts every 30 seconds
    const factInterval = setInterval(() => {
      setCurrentFactIndex((prevIndex) => (prevIndex + 1) % VASTU_FACTS.length);
    }, 30000);

    return () => clearInterval(factInterval);
  }, []);

  const handleFactClick = () => {
    setCurrentFactIndex((prevIndex) => (prevIndex + 1) % VASTU_FACTS.length);
  };

  const progressPercentage = progress.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  });

  const currentFact = VASTU_FACTS[currentFactIndex];

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation?.goBack()}
          activeOpacity={0.7}
        >
          <ArrowLeft size={24} color={colors.textPrimary} strokeWidth={2} />
        </TouchableOpacity>
        
        <View style={styles.headerSpacer} />
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Circular Progress */}
        <View style={styles.progressSection}>
          <View style={styles.progressCircleContainer}>
            {/* Background Circle */}
            <View style={styles.progressCircleBackground} />
            
            {/* Progress Arc - Simulated with styled view */}
            <View style={styles.progressArcContainer}>
              <View style={[styles.progressArc, styles.progressArcOrange]} />
              <View style={[styles.progressArc, styles.progressArcYellow]} />
            </View>

            {/* Center Content */}
            <View style={styles.progressCenter}>
              <View style={styles.aiIconContainer}>
                <Bot size={36} color={colors.primary} strokeWidth={2} />
              </View>
              <Text style={styles.progressText}>73%</Text>
            </View>
          </View>
          
          <Text style={styles.progressStatus}>Analyzing Alignment...</Text>
        </View>

        {/* Analysis Steps */}
        <View style={styles.stepsContainer}>
          {steps.map((step, index) => (
            <View key={step.id} style={styles.stepItem}>
              {/* Status Icon */}
              <View style={styles.stepIconContainer}>
                {step.status === 'completed' && (
                  <View style={styles.completedIcon}>
                    <Check size={16} color={colors.textLight} strokeWidth={3} />
                  </View>
                )}
                {step.status === 'in-progress' && (
                  <View style={styles.inProgressIcon}>
                    <View style={styles.inProgressInner} />
                  </View>
                )}
                {step.status === 'pending' && (
                  <View style={styles.pendingIcon} />
                )}
              </View>

              {/* Step Content */}
              <View style={styles.stepContent}>
                <Text style={styles.stepTitle}>{step.title}</Text>
                <Text style={[
                  styles.stepSubtitle,
                  step.status === 'in-progress' && styles.stepSubtitleActive
                ]}>
                  {step.subtitle}
                </Text>
                
                {/* Progress Bar for in-progress step */}
                {step.status === 'in-progress' && step.progress !== undefined && (
                  <View style={styles.progressBarContainer}>
                    <View 
                      style={[
                        styles.progressBarFill,
                        { width: `${step.progress}%` }
                      ]} 
                    />
                  </View>
                )}
              </View>

              {/* Time Estimate Badge */}
              {step.status === 'pending' && index === steps.length - 1 && (
                <View style={styles.timeBadge}>
                  <Text style={styles.timeBadgeIcon}>⏱</Text>
                  <Text style={styles.timeBadgeText}>Est. completion: ~20 seconds</Text>
                </View>
              )}
            </View>
          ))}
        </View>

        {/* Did You Know Section */}
        <TouchableOpacity
          style={styles.factCard}
          onPress={handleFactClick}
          activeOpacity={0.9}
        >
          <View style={styles.factHeader}>
            <Lightbulb size={24} color='#FDB022' strokeWidth={2} style={{ marginRight: spacing.sm }} />
            <Text style={styles.factTitle}>{currentFact.title}</Text>
          </View>
          <Text style={styles.factText}>{currentFact.fact}</Text>
          <View style={styles.factIndicator}>
            {VASTU_FACTS.map((_, index) => (
              <View
                key={index}
                style={[
                  styles.factDot,
                  index === currentFactIndex && styles.factDotActive
                ]}
              />
            ))}
          </View>
        </TouchableOpacity>
      </ScrollView>

      {/* Bottom Navigation */}
      <BottomNav navigation={navigation} activeScreen="AnalysisProgress" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundLight,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    paddingBottom: spacing.md,
    backgroundColor: colors.backgroundLight,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backIcon: {
    fontSize: 24,
    color: colors.textPrimary,
  },
  headerTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  headerSpacer: {
    width: 40,
  },
  scrollContent: {
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.xl,
  },
  
  // Progress Section Styles
  progressSection: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  progressCircleContainer: {
    width: 200,
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    marginBottom: spacing.lg,
  },
  progressCircleBackground: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 12,
    borderColor: '#E8E8F0',
  },
  progressArcContainer: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
  },
  progressArc: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 12,
    borderColor: 'transparent',
  },
  progressArcOrange: {
    borderTopColor: '#F97316',
    borderRightColor: '#F97316',
    transform: [{ rotate: '-45deg' }],
  },
  progressArcYellow: {
    borderBottomColor: '#FDB022',
    borderLeftColor: '#FDB022',
    transform: [{ rotate: '-45deg' }],
  },
  progressCenter: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  aiIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 16,
    backgroundColor: '#FFF5E6',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  aiIcon: {
    fontSize: 36,
  },
  progressText: {
    fontSize: 32,
    fontWeight: typography.fontWeight.extrabold,
    color: colors.textPrimary,
  },
  progressStatus: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
  },
  
  // Steps Container Styles
  stepsContainer: {
    marginTop: spacing.lg,
    gap: spacing.md,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: 'transparent',
    position: 'relative',
  },
  stepIconContainer: {
    marginRight: spacing.md,
    marginTop: 2,
  },
  completedIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkmark: {
    fontSize: 16,
    color: colors.textLight,
    fontWeight: typography.fontWeight.bold,
  },
  inProgressIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.surfaceLight,
    borderWidth: 3,
    borderColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  inProgressInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.primary,
  },
  pendingIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.surfaceLight,
    borderWidth: 2,
    borderColor: colors.gray300,
  },
  stepContent: {
    flex: 1,
  },
  stepTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  stepSubtitle: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  stepSubtitleActive: {
    color: colors.primary,
    fontWeight: typography.fontWeight.medium,
  },
  progressBarContainer: {
    height: 6,
    backgroundColor: '#FFF5E6',
    borderRadius: 3,
    marginTop: spacing.sm,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 3,
  },
  timeBadge: {
    position: 'absolute',
    top: spacing.md,
    right: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF5E6',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.md,
    gap: spacing.xs,
  },
  timeBadgeIcon: {
    fontSize: 12,
  },
  timeBadgeText: {
    fontSize: typography.fontSize.xs,
    color: colors.primary,
    fontWeight: typography.fontWeight.medium,
  },
  
  // Fact Card Styles
  factCard: {
    backgroundColor: '#1E293B',
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    marginTop: spacing.xl,
  },
  factHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  factIcon: {
    fontSize: 24,
  },
  factTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    letterSpacing: typography.letterSpacing.wide,
  },
  factText: {
    fontSize: typography.fontSize.sm,
    color: colors.textLight,
    lineHeight: 22,
    opacity: 0.9,
  },
  factIndicator: {
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: spacing.md,
    justifyContent: 'center',
  },
  factDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.whiteOpacity(0.3),
  },
  factDotActive: {
    backgroundColor: colors.primary,
    width: 20,
  },
});

export default AnalysisProgressScreen;
