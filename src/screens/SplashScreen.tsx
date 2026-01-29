/**
 * VastuWise AI - Splash Screen
 * Two-phase animated splash with smooth transition
 * Phase 1: Gradient with glowing OM and particles
 * Phase 2: Minimal white background with bordered OM
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  StatusBar,
  Platform,
} from 'react-native';
import { colors, typography } from '../theme';

const { width, height } = Dimensions.get('window');

interface SplashScreenProps {
  onFinish?: () => void;
}

const SplashScreen: React.FC<SplashScreenProps> = ({ onFinish }) => {
  const [phase, setPhase] = useState<1 | 2>(1);
  
  // Animation values
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const omGlowAnim = useRef(new Animated.Value(0)).current;
  const floatAnim = useRef(new Animated.Value(0)).current;
  const spinnerRotate = useRef(new Animated.Value(0)).current;
  const phase2FadeAnim = useRef(new Animated.Value(0)).current;
  const ringScaleAnim = useRef(new Animated.Value(0.8)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Phase 1: Glowing OM animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(omGlowAnim, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        }),
        Animated.timing(omGlowAnim, {
          toValue: 0,
          duration: 2000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Floating animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(floatAnim, {
          toValue: 1,
          duration: 3000,
          useNativeDriver: true,
        }),
        Animated.timing(floatAnim, {
          toValue: 0,
          duration: 3000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Spinner rotation
    Animated.loop(
      Animated.timing(spinnerRotate, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      })
    ).start();

    // Transition to phase 2 after 3 seconds
    const timer = setTimeout(() => {
      // Fade out phase 1
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 0.9,
          duration: 500,
          useNativeDriver: true,
        }),
      ]).start(() => {
        setPhase(2);
        
        // Fade in phase 2
        Animated.parallel([
          Animated.timing(phase2FadeAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.spring(ringScaleAnim, {
            toValue: 1,
            tension: 50,
            friction: 7,
            useNativeDriver: true,
          }),
          Animated.timing(progressAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: false,
          }),
        ]).start();
      });
    }, 3000);

    // Finish after total 5 seconds
    const finishTimer = setTimeout(() => {
      Animated.timing(phase2FadeAnim, {
        toValue: 0,
        duration: 400,
        useNativeDriver: true,
      }).start(() => {
        onFinish?.();
      });
    }, 5000);

    return () => {
      clearTimeout(timer);
      clearTimeout(finishTimer);
    };
  }, []);

  const spinRotation = spinnerRotate.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const floatTranslate = floatAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -20],
  });

  const glowOpacity = omGlowAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.8],
  });

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  if (phase === 1) {
    // Phase 1: Gradient Splash with Glow
    return (
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#d97706" />
        
        {/* Gradient Background */}
        <View style={styles.gradientBackground}>
          {/* Decorative Circles Top Right */}
          <View style={styles.decorCircleTopOuter} />
          <View style={styles.decorCircleTopInner} />
          
          {/* Decorative Circle Bottom Left */}
          <View style={styles.decorCircleBottom} />
          
          {/* Particle Effect Layer */}
          <Animated.View style={[styles.particleLayer, { opacity: glowOpacity }]} />
          
          {/* Main Content */}
          <Animated.View
            style={[
              styles.mainContent,
              {
                opacity: fadeAnim,
                transform: [
                  { scale: scaleAnim },
                  { translateY: floatTranslate },
                ],
              },
            ]}
          >
            {/* OM Symbol with Glow */}
            <View style={styles.omContainer}>
              <Animated.View style={[styles.glowCircle, { opacity: glowOpacity }]} />
              <Text style={styles.omSymbol}>ॐ</Text>
            </View>
            
            {/* Title Section */}
            <View style={styles.titleSection}>
              <Text style={styles.mainTitle}>VastuWise AI</Text>
              <Text style={styles.tagline}>Ancient Wisdom • Modern Living</Text>
            </View>
          </Animated.View>
          
          {/* Bottom Loading Indicator */}
          <Animated.View style={[styles.loadingSection, { opacity: fadeAnim }]}>
            <Animated.View
              style={[
                styles.spinner,
                { transform: [{ rotate: spinRotation }] },
              ]}
            />
            <Text style={styles.loadingText}>Harmonizing Energies...</Text>
          </Animated.View>
        </View>
      </View>
    );
  }

  // Phase 2: Minimal Design
  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.backgroundLight} />
      
      <Animated.View
        style={[
          styles.phase2Container,
          { opacity: phase2FadeAnim },
        ]}
      >
        {/* Decorative Background Circles */}
        <View style={styles.decorCirclePhase2Top} />
        <View style={styles.decorCirclePhase2Bottom} />
        
        {/* Top Spacer */}
        <View style={styles.topSpacer} />
        
        {/* Center Content */}
        <View style={styles.phase2Center}>
          {/* OM in Circle */}
          <Animated.View
            style={[
              styles.omCircleContainer,
              { transform: [{ scale: ringScaleAnim }] },
            ]}
          >
            <View style={styles.outerRing}>
              <Text style={styles.omSymbolPhase2}>ॐ</Text>
            </View>
            {/* Concentric Rings */}
            <View style={styles.ring1} />
            <View style={styles.ring2} />
          </Animated.View>
          
          {/* Title */}
          <View style={styles.phase2TitleSection}>
            <Text style={styles.phase2Title}>VastuWise AI</Text>
          </View>
        </View>
        
        {/* Bottom Section */}
        <View style={styles.phase2Bottom}>
          <Text style={styles.phase2Tagline}>HARMONIZING SPACES WITH AI</Text>
          
          {/* Progress Bar */}
          <View style={styles.progressBarContainer}>
            <Animated.View
              style={[
                styles.progressBar,
                { width: progressWidth },
              ]}
            />
          </View>
          
          {/* Safe Area Spacer */}
          <View style={styles.safeAreaSpacer} />
        </View>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  
  // Phase 1 Styles
  gradientBackground: {
    flex: 1,
    backgroundColor: '#d97706',
    position: 'relative',
  },
  decorCircleTopOuter: {
    position: 'absolute',
    top: -80,
    right: -80,
    width: 320,
    height: 320,
    borderRadius: 160,
    borderWidth: 30,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  decorCircleTopInner: {
    position: 'absolute',
    top: -40,
    right: -40,
    width: 240,
    height: 240,
    borderRadius: 120,
    borderWidth: 15,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  decorCircleBottom: {
    position: 'absolute',
    bottom: -128,
    left: -80,
    width: 384,
    height: 384,
    borderRadius: 192,
    borderWidth: 40,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  particleLayer: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(252, 211, 77, 0.1)',
  },
  mainContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 32,
  },
  omContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  glowCircle: {
    position: 'absolute',
    width: 160,
    height: 160,
    borderRadius: 80,
    backgroundColor: '#fcd34d',
  },
  omSymbol: {
    fontSize: 120,
    lineHeight: 140,
    color: '#fcd34d',
    fontWeight: 'bold',
    textShadowColor: 'rgba(252, 211, 77, 0.8)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 30,
  },
  titleSection: {
    alignItems: 'center',
    gap: 8,
    marginTop: 16,
  },
  mainTitle: {
    fontSize: 40,
    fontWeight: '700',
    color: '#ffffff',
    letterSpacing: 1,
    textShadowColor: 'rgba(0, 0, 0, 0.2)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  tagline: {
    fontSize: 12,
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.8)',
    letterSpacing: 2,
    textTransform: 'uppercase',
    marginTop: 8,
  },
  loadingSection: {
    position: 'absolute',
    bottom: 48,
    alignSelf: 'center',
    alignItems: 'center',
    gap: 16,
  },
  spinner: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 4,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    borderTopColor: '#fcd34d',
  },
  loadingText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.6)',
    letterSpacing: 1.5,
  },
  
  // Phase 2 Styles
  phase2Container: {
    flex: 1,
    backgroundColor: colors.backgroundLight,
    position: 'relative',
  },
  decorCirclePhase2Top: {
    position: 'absolute',
    top: '-20%',
    left: '-20%',
    width: height * 0.7,
    height: height * 0.7,
    borderRadius: height * 0.35,
    borderWidth: 1,
    borderColor: 'rgba(219, 119, 6, 0.05)',
  },
  decorCirclePhase2Bottom: {
    position: 'absolute',
    bottom: '-10%',
    right: '-20%',
    width: height * 0.6,
    height: height * 0.6,
    borderRadius: height * 0.3,
    borderWidth: 1,
    borderColor: 'rgba(219, 119, 6, 0.05)',
  },
  topSpacer: {
    flex: 1,
  },
  phase2Center: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
    zIndex: 10,
  },
  omCircleContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 32,
  },
  outerRing: {
    width: 144,
    height: 144,
    borderRadius: 72,
    borderWidth: 1.5,
    borderColor: colors.primary,
    backgroundColor: colors.backgroundLight,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  omSymbolPhase2: {
    fontSize: 72,
    lineHeight: 80,
    color: colors.primary,
    fontWeight: '300',
    marginBottom: 8,
  },
  ring1: {
    position: 'absolute',
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 1,
    borderColor: 'rgba(219, 119, 6, 0.1)',
  },
  ring2: {
    position: 'absolute',
    width: 176,
    height: 176,
    borderRadius: 88,
    borderWidth: 1,
    borderColor: 'rgba(219, 119, 6, 0.05)',
  },
  phase2TitleSection: {
    alignItems: 'center',
    gap: 4,
  },
  phase2Title: {
    fontSize: 32,
    fontWeight: '800',
    color: '#4A3B32',
    letterSpacing: -0.5,
    textAlign: 'center',
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  phase2Bottom: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingBottom: 40,
    zIndex: 10,
  },
  phase2Tagline: {
    fontSize: 10,
    fontWeight: '600',
    color: '#8c775f',
    letterSpacing: 2,
    textTransform: 'uppercase',
    textAlign: 'center',
    paddingHorizontal: 16,
  },
  progressBarContainer: {
    marginTop: 24,
    height: 4,
    width: 64,
    backgroundColor: 'rgba(219, 119, 6, 0.1)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 2,
  },
  safeAreaSpacer: {
    height: 16,
  },
});

export default SplashScreen;
