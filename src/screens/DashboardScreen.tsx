/**
 * VastuWise AI - Example Dashboard Screen
 * Demonstrates usage of all reusable components
 * This is a template screen showing best practices
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  StatusBar,
} from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import { CustomButton, CustomTextInput, CustomCard } from '../components';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.backgroundLight} />
      
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome back! 👋</Text>
          <Text style={styles.title}>Dashboard</Text>
        </View>

        {/* Search Input Example */}
        <View style={styles.section}>
          <CustomTextInput
            placeholder="Search analysis..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            icon="🔍"
            containerStyle={styles.searchInput}
          />
        </View>

        {/* Stats Cards Grid */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Stats</Text>
          <View style={styles.statsGrid}>
            <CustomCard
              icon="📊"
              title="Total Scans"
              description="24 completed"
              variant="solid"
              style={styles.statCard}
            />
            <CustomCard
              icon="⭐"
              title="Avg Score"
              description="85/100"
              variant="solid"
              style={styles.statCard}
            />
            <CustomCard
              icon="🏠"
              title="Properties"
              description="3 active"
              variant="solid"
              style={styles.statCard}
            />
            <CustomCard
              icon="✅"
              title="Remedies"
              description="12 applied"
              variant="solid"
              style={styles.statCard}
            />
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          
          <CustomButton
            title="Start New Analysis"
            icon="🔍"
            variant="primary"
            onPress={() => console.log('Start Analysis')}
            style={styles.actionButton}
          />
          
          <CustomButton
            title="View Reports"
            icon="📄"
            variant="outline"
            onPress={() => console.log('View Reports')}
            style={styles.actionButton}
          />
          
          <CustomButton
            title="Settings"
            icon="⚙️"
            variant="secondary"
            onPress={() => console.log('Settings')}
            style={styles.actionButton}
          />
        </View>

        {/* Feature Cards */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Features</Text>
          <View style={styles.featuresGrid}>
            <CustomCard
              icon="🧭"
              title="Direction"
              description="Check alignment"
              variant="glass"
              onPress={() => console.log('Direction')}
              style={styles.featureCard}
            />
            <CustomCard
              icon="🌡️"
              title="Heat Map"
              description="View energy flow"
              variant="glass"
              onPress={() => console.log('Heat Map')}
              style={styles.featureCard}
            />
          </View>
        </View>

        {/* Loading Button Example */}
        <View style={styles.section}>
          <CustomButton
            title="Loading Example"
            variant="primary"
            loading={true}
            onPress={() => {}}
          />
        </View>

        {/* Disabled Button Example */}
        <View style={styles.section}>
          <CustomButton
            title="Disabled Example"
            variant="primary"
            disabled={true}
            onPress={() => {}}
          />
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
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  
  // Header
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.md,
  },
  greeting: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
  },
  
  // Sections
  section: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  
  // Search
  searchInput: {
    marginBottom: 0,
  },
  
  // Stats Grid
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  statCard: {
    width: (SCREEN_WIDTH - spacing.lg * 2 - spacing.md) / 2,
  },
  
  // Features Grid
  featuresGrid: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  featureCard: {
    flex: 1,
  },
  
  // Action Buttons
  actionButton: {
    marginBottom: spacing.md,
  },
});

export default DashboardScreen;
