/**
 * VastuWise AI - Analyze Plan Screen
 * Upload floor plan for Vastu analysis
 * Features: File upload, Camera/Gallery integration, Pro tips
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Platform,
  Alert,
  Image as RNImage,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { ArrowLeft, HelpCircle, Lightbulb, X, Cloud, Camera, Image, Ruler, Play } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import BottomNav from '../components/BottomNav';

interface AnalyzePlanScreenProps {
  navigation?: any;
}

const PRO_TIPS = [
  "Ensure the North direction is clearly marked on your plan for the most accurate directional analysis.",
  "A well-lit entrance in the East or North direction invites positive energy and prosperity into your home.",
  "Keep the Brahmasthan (center of the house) open and free from heavy furniture for optimal energy flow.",
  "Place your kitchen in the Southeast corner (Agneya) to harness the fire element's positive energy.",
  "Avoid placing mirrors directly opposite to beds or main doors as they can deflect positive energy.",
  "Water elements like fountains work best in the North or Northeast to attract wealth and abundance.",
  "Bedrooms in the Southwest direction provide stability and restful sleep according to Vastu principles.",
  "Ensure your main door opens clockwise and is larger than other doors for maximum positive energy intake.",
];

const AnalyzePlanScreen: React.FC<AnalyzePlanScreenProps> = ({ navigation }) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showTip, setShowTip] = useState(true);
  const [currentTip] = useState(() => PRO_TIPS[Math.floor(Math.random() * PRO_TIPS.length)]);
  const [isUploading, setIsUploading] = useState(false);

  const requestPermissions = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Please grant camera roll permissions to upload images.');
      return false;
    }
    return true;
  };

  const requestCameraPermissions = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Please grant camera permissions to take photos.');
      return false;
    }
    return true;
  };

  const handleImageSelected = (imageUri: string) => {
    setSelectedImage(imageUri);
    // Navigate to DirectionSetup with the selected image
    setTimeout(() => {
      navigation?.navigate('DirectionSetup', { floorPlanImage: imageUri });
    }, 300);
  };

  const handleBrowseFiles = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    try {
      setIsUploading(true);
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 1,
      });

      if (!result.canceled && result.assets[0]) {
        handleImageSelected(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleCamera = async () => {
    const hasPermission = await requestCameraPermissions();
    if (!hasPermission) return;

    try {
      setIsUploading(true);
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: false,
        quality: 1,
      });

      if (!result.canceled && result.assets[0]) {
        handleImageSelected(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleGallery = async () => {
    await handleBrowseFiles();
  };

  const handleContinue = () => {
    if (selectedImage) {
      navigation?.navigate('DirectionSetup', { floorPlanImage: selectedImage });
    } else {
      Alert.alert('No Image', 'Please upload a floor plan image first.');
    }
  };

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
        
        <TouchableOpacity
          style={styles.helpButton}
          onPress={() => Alert.alert('Help', 'Help information')}
          activeOpacity={0.7}
        >
          <HelpCircle size={20} color={colors.textLight} strokeWidth={2.5} />
        </TouchableOpacity>
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Pro Tip Card */}
        {showTip && (
          <View style={styles.tipCard}>
            <View style={styles.tipHeader}>
              <Lightbulb size={20} color={colors.primary} strokeWidth={2} style={{ marginRight: spacing.xs }} />
              <Text style={styles.tipTitle}>VastuPro Tip</Text>
              <TouchableOpacity
                style={styles.tipClose}
                onPress={() => setShowTip(false)}
                activeOpacity={0.7}
              >
                <X size={20} color={colors.textSecondary} strokeWidth={2} />
              </TouchableOpacity>
            </View>
            <Text style={styles.tipText}>
              <Text style={styles.tipBold}>{currentTip}</Text>
            </Text>
          </View>
        )}

        {/* Upload Section */}
        <View style={styles.uploadCard}>
          {selectedImage ? (
            <View style={styles.imagePreviewContainer}>
              <RNImage
                source={{ uri: selectedImage }}
                style={styles.previewImage}
                resizeMode="contain"
              />
              <TouchableOpacity
                style={styles.changeImageButton}
                onPress={handleBrowseFiles}
                activeOpacity={0.8}
              >
                <Text style={styles.changeImageText}>Change Image</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <View style={styles.uploadIconContainer}>
                <View style={styles.uploadIconCircle}>
                  {isUploading ? (
                    <ActivityIndicator size="large" color={colors.primary} />
                  ) : (
                    <Cloud size={40} color={colors.primary} strokeWidth={2} />
                  )}
                </View>
              </View>
              
              <Text style={styles.uploadTitle}>Upload Your Floor Plan</Text>
          <Text style={styles.uploadDescription}>
            Our AI will analyze its directional zones according to Vastu Shastra principles.
          </Text>

          {/* Browse Files Button */}
          <TouchableOpacity
            style={styles.browseButton}
            onPress={handleBrowseFiles}
            activeOpacity={0.8}
          >
            {/* <Text style={styles.browseIcon}>📁</Text> */}
            <Text style={styles.browseText}>Upload Image</Text>
          </TouchableOpacity>

          {/* Upload Options */}
          <View style={styles.uploadOptions}>
            <TouchableOpacity
              style={styles.optionButton}
              onPress={handleCamera}
              activeOpacity={0.7}
            >
              <View style={styles.optionIconContainer}>
                <Camera size={24} color={colors.primary} strokeWidth={2} />
              </View>
              <Text style={styles.optionText}>Camera</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.optionButton}
              onPress={handleGallery}
              activeOpacity={0.7}
            >
              <View style={styles.optionIconContainer}>
                <Image size={24} color={colors.primary} strokeWidth={2} />
              </View>
              <Text style={styles.optionText}>Gallery</Text>
            </TouchableOpacity>

            {/* <TouchableOpacity
              style={styles.optionButton}
              onPress={handleFiles}
              activeOpacity={0.7}
            >
              <View style={styles.optionIconContainer}>
                <Text style={styles.optionIcon}>📂</Text>
              </View>
              <Text style={styles.optionText}>Files</Text>
            </TouchableOpacity> */}
          </View>

              {/* Supported Formats */}
              <View style={styles.formatsContainer}>
                <Lightbulb size={14} color={colors.primary} strokeWidth={2} style={{ marginRight: spacing.xs }} />
                <Text style={styles.formatsText}>Supported formats: PNG, JPG, PDF</Text>
              </View>
            </>
          )}
        </View>

        {/* Best Results Section */}
        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>How to get the best results</Text>
          
          {/* Continue Button */}
          {selectedImage && (
            <TouchableOpacity
              style={styles.continueButtonPrimary}
              onPress={handleContinue}
              activeOpacity={0.8}
            >
              <Text style={styles.continueButtonPrimaryText}>Continue to Direction Setup</Text>
              <Play size={16} color={colors.textLight} strokeWidth={2} style={{ marginLeft: spacing.sm }} />
            </TouchableOpacity>
          )}

          {/* Tips List */}
          <View style={styles.tipsList}>
            <View style={styles.tipItem}>
              <Lightbulb size={20} color={colors.primary} strokeWidth={2} style={{ marginTop: 2 }} />
              <View style={styles.tipItemContent}>
                <Text style={styles.tipItemTitle}>Include room labels</Text>
                <Text style={styles.tipItemText}>Kitchen, Master bedroom, Entrance, etc.</Text>
              </View>
            </View>

            <View style={styles.tipItem}>
              <Ruler size={20} color={colors.primary} strokeWidth={2} style={{ marginTop: 2 }} />
              <View style={styles.tipItemContent}>
                <Text style={styles.tipItemTitle}>Capture entire boundary</Text>
                <Text style={styles.tipItemText}>The complete shape of the plot is crucial</Text>
              </View>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* Bottom Navigation */}
      <BottomNav navigation={navigation} activeScreen="AnalyzePlan" />
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
  helpButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.textPrimary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerSpacer: {
    flex: 1,
  },
  helpIcon: {
    fontSize: 20,
    color: colors.textLight,
    fontWeight: typography.fontWeight.bold,
  },
  scrollContent: {
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.xl,
  },
  
  // Tip Card Styles
  tipCard: {
    backgroundColor: '#FFF8E7',
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: '#FFE8B3',
  },
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  tipIcon: {
    fontSize: 20,
    marginRight: spacing.xs,
  },
  tipTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textPrimary,
    flex: 1,
  },
  tipClose: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tipCloseText: {
    fontSize: 24,
    color: colors.textSecondary,
    lineHeight: 24,
  },
  tipText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  tipBold: {
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  
  // Upload Card Styles
  uploadCard: {
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    marginBottom: spacing.lg,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.primary,
    borderStyle: 'dashed',
  },
  uploadIconContainer: {
    marginBottom: spacing.md,
  },
  uploadIconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF5E6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadIcon: {
    fontSize: 40,
  },
  uploadTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    textAlign: 'center',
  },
  uploadDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: spacing.lg,
    paddingHorizontal: spacing.md,
  },
  imagePreviewContainer: {
    width: '100%',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  previewImage: {
    width: '100%',
    height: 200,
    borderRadius: borderRadius.md,
    marginBottom: spacing.md,
    backgroundColor: colors.gray100,
  },
  changeImageButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  changeImageText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textLight,
  },
  browseButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.accentLight,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.lg,
  },
  browseIcon: {
    fontSize: 18,
    marginRight: spacing.xs,
  },
  browseText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.primaryDark,
  },
  
  // Upload Options Styles
  uploadOptions: {
    flexDirection: 'row',
    gap: spacing.lg,
    marginBottom: spacing.md,
  },
  optionButton: {
    alignItems: 'center',
    gap: spacing.xs,
  },
  optionIconContainer: {
    width: 56,
    height: 56,
    borderRadius: borderRadius.md,
    backgroundColor: colors.backgroundLight,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  optionIcon: {
    fontSize: 24,
  },
  optionText: {
    fontSize: typography.fontSize.xs,
    color: colors.primaryDark,
    fontWeight: typography.fontWeight.medium,
  },
  
  // Formats Styles
  formatsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  formatsIcon: {
    fontSize: 14,
  },
  formatsText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  
  // Tips Section Styles
  tipsSection: {
    marginBottom: spacing.lg,
  },
  tipsTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  continueButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.md,
  },
  continueButtonPrimary: {
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
  continueButtonPrimaryText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },
  continueIcon: {
    fontSize: 16,
    color: colors.textSecondary,
    marginRight: spacing.sm,
  },
  continueText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
  },
  tipsList: {
    gap: spacing.md,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  tipItemIcon: {
    fontSize: 20,
    marginTop: 2,
  },
  tipItemContent: {
    flex: 1,
  },
  tipItemTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
    color: colors.textPrimary,
    marginBottom: 2,
  },
  tipItemText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    lineHeight: 16,
  },
});

export default AnalyzePlanScreen;
