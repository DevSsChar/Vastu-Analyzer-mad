/**
 * VastuWise AI - Direction Setup Screen
 * Interactive compass for setting North direction
 * Features: Compass dial, rotation control, AI detection, GPS alignment
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Platform,
  Alert,
  Image as RNImage,
  Animated,
  StatusBar,
} from 'react-native';
import { Magnetometer } from 'expo-sensors';
import { ArrowLeft, Info, Compass, Maximize2, RotateCw, Clock, Bot, MapPin, Navigation } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import BottomNav from '../components/BottomNav';

interface DirectionSetupScreenProps {
  navigation?: any;
  route?: {
    params?: {
      floorPlanImage?: string;
    };
  };
}

const DirectionSetupScreen: React.FC<DirectionSetupScreenProps> = ({ navigation, route }) => {
  const [rotation, setRotation] = useState(45); // Degrees from North
  const [showInfo, setShowInfo] = useState(true);
  const [magnetometerData, setMagnetometerData] = useState({ x: 0, y: 0, z: 0 });
  const [heading, setHeading] = useState(0); // Current compass heading in degrees
  const [direction, setDirection] = useState('N'); // Cardinal direction (N, NE, E, etc.)
  const [subscription, setSubscription] = useState<any>(null);
  const compassRotation = new Animated.Value(0);
  const floorPlanImage = route?.params?.floorPlanImage;

  // Convert degrees to cardinal/intercardinal direction
  const getCardinalDirection = (degrees: number): string => {
    const normalizedDegrees = (degrees + 360) % 360;
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(normalizedDegrees / 45) % 8;
    return directions[index];
  };

  // Calculate heading from magnetometer data
  const calculateHeading = (x: number, y: number): number => {
    let angle = Math.atan2(y, x) * (180 / Math.PI);
    // Normalize to 0-360
    angle = (angle + 360) % 360;
    return angle;
  };

  useEffect(() => {
    // Subscribe to magnetometer updates
    const _subscribe = () => {
      Magnetometer.setUpdateInterval(100); // Update every 100ms
      const sub = Magnetometer.addListener((data) => {
        setMagnetometerData(data);
        const newHeading = calculateHeading(data.x, data.y);
        setHeading(newHeading);
        setDirection(getCardinalDirection(newHeading));
        
        // Smooth rotation animation
        Animated.spring(compassRotation, {
          toValue: -newHeading,
          useNativeDriver: true,
          tension: 10,
          friction: 5,
        }).start();
      });
      setSubscription(sub);
    };

    // Check if magnetometer is available
    Magnetometer.isAvailableAsync().then((result) => {
      if (result) {
        _subscribe();
      } else {
        Alert.alert('Compass Not Available', 'Your device does not support compass functionality.');
      }
    });

    return () => {
      if (subscription) {
        subscription.remove();
      }
    };
  }, []);

  const handleConfirm = () => {
    Alert.alert(
      'Direction Confirmed', 
      `House entrance is facing ${direction} (${Math.round(heading)}°)`,
      [
        {
          text: 'OK',
          onPress: () => {
            // Navigate to Processing screen
            console.log('Entrance Direction:', direction, 'Heading:', heading);
            navigation?.navigate('Processing');
          }
        }
      ]
    );
  };

  const handleAIDetection = () => {
    Alert.alert('AI Detection', 'AI will analyze the floor plan to detect North direction');
  };

  const handleGPSAlign = () => {
    Alert.alert('GPS Align', 'Using device compass to align with magnetic North');
  };

  const isClockwise = rotation >= 0;
  const displayRotation = Math.abs(rotation);

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
        
        <View style={styles.headerContent} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Info Card */}
        {showInfo && (
          <View style={styles.infoCard}>
            <View style={styles.infoHeader}>
              <View style={styles.infoIconContainer}>
                <Navigation size={18} color={colors.textLight} strokeWidth={2.5} />
              </View>
              <View style={styles.infoContent}>
                <Text style={styles.infoTitle}>📍 Instructions</Text>
                <Text style={styles.infoText}>
                  1. Go inside your house{'\n'}
                  2. Stand facing the main entrance{'\n'}
                  3. Hold your phone flat and steady{'\n'}
                  4. The compass will show which direction the entrance faces
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Live Compass Display */}
        <View style={styles.liveCompassCard}>
          <Text style={styles.liveCompassLabel}>You are currently facing:</Text>
          <View style={styles.directionBadge}>
            <Text style={styles.directionBadgeText}>{direction}</Text>
          </View>
          <Text style={styles.liveHeadingText}>{Math.round(heading)}°</Text>
          
          {/* Mini Real-time Compass */}
          <View style={styles.miniCompassContainer}>
            <Animated.View 
              style={[
                styles.miniCompassNeedle,
                { transform: [{ rotate: compassRotation.interpolate({
                    inputRange: [0, 360],
                    outputRange: ['0deg', '360deg']
                  })}]
                }
              ]}
            >
              <View style={styles.needleArrow}>
                <View style={styles.needleNorth} />
                <View style={styles.needleSouth} />
              </View>
            </Animated.View>
            <Text style={styles.miniCompassN}>N</Text>
            <Text style={styles.miniCompassE}>E</Text>
            <Text style={styles.miniCompassS}>S</Text>
            <Text style={styles.miniCompassW}>W</Text>
          </View>
        </View>

        {/* Direction Display */}
        <View style={styles.directionDisplay}>
          <Text style={styles.directionLabel}>House Entrance Facing:</Text>
          <Text style={styles.directionValue}>{direction}</Text>
          <Text style={styles.directionSubValue}>({Math.round(heading)}° from North)</Text>
        </View>

        {/* Confirm Button */}
        <TouchableOpacity
          style={styles.confirmButton}
          onPress={handleConfirm}
          activeOpacity={0.8}
        >
          <Text style={styles.confirmButtonText}>Confirm Entrance Direction</Text>
          <View style={styles.confirmIconContainer}>
            <Navigation size={14} color={colors.textLight} strokeWidth={2.5} />
          </View>
        </TouchableOpacity>

        {/* Help Text */}
        <View style={styles.helpContainer}>
          <Text style={styles.helpText}>
            Make sure you're standing inside the house, facing outward toward the entrance door
          </Text>
        </View>
      </ScrollView>

      {/* Bottom Navigation */}
      <BottomNav navigation={navigation} activeScreen="DirectionSetup" />
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
    marginRight: spacing.sm,
  },
  backIcon: {
    fontSize: 24,
    color: colors.textPrimary,
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  headerSubtitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
    marginTop: 2,
  },
  scrollContent: {
    padding: spacing.md,
  },
  
  // Info Card Styles
  infoCard: {
    backgroundColor: '#F3F0FF',
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: '#E0D7FF',
  },
  infoHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  infoIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#7C3AED',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  infoIcon: {
    fontSize: 18,
    color: colors.textLight,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: '#7C3AED',
    marginBottom: spacing.xs,
  },
  infoText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  
  // Live Compass Card Styles
  liveCompassCard: {
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  liveCompassLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
    marginBottom: spacing.sm,
  },
  directionBadge: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.xs,
  },
  directionBadgeText: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    letterSpacing: 2,
  },
  liveHeadingText: {
    fontSize: typography.fontSize.lg,
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
    marginBottom: spacing.md,
  },
  miniCompassContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#F3F0FF',
    borderWidth: 3,
    borderColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  miniCompassNeedle: {
    width: 100,
    height: 100,
    alignItems: 'center',
    justifyContent: 'center',
  },
  needleArrow: {
    width: 4,
    height: 70,
    alignItems: 'center',
  },
  needleNorth: {
    width: 0,
    height: 0,
    borderLeftWidth: 8,
    borderRightWidth: 8,
    borderBottomWidth: 35,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: '#EF4444',
  },
  needleSouth: {
    width: 0,
    height: 0,
    borderLeftWidth: 8,
    borderRightWidth: 8,
    borderTopWidth: 35,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: '#94A3B8',
  },
  miniCompassN: {
    position: 'absolute',
    top: 8,
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: '#EF4444',
  },
  miniCompassE: {
    position: 'absolute',
    right: 8,
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textSecondary,
  },
  miniCompassS: {
    position: 'absolute',
    bottom: 8,
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textSecondary,
  },
  miniCompassW: {
    position: 'absolute',
    left: 8,
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textSecondary,
  },
  
  // Compass Section Styles
  compassSection: {
    position: 'relative',
    height: 280,
    marginBottom: spacing.xl,
    alignItems: 'center',
    justifyContent: 'center',
  },
  gridBackground: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: '#FAFAFA',
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  },
  floorPlanImage: {
    width: '100%',
    height: '100%',
    opacity: 0.6,
  },
  gridLineVertical: {
    position: 'absolute',
    width: 1,
    height: '100%',
    backgroundColor: '#E5E5E5',
  },
  gridLineHorizontal: {
    position: 'absolute',
    width: '100%',
    height: 1,
    backgroundColor: '#E5E5E5',
  },
  compassContainer: {
    width: 200,
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  compassOuter: {
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: colors.surfaceLight,
    borderWidth: 3,
    borderColor: '#E5E5E5',
    position: 'absolute',
    shadowColor: colors.blackOpacity(0.15),
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  directionMarker: {
    position: 'absolute',
    width: 8,
    height: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  markerDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.gray400,
  },
  markerNorth: {
    top: 4,
    left: '50%',
    marginLeft: -4,
  },
  markerEast: {
    right: 4,
    top: '50%',
    marginTop: -4,
  },
  markerSouth: {
    bottom: 4,
    left: '50%',
    marginLeft: -4,
  },
  markerWest: {
    left: 4,
    top: '50%',
    marginTop: -4,
  },
  arrowIndicator: {
    position: 'absolute',
    top: 20,
    left: '50%',
    marginLeft: -2,
    width: 4,
    height: 80,
    alignItems: 'center',
  },
  arrowLine: {
    width: 3,
    height: 60,
    backgroundColor: '#EF4444',
  },
  arrowHead: {
    width: 0,
    height: 0,
    borderLeftWidth: 6,
    borderRightWidth: 6,
    borderBottomWidth: 12,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: '#EF4444',
    transform: [{ rotate: '180deg' }],
  },
  compassMiddle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: colors.backgroundLight,
    position: 'absolute',
    borderWidth: 2,
    borderColor: '#E5E5E5',
  },
  compassInner: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.surfaceLight,
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#E5E5E5',
    shadowColor: colors.blackOpacity(0.1),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  compassIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: '#F3F0FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  compassIcon: {
    fontSize: 28,
  },
  fullscreenButton: {
    position: 'absolute',
    bottom: 10,
    right: 10,
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  fullscreenIcon: {
    fontSize: 18,
    color: colors.textSecondary,
  },
  
  // Direction Display Styles
  directionDisplay: {
    alignItems: 'center',
    marginBottom: spacing.lg,
    backgroundColor: '#F3F0FF',
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: '#E0D7FF',
  },
  directionLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
    marginBottom: spacing.xs,
  },
  directionValue: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  directionSubValue: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  directionSubtext: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  rotationIcon: {
    fontSize: 16,
  },
  rotationText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: typography.fontWeight.medium,
  },
  
  // Confirm Button Styles
  confirmButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  confirmButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    marginRight: spacing.sm,
  },
  confirmIconContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.whiteOpacity(0.2),
    alignItems: 'center',
    justifyContent: 'center',
  },
  confirmIcon: {
    fontSize: 14,
  },
  
  // Help Container Styles
  helpContainer: {
    backgroundColor: '#FFF7ED',
    padding: spacing.md,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: '#FED7AA',
    marginBottom: spacing.lg,
  },
  helpText: {
    fontSize: typography.fontSize.sm,
    color: '#9A3412',
    textAlign: 'center',
    lineHeight: 20,
  },
  
  // Help Link Styles (kept for compatibility)
  helpLink: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  
  // Detection Options Styles
  detectionOptions: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: spacing.xl,
  },
  detectionButton: {
    alignItems: 'center',
    gap: spacing.xs,
  },
  detectionIcon: {
    fontSize: 32,
  },
  detectionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.medium,
  },
});

export default DirectionSetupScreen;
