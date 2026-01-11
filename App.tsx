/**
 * VastuWise AI - Main App Component
 * React Native Application Entry Point
 * 
 * @format
 */

import React, { useState } from 'react';
import { StatusBar, StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Import Screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import LoginScreen from './src/screens/LoginScreen';

function App() {
  // Toggle between screens for demo purposes
  // Set to 'welcome' or 'login' to see different screens
  const [currentScreen, setCurrentScreen] = useState<'welcome' | 'login'>('login');

  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" backgroundColor="#fffaf5" />
      <View style={styles.container}>
        {currentScreen === 'welcome' ? <WelcomeScreen /> : <LoginScreen />}
      </View>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App;
