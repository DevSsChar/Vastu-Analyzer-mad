/**
 * VastuWise AI - Direction Setup Screen
 * Interactive compass for setting North direction
 * Features: Compass dial, rotation control, AI detection, GPS alignment
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
  Platform,
  Alert,
} from 'react-native';
import { ArrowLeft, Info, Compass, Maximize2, RotateCw, Clock, Bot, MapPin } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

interface DirectionSetupScreenProps {
  navigation?: any;
}

const DirectionSetupScreen: React.FC<DirectionSetupScreenProps> = ({ navigation }) => {
  const [rotation, setRotation] = useState(45); // Degrees from North
  const [showInfo, setShowInfo] = useState(true);

  const handleConfirm = () => {
    Alert.alert('Direction Confirmed', `North direction set at ${rotation}° from current orientation`);
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
      <StatusBar barStyle="dark-content" backgroundColor={colors.backgroundLight} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation?.goBack()}
          activeOpacity={0.7}
        >
          <ArrowLeft size={24} color={colors.textPrimary} strokeWidth={2} />
        </TouchableOpacity>
        
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Critical for accurate Vastu analysis</Text>
        </View>
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
                <Info size={18} color={colors.textLight} strokeWidth={2.5} />
              </View>
              <View style={styles.infoContent}>
                <Text style={styles.infoTitle}>Why is this important?</Text>
                <Text style={styles.infoText}>
                  Accurate direction ensures correct Dosha identification and remedy suggestions.
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Compass Container */}
        <View style={styles.compassSection}>
          <View style={styles.gridBackground}>
            {/* Grid lines */}
            {Array.from({ length: 20 }).map((_, i) => (
              <View key={`v-${i}`} style={[styles.gridLineVertical, { left: `${i * 5}%` }]} />
            ))}
            {Array.from({ length: 20 }).map((_, i) => (
              <View key={`h-${i}`} style={[styles.gridLineHorizontal, { top: `${i * 5}%` }]} />
            ))}
          </View>

          {/* Compass Dial */}
          <View style={styles.compassContainer}>
            {/* Outer Ring */}
            <View style={styles.compassOuter}>
              {/* Direction Markers */}
              <View style={[styles.directionMarker, styles.markerNorth]}>
                <View style={styles.markerDot} />
              </View>
              <View style={[styles.directionMarker, styles.markerEast]}>
                <View style={styles.markerDot} />
              </View>
              <View style={[styles.directionMarker, styles.markerSouth]}>
                <View style={styles.markerDot} />
              </View>
              <View style={[styles.directionMarker, styles.markerWest]}>
                <View style={styles.markerDot} />
              </View>
              
              {/* North Arrow Indicator */}
              <View style={[styles.arrowIndicator, { transform: [{ rotate: `${rotation}deg` }] }]}>
                <View style={styles.arrowLine} />
                <View style={styles.arrowHead} />
              </View>
            </View>

            {/* Middle Ring */}
            <View style={styles.compassMiddle} />

            {/* Inner Circle */}
            <View style={styles.compassInner}>
              <View style={styles.compassIconContainer}>
                <Compass size={28} color='#7C3AED' strokeWidth={2} />
              </View>
            </View>
          </View>

          {/* Fullscreen Button */}
          <TouchableOpacity style={styles.fullscreenButton} activeOpacity={0.7}>
            <Maximize2 size={18} color={colors.textSecondary} strokeWidth={2} />
          </TouchableOpacity>
        </View>

        {/* Direction Display */}
        <View style={styles.directionDisplay}>
          <Text style={styles.directionValue}>{displayRotation}° from North</Text>
          <View style={styles.directionSubtext}>
            <RotateCw size={16} color={colors.primary} strokeWidth={2} style={{ marginRight: spacing.xs }} />
            <Text style={styles.rotationText}>
              +{displayRotation}° {isClockwise ? 'clockwise' : 'counter-clockwise'}
            </Text>
          </View>
        </View>

        {/* Confirm Button */}
        <TouchableOpacity
          style={styles.confirmButton}
          onPress={handleConfirm}
          activeOpacity={0.8}
        >
          <Text style={styles.confirmButtonText}>Confirm Direction</Text>
          <View style={styles.confirmIconContainer}>
            <Compass size={14} color={colors.textLight} strokeWidth={2.5} />
          </View>
        </TouchableOpacity>

        {/* Need Help Link */}
        <TouchableOpacity style={styles.helpLink} activeOpacity={0.7}>
          <Text style={styles.helpText}>Need help?</Text>
        </TouchableOpacity>

        {/* Detection Options */}
        <View style={styles.detectionOptions}>
          <TouchableOpacity
            style={styles.detectionButton}
            onPress={handleAIDetection}
            activeOpacity={0.7}
          >
            <Bot size={32} color={colors.primary} strokeWidth={2} />
            <Text style={styles.detectionText}>AI Detection</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.detectionButton}
            onPress={handleGPSAlign}
            activeOpacity={0.7}
          >
            <MapPin size={32} color={colors.primary} strokeWidth={2} />
            <Text style={styles.detectionText}>GPS Align</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
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
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
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
    marginBottom: spacing.xl,
  },
  directionValue: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
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
  
  // Help Link Styles
  helpLink: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  helpText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textDecorationLine: 'underline',
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
