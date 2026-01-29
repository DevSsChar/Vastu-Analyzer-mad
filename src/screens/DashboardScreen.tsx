/**
 * VastuWise AI - Dashboard Screen
 * Main dashboard with quick actions, recent analyses, and tips
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  SafeAreaView,
  Animated,
  Platform,
  StatusBar,
} from 'react-native';
import {
  Menu,
  Bell,
  Plus,
  MapPin,
  Lightbulb,
  Compass,
  Home as HomeIcon,
  Camera,
  BookOpen,
  User,
} from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import CustomDrawer from '../components/CustomDrawer';
import BottomNav from '../components/BottomNav';
import { getUserData } from '../services/storage.service';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface RecentAnalysis {
  id: string;
  title: string;
  location: string;
  date: string;
  score: number;
  scoreType: 'good' | 'warning';
  image: any;
}

const DashboardScreen: React.FC<any> = ({ navigation }) => {
  const [userName, setUserName] = useState('User');
  const [drawerVisible, setDrawerVisible] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await getUserData();
      if (userData && userData.name) {
        setUserName(userData.name);
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const recentAnalyses: RecentAnalysis[] = [
    {
      id: '1',
      title: 'Home Analysis',
      location: 'NE Corner • Today',
      date: 'Today',
      score: 82,
      scoreType: 'good',
      image: null,
    },
    {
      id: '2',
      title: 'Office Space',
      location: 'E Direction • Yesterday',
      date: 'Yesterday',
      score: 75,
      scoreType: 'warning',
      image: null,
    },
  ];

  const handleMenuPress = () => {
    setDrawerVisible(true);
  };

  const handleNotifications = () => {
    console.log('Notifications');
  };

  const handleNewAnalysis = () => {
    navigation.navigate('AnalyzePlan');
  };

  const handleDirectionCheck = () => {
    navigation.navigate('DirectionSetup');
  };

  const handleRecentAnalysis = (analysis: RecentAnalysis) => {
    console.log('View analysis:', analysis.id);
  };

  const handleNavigation = (screen: string) => {
    if (screen === 'Learn') {
      console.log('Learn section coming soon');
    } else {
      navigation.navigate(screen);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Custom Drawer */}
      <CustomDrawer
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        navigation={navigation}
      />

      {/* Top App Bar */}
      <View style={styles.appBar}>
        <TouchableOpacity
          style={styles.iconButton}
          onPress={handleMenuPress}
          activeOpacity={0.7}
        >
          <Menu size={24} color={colors.textPrimary} strokeWidth={2} />
        </TouchableOpacity>

        <View style={styles.appBarCenter} />

        <View style={styles.appBarRight}>
          <TouchableOpacity
            style={styles.iconButton}
            onPress={handleNotifications}
            activeOpacity={0.7}
          >
            <Bell size={24} color={colors.textPrimary} strokeWidth={2} />
            <View style={styles.notificationBadge} />
          </TouchableOpacity>

          <View style={styles.profileAvatar}>
            <Text style={styles.profileInitial}>
              {userName.charAt(0).toUpperCase()}
            </Text>
          </View>
        </View>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Hero Card with Gradient - Logo Version */}
        <View style={styles.heroCard}>
          {/* Decorative background elements */}
          <View style={[styles.decorBg, styles.decorBg1]} />
          <View style={[styles.decorBg, styles.decorBg2]} />

          <View style={styles.heroContent}>
            <View style={styles.heroLogoContainer}>
              {/* <View style={styles.heroLogoIcon}>
                <Plus size={24} color={colors.textLight} strokeWidth={2.5} />
              </View> */}
              <Text style={styles.heroLogoText}>VastuWise</Text>
            </View>
            <Text style={styles.heroGreeting}>Hello, {userName}!</Text>
            <Text style={styles.heroSubtitle}>Your home energy is currently balanced.</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity
              style={styles.actionCard}
              onPress={handleNewAnalysis}
              activeOpacity={0.7}
            >
              <View style={[styles.actionIcon, { backgroundColor: '#FFF5E6' }]}>
                <Camera size={28} color={colors.primary} strokeWidth={2.5} />
              </View>
              <Text style={styles.actionLabel}>New Analysis</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionCard}
              onPress={() => handleNavigation('Learn')}
              activeOpacity={0.7}
            >
              <View style={[styles.actionIcon, { backgroundColor: '#FFF5E6' }]}>
                <BookOpen size={28} color={colors.primary} strokeWidth={2.5} />
              </View>
              <Text style={styles.actionLabel}>Learn Vastu</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Recent Analyses */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Analyses</Text>
            <TouchableOpacity onPress={() => handleNavigation('History')}>
              <Text style={styles.viewAll}>View All</Text>
            </TouchableOpacity>
          </View>

          {recentAnalyses.map((analysis) => (
            <TouchableOpacity
              key={analysis.id}
              style={styles.analysisCard}
              onPress={() => handleRecentAnalysis(analysis)}
              activeOpacity={0.7}
            >
              <View style={styles.analysisImage}>
                <View
                  style={[
                    styles.imagePlaceholder,
                    {
                      backgroundColor: analysis.id === '1' ? '#86EFAC' : '#F59E0B',
                    },
                  ]}
                >
                  {analysis.id === '1' ? (
                    <HomeIcon size={24} color="#059669" strokeWidth={2} />
                  ) : (
                    <User size={24} color="#D97706" strokeWidth={2} />
                  )}
                </View>
              </View>

              <View style={styles.analysisInfo}>
                <Text style={styles.analysisTitle}>{analysis.title}</Text>
                <View style={styles.analysisLocation}>
                  <MapPin size={14} color={colors.textSecondary} strokeWidth={2} />
                  <Text style={styles.analysisLocationText}>{analysis.location}</Text>
                </View>
              </View>

              <View
                style={[
                  styles.scoreBadge,
                  {
                    backgroundColor:
                      analysis.scoreType === 'good'
                        ? '#DCFCE7'
                        : '#FEF3C7',
                  },
                ]}
              >
                <Text
                  style={[
                    styles.scoreBadgeText,
                    {
                      color:
                        analysis.scoreType === 'good'
                          ? '#16A34A'
                          : colors.primary,
                    },
                  ]}
                >
                  {analysis.score} Score
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Daily Vastu Tip */}
        <View style={styles.section}>
          <View style={styles.tipCard}>
            <View style={styles.tipIcon}>
              <Lightbulb size={20} color={colors.primary} strokeWidth={2} />
            </View>
            <View style={styles.tipContent}>
              <Text style={styles.tipTitle}>Daily Vastu Tip</Text>
              <Text style={styles.tipText}>
                Place a small water fountain in the North-East corner of your
                living room to attract prosperity and positive energy flow.
              </Text>
            </View>
          </View>
        </View>

        {/* Spacer for bottom nav */}
        <View style={styles.bottomSpacer} />
      </ScrollView>

      {/* Bottom Navigation */}
      <BottomNav navigation={navigation} activeScreen="Dashboard" />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundLight,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },

  // Top App Bar
  appBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    paddingTop: spacing.md,
    backgroundColor: colors.backgroundLight,
    borderBottomWidth: 0,
  },
  iconButton: {
    padding: spacing.sm,
    borderRadius: borderRadius.full,
  },
  appBarCenter: {
    flex: 1,
    alignItems: 'center',
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  templeIcon: {
    fontSize: 20,
  },
  appBarTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  appBarRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  notificationBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
    borderWidth: 2,
    borderColor: colors.backgroundLight,
  },
  profileAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(219, 119, 6, 0.2)',
  },
  profileInitial: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },

  // Hero Card
  heroCard: {
    marginHorizontal: spacing.lg,
    marginTop: spacing.md,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    overflow: 'hidden',
    backgroundColor: colors.primary,
    elevation: 8,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
  },
  decorBg: {
    position: 'absolute',
    borderRadius: 9999,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  decorBg1: {
    width: 160,
    height: 160,
    top: -80,
    right: -40,
  },
  decorBg2: {
    width: 128,
    height: 128,
    bottom: 0,
    left: 0,
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
  },
  heroContent: {
    zIndex: 10,
  },
  heroLogoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  heroLogoIcon: {
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroLogoText: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    letterSpacing: 0.5,
  },
  heroGreeting: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  heroSubtitle: {
    fontSize: typography.fontSize.sm,
    color: '#FED7AA',
  },

  // Sections
  section: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  viewAll: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
  },

  // Quick Actions
  quickActionsGrid: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  actionCard: {
    flex: 1,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.backgroundLight,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  actionIcon: {
    width: 56,
    height: 56,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  actionLabel: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    textAlign: 'center',
  },

  // Recent Analyses
  analysisCard: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.backgroundLight,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  analysisImage: {
    marginRight: spacing.md,
  },
  imagePlaceholder: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  analysisInfo: {
    flex: 1,
  },
  analysisTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  analysisLocation: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  analysisLocationText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  scoreBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.md,
  },
  scoreBadgeText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold,
  },

  // Vastu Tip
  tipCard: {
    flexDirection: 'row',
    backgroundColor: '#FEF3C7',
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: '#FDE68A',
    alignItems: 'flex-start',
  },
  tipIcon: {
    width: 32,
    height: 32,
    borderRadius: borderRadius.full,
    backgroundColor: 'rgba(219, 119, 6, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
    marginTop: spacing.xs,
  },
  tipContent: {
    flex: 1,
  },
  tipTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
    letterSpacing: 0.5,
    marginBottom: spacing.xs,
  },
  tipText: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    lineHeight: typography.fontSize.base * 1.5,
  },

  // Spacer
  bottomSpacer: {
    height: spacing.xl,
  },
});

export default DashboardScreen;
