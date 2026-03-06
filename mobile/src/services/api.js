import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// Update this to your Flask backend URL
// For iOS Simulator: 'http://localhost:5001'
// For Android Emulator: 'http://10.0.2.2:5001'
// For Physical Device: 'http://YOUR_COMPUTER_IP:5001'
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL ||
  (__DEV__
    ? Platform.OS === 'android'
      ? 'http://10.0.2.2:5001'
      : 'http://localhost:5001'
    : 'http://10.0.2.2:5001');

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
  // Gemini-powered chatbot endpoint used by the mobile ChatBot screen
  sendChatbotMessage: async (message, conversationHistory = [], profile = {}) => {
    return await apiRequest('POST', '/api/chat/llm', {
      message,
      conversation_history: conversationHistory,
      profile,
    });
  },
  // Generate 2-week fitness plan from database (uses authenticated user's health profile)
  generatePlan: async () => {
    return await apiRequest('POST', '/api/chat/plan', {});
  },
};

// CV upload/analysis API functions
export const cvAPI = {
  analyzeVideo: async ({ uri, exercise, userId, asset = null }) => {
    if (!uri) {
      return { success: false, error: 'Video URI is required' };
    }
    if (!exercise) {
      return { success: false, error: 'Exercise is required' };
    }

    const endpoint = '/api/exercises/upload_video';
    const url = `${API_BASE_URL}${endpoint}`;

    const extension = uri.split('.').pop()?.toLowerCase() || 'mp4';
    const mimeType = extension === 'mov' ? 'video/quicktime' : `video/${extension}`;
    const fileName = asset?.fileName || asset?.name || `upload.${extension}`;

    const formData = new FormData();
    if (Platform.OS === 'web') {
      // Web expects a File/Blob in multipart form data.
      if (asset?.file instanceof File) {
        formData.append('video', asset.file, fileName);
      } else {
        const blobResponse = await fetch(uri);
        const blob = await blobResponse.blob();
        formData.append('video', blob, fileName);
      }
    } else {
      // Native expects the { uri, name, type } form.
      formData.append('video', {
        uri,
        name: fileName,
        type: asset?.mimeType || mimeType,
      });
    }
    formData.append('exercise', exercise);
    if (userId) {
      formData.append('user_id', String(userId));
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      const rawResponseText = await response.text();
      let responseData = null;
      try {
        responseData = rawResponseText ? JSON.parse(rawResponseText) : null;
      } catch {
        responseData = null;
      }

      if (!response.ok) {
        return {
          success: false,
          error:
            responseData?.error ||
            rawResponseText ||
            `Upload failed with status ${response.status}`,
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
        error: error.message || 'Video upload failed',
      };
    }
  },
};

export default { request: apiRequest };
