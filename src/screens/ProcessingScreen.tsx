/**
 * VastuWise AI - Processing Screen
 * AI Analysis processing with progress tracking and Vastu facts
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Easing,
  SafeAreaView,
} from 'react-native';
import {
  ArrowLeft,
  HelpCircle,
  Settings,
  Check,
  Circle,
  Loader,
  Lightbulb,
  Bell,
} from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import BottomNav from '../components/BottomNav';

interface ProcessingScreenProps {
  navigation?: any;
}

interface ProcessingStep {
  id: string;
  label: string;
  status: 'completed' | 'active' | 'pending';
}

const VASTU_FACTS = [
  {
    title: "DID YOU KNOW?",
    fact: "The North-East corner is known as the Ishan Kon and represents the water element. It is ideal for meditation spaces."
  },
  {
    title: "DID YOU KNOW?",
    fact: "The kitchen should ideally be in the Southeast (Agneya) corner, governed by the fire element for positive energy flow."
  },
];

const ProcessingScreen: React.FC<ProcessingScreenProps> = ({ navigation }) => {
  const [progress] = useState(75);
  const [currentFact] = useState(() => VASTU_FACTS[Math.floor(Math.random() * VASTU_FACTS.length)]);
  const spinValue = useRef(new Animated.Value(0)).current;
  const pulseValue = useRef(new Animated.Value(1)).current;

  const steps: ProcessingStep[] = [
    { id: '1', label: 'Floor plan uploaded', status: 'completed' },
    { id: '2', label: 'Boundaries detected', status: 'completed' },
    { id: '3', label: 'Analyzing Vastu zones', status: 'active' },
    { id: '4', label: 'Calculating scores', status: 'pending' },
    { id: '5', label: 'Generating remedies', status: 'pending' },
  ];

  useEffect(() => {
    // Spinning animation
    Animated.loop(
      Animated.timing(spinValue, {
        toValue: 1,
        duration: 3000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    ).start();

    // Pulse animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseValue, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const spin = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const handleBack = () => {
    navigation?.goBack();
  };

  const handleHelp = () => {
    console.log('Help');
  };

  const handleNotify = () => {
    console.log('Notify me when ready');
  };

  // Simulate processing completion and navigate to Results
  useEffect(() => {
    const timer = setTimeout(() => {
      navigation?.navigate('Results');
    }, 8000); // Navigate after 8 seconds

    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={handleBack}
          activeOpacity={0.7}
        >
          <ArrowLeft size={24} color={colors.textPrimary} strokeWidth={2} />
        </TouchableOpacity>
        
        <TouchableOpacity
          onPress={handleHelp}
          activeOpacity={0.7}
        >
          <Text style={styles.helpText}>Help</Text>
        </TouchableOpacity>
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        {/* Spinner Section */}
        <View style={styles.spinnerSection}>
          <View style={styles.spinnerContainer}>
            <Animated.View
              style={[
                styles.glowRing,
                {
                  transform: [{ scale: pulseValue }],
                },
              ]}
            />
            <Animated.View
              style={{
                transform: [{ rotate: spin }],
              }}
            >
              <Settings size={72} color={colors.primary} strokeWidth={1.5} />
            </Animated.View>
          </View>

          <Text style={styles.title}>Analyzing Your Space</Text>
          <Text style={styles.subtitle}>
            Please wait while our AI connects with ancient wisdom to map your energy flow.
          </Text>
        </View>

        {/* Progress Bar */}
        <View style={styles.progressSection}>
          <View style={styles.progressHeader}>
            <Text style={styles.progressLabel}>Processing Analysis</Text>
            <Text style={styles.progressPercent}>{progress}%</Text>
          </View>
          <View style={styles.progressBarBackground}>
            <View style={[styles.progressBarFill, { width: `${progress}%` }]} />
          </View>
        </View>

        {/* Steps Checklist */}
        <View style={styles.stepsContainer}>
          {steps.map((step) => (
            <View key={step.id} style={styles.stepItem}>
              <View style={styles.stepIconContainer}>
                {step.status === 'completed' && (
                  <View style={styles.stepCompleted}>
                    <Check size={14} color="#059669" strokeWidth={3} />
                  </View>
                )}
                {step.status === 'active' && (
                  <View style={styles.stepActive}>
                    <Animated.View
                      style={[
                        styles.stepActivePulse,
                        {
                          transform: [{ scale: pulseValue }],
                        },
                      ]}
                    />
                    <Loader size={18} color={colors.primary} strokeWidth={2.5} />
                  </View>
                )}
                {step.status === 'pending' && (
                  <Circle size={18} color="#9CA3AF" strokeWidth={2} />
                )}
              </View>
              <Text
                style={[
                  styles.stepLabel,
                  step.status === 'completed' && styles.stepLabelCompleted,
                  step.status === 'active' && styles.stepLabelActive,
                  step.status === 'pending' && styles.stepLabelPending,
                ]}
              >
                {step.label}
              </Text>
            </View>
          ))}
        </View>

        {/* Fact Card */}
        <View style={styles.factCard}>
          <View style={styles.factBackground}>
            <Lightbulb size={80} color="#FCD34D" strokeWidth={1} opacity={0.15} />
          </View>
          <View style={styles.factContent}>
            <View style={styles.factIcon}>
              <Lightbulb size={20} color={colors.primary} strokeWidth={2} />
            </View>
            <View style={styles.factText}>
              <Text style={styles.factTitle}>{currentFact.title}</Text>
              <Text style={styles.factDescription}>{currentFact.fact}</Text>
            </View>
          </View>
        </View>

        {/* Notify Button */}
        <TouchableOpacity
          style={styles.notifyButton}
          onPress={handleNotify}
          activeOpacity={0.7}
        >
          <Bell size={16} color={colors.textSecondary} strokeWidth={2} />
          <Text style={styles.notifyText}>Notify me when ready</Text>
        </TouchableOpacity>
      </View>

      {/* Bottom Navigation */}
      <BottomNav navigation={navigation} activeScreen="Processing" />
    </SafeAreaView>
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
    paddingVertical: spacing.sm,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  helpText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textSecondary,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    paddingBottom: spacing.md,
  },
  
  // Spinner Section
  spinnerSection: {
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  spinnerContainer: {
    position: 'relative',
    width: 96,
    height: 96,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  glowRing: {
    position: 'absolute',
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: colors.primaryOpacity(0.15),
  },
  title: {
    fontSize: typography.fontSize['xl'],
    fontWeight: typography.fontWeight.extrabold,
    color: colors.textPrimary,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 16,
    maxWidth: 240,
  },

  // Progress Section
  progressSection: {
    marginBottom: spacing.md,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  progressLabel: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  progressPercent: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
  },
  progressBarBackground: {
    height: 10,
    backgroundColor: '#E6E1DB',
    borderRadius: borderRadius.full,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: borderRadius.full,
  },

  // Steps
  stepsContainer: {
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  stepIconContainer: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepCompleted: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#D1FAE5',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepActive: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepActivePulse: {
    position: 'absolute',
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primaryOpacity(0.2),
  },
  stepLabel: {
    fontSize: typography.fontSize.sm,
    flex: 1,
  },
  stepLabelCompleted: {
    color: colors.textSecondary,
    textDecorationLine: 'line-through',
    fontWeight: typography.fontWeight.medium,
  },
  stepLabelActive: {
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.bold,
    fontSize: typography.fontSize.base,
  },
  stepLabelPending: {
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
  },

  // Fact Card
  factCard: {
    position: 'relative',
    backgroundColor: '#FFF8E7',
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: '#FDE68A',
    overflow: 'hidden',
    marginBottom: spacing.md,
  },
  factBackground: {
    position: 'absolute',
    right: -20,
    top: -20,
    transform: [{ rotate: '12deg' }],
  },
  factContent: {
    flexDirection: 'row',
    gap: spacing.sm,
    zIndex: 10,
  },
  factIcon: {
    paddingTop: 2,
  },
  factText: {
    flex: 1,
    gap: spacing.xs,
  },
  factTitle: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
    letterSpacing: 1,
  },
  factDescription: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.medium,
    color: '#5C4A35',
    lineHeight: 16,
  },

  // Notify Button
  notifyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.lg,
    alignSelf: 'center',
  },
  notifyText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textSecondary,
  },
});

export default ProcessingScreen;
