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

export default function SignupScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [errorMessage, setErrorMessage] = useState('');

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = () => {
    const newErrors = {};

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!username.trim()) {
      newErrors.username = 'Username is required';
    } else if (username.trim().length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(username.trim())) {
      newErrors.username = 'Username can only contain letters, numbers, underscores, and hyphens';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignup = async () => {
    // Clear previous error messages
    setErrorMessage('');
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrorMessage(''); // Clear any previous errors
    
    try {
      const result = await authAPI.register(
        email.trim().toLowerCase(),
        username.trim(),
        password
      );

      setLoading(false);

      if (result.success) {
        setErrorMessage(''); // Clear errors on success
        Alert.alert('Success', 'Account created successfully!', [
          {
            text: 'OK',
            onPress: () => navigation.replace('Chat'),
          },
        ]);
      } else {
        // Display user-friendly error messages
        let errorMsg = result.error || 'Sign up failed. Please try again.';
        
        // Make error messages more user-friendly
        if (errorMsg.includes('already registered') || errorMsg.includes('already taken')) {
          if (errorMsg.includes('Email')) {
            errorMsg = 'This email is already registered. Please use a different email or sign in.';
          } else if (errorMsg.includes('Username')) {
            errorMsg = 'This username is already taken. Please choose a different username.';
          } else {
            errorMsg = 'This account already exists. Please sign in instead.';
          }
        } else if (errorMsg.includes('Invalid email')) {
          errorMsg = 'Please enter a valid email address.';
        } else if (errorMsg.includes('Password')) {
          errorMsg = 'Password does not meet requirements. Please use a stronger password.';
        } else if (errorMsg.includes('Username')) {
          errorMsg = 'Username does not meet requirements. Please use 3+ characters with only letters, numbers, underscores, and hyphens.';
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
      console.error('Signup error:', error);
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
              
              <View style={styles.loginLinkContainer}>
                <Text style={styles.loginText}>Already have an account? </Text>
                <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                  <Text style={styles.loginLink}>Sign in.</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.form}>
                {errorMessage ? (
                  <View style={styles.errorBanner}>
                    <Text style={styles.errorBannerText}>⚠️ {errorMessage}</Text>
                  </View>
                ) : null}
                
                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Email</Text>
                  <TextInput
                    style={[styles.input, errors.email && styles.inputError]}
                    placeholder="Enter your email"
                    placeholderTextColor="#9ca3af"
                    value={email}
                    onChangeText={(text) => {
                      setEmail(text);
                      if (errors.email) {
                        setErrors({ ...errors, email: null });
                      }
                      if (errorMessage) {
                        setErrorMessage(''); // Clear error when user starts typing
                      }
                    }}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                  {errors.email && (
                    <Text style={styles.errorText}>{errors.email}</Text>
                  )}
                </View>

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

                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Confirm Password</Text>
                  <View style={styles.passwordContainer}>
                    <TextInput
                      style={[
                        styles.input,
                        styles.passwordInput,
                        errors.confirmPassword && styles.inputError
                      ]}
                      placeholder="Confirm your password"
                      placeholderTextColor="#9ca3af"
                      value={confirmPassword}
                      onChangeText={(text) => {
                        setConfirmPassword(text);
                        if (errors.confirmPassword) {
                          setErrors({ ...errors, confirmPassword: null });
                        }
                        if (errorMessage) {
                          setErrorMessage(''); // Clear error when user starts typing
                        }
                      }}
                      secureTextEntry={!showConfirmPassword}
                      autoCapitalize="none"
                      autoCorrect={false}
                    />
                    <TouchableOpacity
                      style={styles.eyeIcon}
                      onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      <Text style={styles.eyeIconText}>
                        {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
                      </Text>
                    </TouchableOpacity>
                  </View>
                  {errors.confirmPassword && (
                    <Text style={styles.errorText}>{errors.confirmPassword}</Text>
                  )}
                </View>

                <TouchableOpacity
                  style={[styles.signUpButton, loading && styles.buttonDisabled]}
                  onPress={handleSignup}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color="#ffffff" />
                  ) : (
                    <Text style={styles.signUpButtonText}>SIGN UP</Text>
                  )}
                </TouchableOpacity>

                <View style={styles.divider}>
                  <View style={styles.dividerLine} />
                  <Text style={styles.dividerText}>- OR -</Text>
                  <View style={styles.dividerLine} />
                </View>

                <TouchableOpacity
                  style={styles.googleButton}
                  onPress={() => Alert.alert('Coming Soon', 'Google signup will be available soon')}
                >
                  <View style={styles.googleButtonContent}>
                    <View style={styles.googleLogo}>
                      <Text style={styles.googleLogoText}>G</Text>
                    </View>
                    <Text style={styles.googleButtonText}>Sign up with Google</Text>
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
  loginLinkContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 48,
  },
  loginText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  loginLink: {
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
  signUpButton: {
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
  signUpButtonText: {
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
