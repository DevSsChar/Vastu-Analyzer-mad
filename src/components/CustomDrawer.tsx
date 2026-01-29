/**
 * Custom Drawer Component
 * Features: User profile, logout, menu items
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  Modal,
  Animated,
  Dimensions,
} from 'react-native';
import { Home, BarChart, User, BookOpen, Settings, LogOut, Clock } from 'lucide-react-native';
import { colors, typography, spacing, borderRadius } from '../theme';
import { getToken, getUserData, clearStorage } from '../services/storage.service';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface CustomDrawerProps {
  visible: boolean;
  onClose: () => void;
  navigation: any;
}

const CustomDrawer: React.FC<CustomDrawerProps> = ({ visible, onClose, navigation }) => {
  const [userData, setUserData] = useState<any>(null);
  const slideAnim = useState(new Animated.Value(-SCREEN_WIDTH * 0.8))[0];
  const backdropOpacity = useState(new Animated.Value(0))[0];

  useEffect(() => {
    loadUserData();
  }, []);

  useEffect(() => {
    if (visible) {
      console.log('Opening drawer');
      Animated.parallel([
        Animated.spring(slideAnim, {
          toValue: 0,
          tension: 65,
          friction: 11,
          useNativeDriver: true,
        }),
        Animated.timing(backdropOpacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: -SCREEN_WIDTH * 0.8,
          duration: 250,
          useNativeDriver: true,
        }),
        Animated.timing(backdropOpacity, {
          toValue: 0,
          duration: 250,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [visible, slideAnim, backdropOpacity]);

  const loadUserData = async () => {
    const user = await getUserData();
    setUserData(user);
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              // Clear all session data
              await clearStorage();
              console.log('Session data cleared');
              
              // Close drawer
              onClose();
              
              // Navigate to Login and reset navigation stack
              navigation.reset({
                index: 0,
                routes: [{ name: 'Login' }],
              });
            } catch (error) {
              console.error('Logout error:', error);
              Alert.alert('Error', 'Failed to logout. Please try again.');
            }
          },
        },
      ]
    );
  };

  const navigateTo = (screen: string) => {
    onClose();
    if (screen === 'Learn' || screen === 'Settings') {
      Alert.alert('Coming Soon', `${screen} feature will be available soon!`);
    } else {
      navigation.navigate(screen);
    }
  };

  const menuItems = [
    { id: 1, icon: Home, label: 'Home', screen: 'Welcome' },
    { id: 2, icon: BarChart, label: 'Dashboard', screen: 'Dashboard' },
    { id: 3, icon: Clock, label: 'History', screen: 'History' },
    { id: 4, icon: User, label: 'Profile', screen: 'Profile' },
    { id: 5, icon: BookOpen, label: 'Learn Vastu', screen: 'Learn' },
    { id: 6, icon: Settings, label: 'Settings', screen: 'Settings' },
  ];

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="none"
      onRequestClose={onClose}
    >
      <View style={styles.modalContainer}>
        <Animated.View
          style={[styles.overlay, { opacity: backdropOpacity }]}
        >
          <TouchableOpacity
            style={styles.overlayTouchable}
            activeOpacity={1}
            onPress={onClose}
          />
        </Animated.View>
        <Animated.View
          style={[
            styles.drawerContainer,
            { transform: [{ translateX: slideAnim }] },
          ]}
        >
          <ScrollView style={styles.container}>
            <View style={styles.drawerContent}>
        {/* User Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarText}>
              {userData?.name ? userData.name.charAt(0).toUpperCase() : '👤'}
            </Text>
          </View>
          <Text style={styles.userName}>{userData?.name || 'Guest User'}</Text>
          <Text style={styles.userEmail}>{userData?.email || 'guest@example.com'}</Text>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Menu Items */}
        <View style={styles.menuSection}>
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <TouchableOpacity
                key={item.id}
                style={styles.menuItem}
                onPress={() => navigateTo(item.screen)}
                activeOpacity={0.7}
              >
                <View style={styles.menuIcon}>
                  <IconComponent size={22} color={colors.textPrimary} strokeWidth={2} />
                </View>
                <Text style={styles.menuLabel}>{item.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Logout Button */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
          activeOpacity={0.7}
        >
          <View style={styles.logoutIcon}>
            <LogOut size={22} color={colors.error} strokeWidth={2} />
          </View>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>

        {/* App Version */}
        <Text style={styles.versionText}>VastuWise AI v1.0.0</Text>
      </View>
    </ScrollView>
        </Animated.View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    flexDirection: 'row',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  overlayTouchable: {
    flex: 1,
  },
  drawerContainer: {
    width: SCREEN_WIDTH * 0.8,
    maxWidth: 320,
    backgroundColor: colors.backgroundLight,
    shadowColor: colors.blackOpacity(0.3),
    shadowOffset: { width: 2, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 16,
  },
  container: {
    flex: 1,
    backgroundColor: colors.backgroundLight,
  },
  drawerContent: {
    flex: 1,
    paddingVertical: spacing.lg,
  },
  
  // Profile Section
  profileSection: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  avatarText: {
    fontSize: 36,
    fontWeight: typography.fontWeight.bold,
    color: colors.textLight,
  },
  userName: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  userEmail: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },

  // Divider
  divider: {
    height: 1,
    backgroundColor: colors.gray300,
    marginVertical: spacing.md,
    marginHorizontal: spacing.lg,
  },

  // Menu Section
  menuSection: {
    paddingHorizontal: spacing.sm,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.md,
    marginBottom: spacing.xs,
  },
  menuIcon: {
    marginRight: spacing.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuLabel: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
  },

  // Logout Button
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    marginHorizontal: spacing.sm,
    borderRadius: borderRadius.md,
    backgroundColor: colors.errorOpacity(0.1),
    marginTop: spacing.md,
  },
  logoutIcon: {
    marginRight: spacing.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoutText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    color: colors.error,
  },

  // Version
  versionText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xl,
    paddingBottom: spacing.lg,
  },
});

export default CustomDrawer;
