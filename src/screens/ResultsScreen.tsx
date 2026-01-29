/**
 * VastuWise AI - Results Screen
 * Displays Vastu analysis results with score and zone analysis
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
} from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import {
  ArrowLeft,
  MoreHorizontal,
  Droplet,
  Flame,
  Mountain,
  AlertCircle,
  CheckCircle,
  Check,
  Share2,
  Download,
  ArrowRight,
} from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import BottomNav from '../components/BottomNav';

interface ResultsScreenProps {
  navigation?: any;
}

interface ZoneData {
  id: string;
  name: string;
  direction: string;
  icon: string;
  iconBg: string;
  iconColor: string;
  status: 'excellent' | 'good' | 'attention';
  statusLabel: string;
  statusBg: string;
  statusColor: string;
  description: string;
}

interface IssueData {
  id: string;
  title: string;
  description: string;
}

const ResultsScreen: React.FC<ResultsScreenProps> = ({ navigation }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'issues'>('overview');
  const score = 78;
  const maxScore = 100;

  // Calculate circle progress
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / maxScore) * circumference;
  const strokeDashoffset = circumference - progress;

  const zones: ZoneData[] = [
    {
      id: '1',
      name: 'Northeast',
      direction: '(Ishaanya)',
      icon: 'water',
      iconBg: '#DBEAFE',
      iconColor: '#2563EB',
      status: 'excellent',
      statusLabel: 'Excellent',
      statusBg: '#D1FAE5',
      statusColor: '#059669',
      description: 'Water element is perfectly placed. This brings prosperity and clarity of mind.',
    },
    {
      id: '2',
      name: 'Southeast',
      direction: '(Agneya)',
      icon: 'fire',
      iconBg: '#FED7AA',
      iconColor: '#db7706',
      status: 'attention',
      statusLabel: 'Needs Attention',
      statusBg: '#FFF8E7',
      statusColor: '#db7706',
      description: 'Fire element is weak. Kitchen placement here is recommended to boost energy.',
    },
    {
      id: '3',
      name: 'Southwest',
      direction: '(Nairutya)',
      icon: 'earth',
      iconBg: '#FEF3C7',
      iconColor: '#B45309',
      status: 'good',
      statusLabel: 'Good',
      statusBg: '#ECFDF5',
      statusColor: '#059669',
      description: 'Earth element stability is good. Ideal for master bedroom.',
    },
  ];

  const issues: IssueData[] = [
    {
      id: '1',
      title: 'Toilet in Northeast',
      description: 'This is a major defect blocking positive energy flow.',
    },
  ];

  const renderIcon = (iconType: string, color: string) => {
    switch (iconType) {
      case 'water':
        return <Droplet size={24} color={color} fill={color} />;
      case 'fire':
        return <Flame size={24} color={color} fill={color} />;
      case 'earth':
        return <Mountain size={24} color={color} fill={color} />;
      default:
        return <AlertCircle size={24} color={color} />;
    }
  };

  const renderStatusIcon = (status: string, color: string) => {
    if (status === 'excellent') {
      return <CheckCircle size={14} color={color} fill={color} />;
    } else if (status === 'attention') {
      return <AlertCircle size={14} color={color} fill={color} />;
    } else {
      return <Check size={14} color={color} />;
    }
  };

  const handleBack = () => {
    navigation?.goBack();
  };

  const handleShare = () => {
    Alert.alert('Share', 'Share analysis report');
  };

  const handleSaveReport = () => {
    Alert.alert('Save Report', 'Report saved successfully');
  };

  const handleViewRemediation = (issue: IssueData) => {
    Alert.alert('Remediation', `View remediation for: ${issue.title}`);
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      {/* <View style={styles.header}>
        <TouchableOpacity
          style={styles.headerButton}
          onPress={handleBack}
          activeOpacity={0.7}
        >
          <ArrowLeft size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View> */}

      {/* Main Content */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Score Header Section */}
        <View style={styles.scoreSection}>
          <View style={styles.scoreContainer}>
            {/* Progress Ring */}
            <View style={styles.progressRing}>
              <Svg width={160} height={160} viewBox="0 0 100 100">
                {/* Background Circle */}
                <Circle
                  cx="50"
                  cy="50"
                  r={radius}
                  stroke="rgba(255, 255, 255, 0.2)"
                  strokeWidth="8"
                  fill="transparent"
                />
                {/* Progress Circle */}
                <Circle
                  cx="50"
                  cy="50"
                  r={radius}
                  stroke="#FFFFFF"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
              </Svg>
              <View style={styles.scoreTextContainer}>
                <Text style={styles.scoreValue}>{score}</Text>
                <Text style={styles.scoreMax}>out of {maxScore}</Text>
              </View>
            </View>

            <Text style={styles.scoreTitle}>Good Vastu Balance</Text>
            <Text style={styles.scoreDescription}>
              Your space has strong positive energy in the Northeast, but requires attention in the Fire zone.
            </Text>
          </View>
        </View>

        {/* Tabs */}
        <View style={styles.tabsContainer}>
          <View style={styles.tabs}>
            <TouchableOpacity
              style={[styles.tab, activeTab === 'overview' && styles.tabActive]}
              onPress={() => setActiveTab('overview')}
              activeOpacity={0.8}
            >
              <Text style={[styles.tabText, activeTab === 'overview' && styles.tabTextActive]}>
                Overview
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.tab, activeTab === 'issues' && styles.tabActive]}
              onPress={() => setActiveTab('issues')}
              activeOpacity={0.8}
            >
              <Text style={[styles.tabText, activeTab === 'issues' && styles.tabTextActive]}>
                Issues
                {issues.length > 0 && (
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>{issues.length}</Text>
                  </View>
                )}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Content */}
        <View style={styles.content}>
          {activeTab === 'overview' ? (
            <>
              <Text style={styles.sectionTitle}>Zone Analysis</Text>

              {zones.map((zone) => (
                <View
                  key={zone.id}
                  style={[
                    styles.zoneCard,
                    zone.status === 'attention' && styles.zoneCardHighlight,
                  ]}
                >
                  <View style={[styles.zoneIcon, { backgroundColor: zone.iconBg }]}>
                    {renderIcon(zone.icon, zone.iconColor)}
                  </View>

                  <View style={styles.zoneContent}>
                    <View style={styles.zoneHeader}>
                      <Text style={styles.zoneName} numberOfLines={1}>
                        {zone.name} <Text style={styles.zoneDirection}>{zone.direction}</Text>
                      </Text>
                      <View style={[styles.statusBadge, { backgroundColor: zone.statusBg }]}>
                        {renderStatusIcon(zone.status, zone.statusColor)}
                        <Text style={[styles.statusText, { color: zone.statusColor }]}>
                          {zone.statusLabel}
                        </Text>
                      </View>
                    </View>
                    <Text style={styles.zoneDescription}>{zone.description}</Text>
                  </View>
                </View>
              ))}
            </>
          ) : (
            <>
              <Text style={styles.sectionTitle}>Critical Issues Found</Text>

              {issues.map((issue) => (
                <View key={issue.id} style={styles.issueCard}>
                  <View style={styles.issueHeader}>
                    <View style={styles.issueIcon}>
                      <AlertCircle size={24} color="#DC2626" />
                    </View>
                    <View style={styles.issueContent}>
                      <Text style={styles.issueTitle}>{issue.title}</Text>
                      <Text style={styles.issueDescription}>{issue.description}</Text>
                    </View>
                  </View>
                  <TouchableOpacity
                    style={styles.remediationButton}
                    onPress={() => handleViewRemediation(issue)}
                    activeOpacity={0.7}
                  >
                    <Text style={styles.remediationText}>View Remediation</Text>
                    <ArrowRight size={16} color="#DC2626" />
                  </TouchableOpacity>
                </View>
              ))}
            </>
          )}
        </View>
      </ScrollView>

      {/* Action Buttons */}
      <View style={styles.actionBar}>
        <TouchableOpacity
          style={styles.saveButton}
          onPress={handleSaveReport}
          activeOpacity={0.8}
        >
          <Download size={18} color={colors.textPrimary} />
          <Text style={styles.saveButtonText}>Save Report</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.shareButton}
          onPress={handleShare}
          activeOpacity={0.8}
        >
          <Share2 size={18} color={colors.textLight} />
          <Text style={styles.shareButtonText}>Share</Text>
        </TouchableOpacity>
      </View>

      {/* Bottom Navigation */}
      <BottomNav navigation={navigation} activeScreen="Results" />
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
    paddingVertical: spacing.sm,
    backgroundColor: colors.surfaceLight,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
    shadowColor: colors.blackOpacity(0.05),
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 2,
    elevation: 2,
  },
  headerButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 160,
  },
  scoreSection: {
    backgroundColor: colors.primary,
    paddingTop: spacing.lg,
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.md,
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  scoreContainer: {
    alignItems: 'center',
  },
  progressRing: {
    width: 160,
    height: 160,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  scoreTextContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
  scoreValue: {
    fontSize: 40,
    fontWeight: typography.fontWeight.extrabold,
    color: colors.textLight,
    lineHeight: 48,
  },
  scoreMax: {
    fontSize: typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: typography.fontWeight.medium,
  },
  scoreTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  scoreDescription: {
    fontSize: typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    maxWidth: 300,
    lineHeight: 20,
  },
  tabsContainer: {
    paddingHorizontal: spacing.md,
    marginTop: -spacing.lg,
    zIndex: 10,
  },
  tabs: {
    flexDirection: 'row',
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.xl,
    padding: 6,
    shadowColor: colors.blackOpacity(0.1),
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 4,
    elevation: 4,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabActive: {
    backgroundColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    elevation: 2,
  },
  tabText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
  },
  tabTextActive: {
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },
  badge: {
    marginLeft: spacing.xs,
    backgroundColor: '#FEE2E2',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 999,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: typography.fontWeight.bold,
    color: '#DC2626',
  },
  content: {
    padding: spacing.md,
    gap: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  zoneCard: {
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    flexDirection: 'row',
    gap: spacing.md,
    shadowColor: colors.blackOpacity(0.05),
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 2,
    elevation: 1,
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  zoneCardHighlight: {
    borderColor: colors.primaryOpacity(0.1),
    shadowColor: colors.primary,
    shadowOpacity: 0.1,
  },
  zoneIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  zoneContent: {
    flex: 1,
    gap: spacing.xs,
  },
  zoneHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  zoneName: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    flex: 1,
  },
  zoneDirection: {
    fontWeight: '400' as any,
    color: colors.textSecondary,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 999,
  },
  statusText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold,
  },
  zoneDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  issueCard: {
    backgroundColor: '#FEF2F2',
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    gap: spacing.sm,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  issueHeader: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  issueIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FEE2E2',
    alignItems: 'center',
    justifyContent: 'center',
  },
  issueContent: {
    flex: 1,
    gap: spacing.xs,
  },
  issueTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  issueDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  remediationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingTop: spacing.xs,
  },
  remediationText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: '#DC2626',
  },
  actionBar: {
    backgroundColor: colors.surfaceLight,
    borderTopWidth: 1,
    borderTopColor: colors.gray100,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    flexDirection: 'row',
    gap: spacing.md,
  },
  saveButton: {
    flex: 1,
    height: 48,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    borderRadius: borderRadius.xl,
    borderWidth: 2,
    borderColor: colors.gray200,
    backgroundColor: colors.surfaceLight,
  },
  saveButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  shareButton: {
    flex: 1,
    height: 48,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    borderRadius: borderRadius.xl,
    backgroundColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  shareButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },
});

export default ResultsScreen;
