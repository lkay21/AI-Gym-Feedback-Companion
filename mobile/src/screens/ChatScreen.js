import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';

export default function ChatScreen({ navigation }) {
  const handleLogout = async () => {
    await authAPI.logout();
    navigation.replace('Login');
  };

  return (
    <LinearGradient
      colors={['#7c3aed', '#6366f1', '#3b82f6']}
      style={styles.container}
    >
      <View style={styles.content}>
        <Text style={styles.title}>Chat Screen</Text>
        <Text style={styles.subtitle}>Welcome to the chat!</Text>
        
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 28,
  },
  title: {
    fontSize: 32,
    fontWeight: '800',
    color: '#ffffff',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 40,
  },
  logoutButton: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    paddingHorizontal: 32,
  },
  logoutButtonText: {
    color: '#7c3aed',
    fontSize: 16,
    fontWeight: '700',
  },
});


