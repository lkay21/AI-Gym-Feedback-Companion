import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';

export default function ChatScreen({ navigation }) {
  const [username, setUsername] = useState('');

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    const storedUsername = await AsyncStorage.getItem('username');
    if (storedUsername) {
      setUsername(storedUsername);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigation.replace('Login');
  };

  return (
    <LinearGradient
      colors={['#7c3aed', '#6366f1', '#4c1d95']}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.content}>
          <Text style={styles.title}>Welcome{username ? `, ${username}` : ''}!</Text>
          <Text style={styles.subtitle}>Chat functionality coming soon</Text>

          <TouchableOpacity
            style={styles.planButton}
            onPress={() => navigation.navigate('Plan')}
          >
            <Text style={styles.planButtonText}>View Fitness Plan</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
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
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 40,
    textAlign: 'center',
  },
  planButton: {
    backgroundColor: '#facc15',
    borderRadius: 12,
    padding: 16,
    paddingHorizontal: 32,
    marginBottom: 16,
  },
  planButtonText: {
    color: '#1e1b4b',
    fontSize: 16,
    fontWeight: '700',
  },
  logoutButton: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    paddingHorizontal: 32,
  },
  logoutButtonText: {
    color: '#7c3aed',
    fontSize: 16,
    fontWeight: '700',
  },
});
