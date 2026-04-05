import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import { createClient } from '@supabase/supabase-js';

// Update this to your Flask backend URL
// For iOS Simulator: 'http://localhost:5001'
// For Android Emulator: 'http://10.0.2.2:5001'
// For Physical Device: 'http://YOUR_COMPUTER_IP:5001'
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5001'
  : 'http://10.0.2.2:5001';

const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

const supabase = SUPABASE_URL && SUPABASE_ANON_KEY
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : null;

const getCurrentSessionUserId = async (fallbackUserId = null) => {
  if (supabase) {
    try {
      const { data, error } = await supabase.auth.getSession();
      if (!error) {
        const sessionUserId = data?.session?.user?.id;
        if (sessionUserId) return String(sessionUserId);
      }
    } catch {
      // Fall through to the existing app fallback behavior.
    }
  }

  if (fallbackUserId) return String(fallbackUserId);

  const storedUserId = await AsyncStorage.getItem('userId');
  return storedUserId ? String(storedUserId) : null;
};

// Helper function to make API requests using fetch (React Native compatible)
const apiRequest = async (method, endpoint, data = null) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const storedUserId = await AsyncStorage.getItem('userId');
  const headers = { 'Content-Type': 'application/json' };
  if (storedUserId) headers['X-User-Id'] = String(storedUserId);
  const options = {
    method,
    headers,
    credentials: 'include',
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

export default { request: apiRequest };

export const cvAPI = {
  analyzeVideo: async ({ uri, exercise, userId, fileName = "upload.mp4", mimeType = "video/mp4" }) => {
    const resolvedUserId = await getCurrentSessionUserId(userId);
    if (!resolvedUserId) {
      return {
        success: false,
        error: 'No authenticated user found. Please log in again.',
      };
    }

    const formData = new FormData();
    formData.append("exercise", String(exercise || "").trim());
    formData.append("user_id", resolvedUserId);

    if (Platform.OS === "web") {
      const blobResponse = await fetch(uri);
      const blob = await blobResponse.blob();
      formData.append("video", blob, fileName);
    } else {
      formData.append("video", {
        uri,
        name: fileName,
        type: mimeType,
      });
    }

    const cvHeaders = {};
    if (resolvedUserId) cvHeaders["X-User-Id"] = String(resolvedUserId);
    const res = await fetch(`${API_BASE_URL}/api/cv/analyze`, {
      method: "POST",
      headers: cvHeaders,
      body: formData,
      credentials: "include",
      // do NOT set Content-Type manually for multipart in RN
    });

    let data = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }

    if (res.ok) {
      return { success: true, data: data || {} };
    }

    return {
      success: false,
      error: data?.error || `CV analyze failed with status ${res.status}`,
    };
  },
};
