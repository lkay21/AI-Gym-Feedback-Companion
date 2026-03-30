import React, { useEffect, useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import MenuDropdown from "../components/MenuDropdown";

const PROFILE_STORAGE_KEY = "userProfile";
const AUTH_TOKEN_KEY = "authToken";

const DEFAULT_PROFILE = {
  username: "",
  email: "",
  weight: "",
  height: "",
  fitnessGoals: "",
};

export default function UserProfileScreen({ navigation }) {
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const raw = await AsyncStorage.getItem(PROFILE_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        setProfile({
          ...DEFAULT_PROFILE,
          ...parsed,
        });
      }
    } catch (err) {
      console.log("Failed to load profile:", err);
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field, value) => {
    setProfile((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await AsyncStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
      Alert.alert("Saved", "Your profile has been updated.");
    } catch (err) {
      console.log("Failed to save profile:", err);
      Alert.alert("Error", "Could not save your profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      setLoggingOut(true);

      await AsyncStorage.multiRemove([AUTH_TOKEN_KEY]);

      navigation.reset({
        index: 0,
        routes: [{ name: "Login" }],
      });
    } catch (err) {
      console.log("Logout failed:", err);
      Alert.alert("Error", "Could not log out.");
    } finally {
      setLoggingOut(false);
    }
  };

  return (
    <LinearGradient
      colors={["#4C76D6", "#8E5AAE"]}
      start={{ x: 0.15, y: 0.1 }}
      end={{ x: 0.85, y: 0.95 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          style={styles.safeArea}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          <View style={styles.cardShell}>
            <ScrollView
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
              keyboardShouldPersistTaps="handled"
            >
              <View style={styles.topBar}>
                <MenuDropdown />
              </View>

              <Text style={styles.title}>User Profile</Text>
              <Text style={styles.subtitle}>
                Manage your account and fitness information
              </Text>

              <View style={styles.avatarWrap}>
                <View style={styles.avatarCircle}>
                  <Ionicons name="person-outline" size={42} color="#fff" />
                </View>
              </View>

              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>Account Information</Text>

                <Text style={styles.label}>Username</Text>
                <TextInput
                  value={profile.username}
                  onChangeText={(text) => updateField("username", text)}
                  placeholder="Enter username"
                  placeholderTextColor="rgba(255,255,255,0.45)"
                  style={styles.input}
                  editable={!loading}
                />

                <Text style={styles.label}>Email</Text>
                <TextInput
                  value={profile.email}
                  onChangeText={(text) => updateField("email", text)}
                  placeholder="Enter email"
                  placeholderTextColor="rgba(255,255,255,0.45)"
                  style={styles.input}
                  autoCapitalize="none"
                  keyboardType="email-address"
                  editable={!loading}
                />
              </View>

              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>Fitness Information</Text>

                <Text style={styles.label}>Weight</Text>
                <TextInput
                  value={profile.weight}
                  onChangeText={(text) => updateField("weight", text)}
                  placeholder="e.g. 180 lbs"
                  placeholderTextColor="rgba(255,255,255,0.45)"
                  style={styles.input}
                  editable={!loading}
                />

                <Text style={styles.label}>Height</Text>
                <TextInput
                  value={profile.height}
                  onChangeText={(text) => updateField("height", text)}
                  placeholder={`e.g. 5'11"`}
                  placeholderTextColor="rgba(255,255,255,0.45)"
                  style={styles.input}
                  editable={!loading}
                />

                <Text style={styles.label}>Fitness Goals</Text>
                <TextInput
                  value={profile.fitnessGoals}
                  onChangeText={(text) => updateField("fitnessGoals", text)}
                  placeholder="Build muscle, lose fat, improve endurance..."
                  placeholderTextColor="rgba(255,255,255,0.45)"
                  style={[styles.input, styles.textArea]}
                  multiline
                  textAlignVertical="top"
                  editable={!loading}
                />
              </View>

              <View style={styles.tipCard}>
                <Ionicons
                  name="sparkles-outline"
                  size={18}
                  color="rgba(255,255,255,0.92)"
                />
                <Text style={styles.tipText}>
                  Your chatbot can update this information automatically when it
                  detects profile details in conversation.
                </Text>
              </View>

              <Pressable
                style={[styles.primaryButton, saving && styles.disabledButton]}
                onPress={handleSave}
                disabled={saving || loading}
              >
                <Text style={styles.primaryButtonText}>
                  {saving ? "Saving..." : "Save Profile"}
                </Text>
              </Pressable>

              <Pressable
                style={styles.secondaryButton}
                onPress={() => navigation.navigate("ChatBot")}
              >
                <Text style={styles.secondaryButtonText}>Go to ChatBot</Text>
              </Pressable>

              <Pressable
                style={[styles.logoutButton, loggingOut && styles.disabledButton]}
                onPress={handleLogout}
                disabled={loggingOut}
              >
                <Text style={styles.logoutButtonText}>
                  {loggingOut ? "Logging Out..." : "Logout"}
                </Text>
              </Pressable>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  cardShell: {
    flex: 1,
    marginHorizontal: 16,
    marginTop: 10,
    marginBottom: 14,
    borderRadius: 28,
    paddingTop: 12,
    paddingHorizontal: 14,
    backgroundColor: "rgba(255,255,255,0.14)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    overflow: "hidden",
  },
  scrollContent: {
    paddingBottom: 28,
  },
  topBar: {
    paddingTop: 6,
    flexDirection: "row",
    justifyContent: "flex-end",
  },
  title: {
    color: "#fff",
    fontSize: 28,
    fontWeight: "800",
    textAlign: "center",
    marginTop: 8,
  },
  subtitle: {
    color: "rgba(255,255,255,0.72)",
    fontSize: 12,
    fontWeight: "700",
    textAlign: "center",
    marginTop: 6,
    marginBottom: 14,
  },
  avatarWrap: {
    alignItems: "center",
    marginBottom: 14,
  },
  avatarCircle: {
    width: 82,
    height: 82,
    borderRadius: 41,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.16)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.22)",
  },
  sectionCard: {
    borderRadius: 16,
    padding: 14,
    backgroundColor: "rgba(255,255,255,0.14)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    marginBottom: 14,
  },
  sectionTitle: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "900",
    textAlign: "center",
    marginBottom: 12,
  },
  label: {
    color: "rgba(255,255,255,0.86)",
    fontSize: 12,
    fontWeight: "800",
    marginBottom: 6,
    marginTop: 8,
  },
  input: {
    minHeight: 48,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: "#fff",
    backgroundColor: "rgba(255,255,255,0.08)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
    fontSize: 13,
    fontWeight: "700",
  },
  textArea: {
    minHeight: 110,
  },
  tipCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    borderRadius: 16,
    padding: 14,
    backgroundColor: "rgba(0,0,0,0.18)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
    marginBottom: 14,
  },
  tipText: {
    flex: 1,
    color: "rgba(255,255,255,0.9)",
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
  },
  primaryButton: {
    height: 48,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.92)",
    marginBottom: 12,
  },
  primaryButtonText: {
    color: "#3C3C3C",
    fontSize: 13,
    fontWeight: "900",
  },
  secondaryButton: {
    height: 48,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.26)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
    marginBottom: 12,
  },
  secondaryButtonText: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 13,
    fontWeight: "900",
  },
  logoutButton: {
    height: 48,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ffffff",
  },
  logoutButtonText: {
    color: "#7c3aed",
    fontSize: 13,
    fontWeight: "900",
  },
  disabledButton: {
    opacity: 0.6,
  },
});