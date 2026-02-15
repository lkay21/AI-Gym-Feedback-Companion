import AsyncStorage from '@react-native-async-storage/async-storage';

// Update this to your Flask backend URL
// For iOS Simulator: 'http://localhost:5001'
// For Android Emulator: 'http://10.0.2.2:5001'
// For Physical Device: 'http://YOUR_COMPUTER_IP:5001'
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5001'
  : 'http://10.0.2.2:5001';

// Helper function to make API requests using fetch (React Native compatible)
const apiRequest = async (method, endpoint, data = null) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    const responseData = await response.json();
    
    if (!response.ok) {
      return {
        success: false,
        error: responseData.error || `Request failed with status ${response.status}`,
        status: response.status,
      };
    }

    return {
      success: true,
      data: responseData,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Network request failed',
    };
  }
};

// Auth API functions
export const authAPI = {
  register: async (email, username, password) => {
    const result = await apiRequest('POST', '/auth/register', {
      email,
      username,
      password,
    });
    
    // Store user data on success
    if (result.success && result.data.user) {
      await AsyncStorage.setItem('user', JSON.stringify(result.data.user));
      await AsyncStorage.setItem('username', result.data.user.username);
      await AsyncStorage.setItem('userId', String(result.data.user.id));
    }
    
    return result;
  },

  login: async (username, password) => {
    const result = await apiRequest('POST', '/auth/login', {
      username,
      password,
    });
    
    // Store user data on success
    if (result.success && result.data.user) {
      await AsyncStorage.setItem('user', JSON.stringify(result.data.user));
      await AsyncStorage.setItem('username', result.data.user.username);
      await AsyncStorage.setItem('userId', String(result.data.user.id));
    }
    
    return result;
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
};

// Chat API functions
export const chatAPI = {
  sendMessage: async (message, profile = {}) => {
    return await apiRequest('POST', '/api/chat', {
      message,
      profile,
    });
  },
  generatePlan: async (message, profile = {}, startDate) => {
    return await apiRequest('POST', '/api/chat/plan', {
      message,
      profile,
      startDate,
    });
  },
};

export default { request: apiRequest };
