import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { authAPI } from '../services/api';

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [errorMessage, setErrorMessage] = useState('');

  const validateForm = () => {
    const newErrors = {};

    if (!username.trim()) {
      newErrors.username = 'Username is required';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    // Clear previous error messages
    setErrorMessage('');
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrorMessage(''); // Clear any previous errors
    
    try {
      const result = await authAPI.login(username.trim(), password);

      setLoading(false);

      if (result.success) {
        setErrorMessage(''); // Clear errors on success
        Alert.alert('Success', 'Login successful!', [
          {
            text: 'OK',
            onPress: () => navigation.replace('Chat'),
          },
        ]);
      } else {
        // Display user-friendly error messages
        let errorMsg = result.error || 'Sign in failed. Please try again.';
        
        // Make error messages more user-friendly
        if (errorMsg.includes('Invalid') || errorMsg.includes('invalid')) {
          errorMsg = 'Invalid username or password. Please check your credentials and try again.';
        } else if (errorMsg.includes('Email not confirmed')) {
          errorMsg = 'Please confirm your email address before signing in.';
        } else if (errorMsg.includes('Server configuration')) {
          errorMsg = 'Server error. Please try again later or contact support.';
        } else if (errorMsg.includes('Network') || errorMsg.includes('Failed to fetch')) {
          errorMsg = 'Network error. Please check your internet connection and try again.';
        }
        
        setErrorMessage(errorMsg);
      }
    } catch (error) {
      setLoading(false);
      setErrorMessage('An unexpected error occurred. Please try again.');
      console.error('Login error:', error);
    }
  };

  return (
    <LinearGradient
      colors={['#7c3aed', '#6366f1', '#4c1d95']}
      style={styles.container}
    >
      <StatusBar style="light" />
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.content}>
              <Text style={styles.title}>AI Workout Companion</Text>
              
              <View style={styles.signupLinkContainer}>
                <Text style={styles.signupText}>Don't have an account? </Text>
                <TouchableOpacity onPress={() => navigation.navigate('Signup')}>
                  <Text style={styles.signupLink}>Sign up.</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.form}>
                {errorMessage ? (
                  <View style={styles.errorBanner}>
                    <Text style={styles.errorBannerText}>⚠️ {errorMessage}</Text>
                  </View>
                ) : null}
                
                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Username</Text>
                  <TextInput
                    style={[styles.input, errors.username && styles.inputError]}
                    placeholder="Enter your username"
                    placeholderTextColor="#9ca3af"
                    value={username}
                    onChangeText={(text) => {
                      setUsername(text);
                      if (errors.username) {
                        setErrors({ ...errors, username: null });
                      }
                      if (errorMessage) {
                        setErrorMessage(''); // Clear error when user starts typing
                      }
                    }}
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                  {errors.username && (
                    <Text style={styles.errorText}>{errors.username}</Text>
                  )}
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Password</Text>
                  <View style={styles.passwordContainer}>
                    <TextInput
                      style={[
                        styles.input,
                        styles.passwordInput,
                        errors.password && styles.inputError
                      ]}
                      placeholder="Enter your password"
                      placeholderTextColor="#9ca3af"
                      value={password}
                      onChangeText={(text) => {
                        setPassword(text);
                        if (errors.password) {
                          setErrors({ ...errors, password: null });
                        }
                        if (errorMessage) {
                          setErrorMessage(''); // Clear error when user starts typing
                        }
                      }}
                      secureTextEntry={!showPassword}
                      autoCapitalize="none"
                      autoCorrect={false}
                    />
                    <TouchableOpacity
                      style={styles.eyeIcon}
                      onPress={() => setShowPassword(!showPassword)}
                    >
                      <Text style={styles.eyeIconText}>
                        {showPassword ? '👁️' : '👁️‍🗨️'}
                      </Text>
                    </TouchableOpacity>
                  </View>
                  {errors.password && (
                    <Text style={styles.errorText}>{errors.password}</Text>
                  )}
                </View>

                <TouchableOpacity
                  style={[styles.signInButton, loading && styles.buttonDisabled]}
                  onPress={handleLogin}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color="#ffffff" />
                  ) : (
                    <Text style={styles.signInButtonText}>SIGN IN</Text>
                  )}
                </TouchableOpacity>

                <View style={styles.divider}>
                  <View style={styles.dividerLine} />
                  <Text style={styles.dividerText}>- OR -</Text>
                  <View style={styles.dividerLine} />
                </View>

                <TouchableOpacity
                  style={styles.googleButton}
                  onPress={() => Alert.alert('Coming Soon', 'Google login will be available soon')}
                >
                  <View style={styles.googleButtonContent}>
                    <View style={styles.googleLogo}>
                      <Text style={styles.googleLogoText}>G</Text>
                    </View>
                    <Text style={styles.googleButtonText}>Login with Google</Text>
                  </View>
                </TouchableOpacity>
              </View>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
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
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
  },
  content: {
    paddingHorizontal: 28,
    paddingVertical: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: '800',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 32,
    letterSpacing: -0.5,
  },
  signupLinkContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 48,
  },
  signupText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  signupLink: {
    fontSize: 14,
    color: '#ffffff',
    textDecorationLine: 'underline',
    fontWeight: '600',
  },
  form: {
    width: '100%',
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#1f2937',
    borderWidth: 1,
    borderColor: '#93c5fd',
    height: 52,
  },
  inputError: {
    borderColor: '#ef4444',
    borderWidth: 2,
  },
  passwordContainer: {
    position: 'relative',
  },
  passwordInput: {
    paddingRight: 50,
  },
  eyeIcon: {
    position: 'absolute',
    right: 16,
    top: 16,
  },
  eyeIconText: {
    fontSize: 20,
  },
  errorText: {
    color: '#fca5a5',
    fontSize: 12,
    marginTop: 6,
  },
  errorBanner: {
    backgroundColor: '#fee2e2',
    borderColor: '#ef4444',
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 20,
  },
  errorBannerText: {
    color: '#dc2626',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  signInButton: {
    backgroundColor: '#4c1d95',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    marginBottom: 24,
    height: 52,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  signInButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 1,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  dividerText: {
    color: '#ffffff',
    fontSize: 14,
    marginHorizontal: 16,
    fontWeight: '500',
  },
  googleButton: {
    backgroundColor: '#4c1d95',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
    height: 52,
  },
  googleButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  googleLogo: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleLogoText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#4285F4',
  },
  googleButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});
