import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Update this to your Flask backend URL
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5001'  // For iOS simulator
  : 'http://10.0.2.2:5001';   // For Android emulator
  // For physical device, use your computer's IP: 'http://192.168.1.X:5001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API functions
export const authAPI = {
  register: async (email, username, password) => {
    try {
      const response = await api.post('/auth/register', {
        email,
        username,
        password,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed. Please try again.',
      };
    }
  },

  login: async (username, password, email = null) => {
    try {
      const response = await api.post('/auth/login', {
        username,
        password,
        email,
      });
      
      // Store user data
      if (response.data.user) {
        await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
        await AsyncStorage.setItem('username', response.data.user.username);
        await AsyncStorage.setItem('userId', String(response.data.user.id));
      }
      
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed. Please try again.',
      };
    }
  },

  logout: async () => {
    try {
      await AsyncStorage.removeItem('user');
      await AsyncStorage.removeItem('username');
      await AsyncStorage.removeItem('userId');
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Logout failed' };
    }
  },

  checkSession: async () => {
    try {
      const response = await api.get('/auth/check');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false };
    }
  },
};

// Chat API functions
export const chatAPI = {
  sendMessage: async (message, profile = {}) => {
    try {
      const response = await api.post('/api/chat', {
        message,
        profile,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to send message',
      };
    }
  },
};

export default api;

